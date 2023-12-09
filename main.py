import os
import asyncio
import json
import vk_api
import sqlite3
import schedule
import time
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from instagrapi import Client
from PIL import Image


# Загрузка настроек из файла JSON
with open('settings.json') as f:
    settings = json.load(f)

phone = settings['phone']
api_id = settings['api_id']
api_hash = settings['api_hash']
channel_username = settings['channel_username']
channel_id = settings['channel_id']
vk_token = settings['vk_token']
vk_group_id = settings['vk_group_id']
source_url = settings['source_url']
inst_username = settings['inst_username']
inst_password = settings['inst_password']
inst_caption = settings['inst_caption']

# Создание таблицы, если она еще не существует
db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY)
''')
# Закрытие базы данных
cursor.close()
db.close()   

# Конвертирование png-картинки в jpg-картинку
def convert_png_to_jpg(image_path):
    image = Image.open(image_path)
    jpg_path = os.path.splitext(image_path)[0] + ".jpg"
    image.convert("RGB").save(jpg_path, "JPEG")
    return jpg_path

# Скачивание фотографии, по индентификатоиру поста в канале
async def download_photo(client: TelegramClient, message_id: int, channel_id: int):
    message = await client.get_messages(channel_id, ids=message_id)
    if message and message.media:
        path = await client.download_media(message.media)
        if path.lower().endswith(".jpg"):
            return path
        if path.lower().endswith(".png"):
            path = convert_png_to_jpg(path)
            return path
    return None
 
# Асинхронная функция для получения и сохранения поста
async def get_and_save_post(session_name):
    vk_success = False
    inst_success = False

     # Открытие соединения с базой данных
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    async with TelegramClient(session_name, api_id, api_hash) as client: 
        await client.start(phone)
        channel_entity = await client.get_entity(channel_id)
        async for message in client.iter_messages(channel_entity, reverse=True):
            if message.media is not None and isinstance(message.media, MessageMediaPhoto):
                cursor.execute("SELECT * FROM posts WHERE id = ?", (message.id,))
                data = cursor.fetchone()
                if data is None:
                    cursor.execute("INSERT INTO posts (id) VALUES (?)", (message.id,))
                    db.commit()
                    photo_path = await download_photo(client, message.id, channel_id)
                    try:
                        if not vk_success:
                            post_to_vk(photo_path)
                            vk_success = True
                        if not inst_success:
                            post_to_inst(photo_path, inst_caption)
                            inst_success = True
                    except Exception as error:
                        print(error)
                        continue
                    finally: 
                        if (photo_path):
                            # Удаление файла после использования
                            os.remove(photo_path)
                    break # Если пост успешно обработан, выходим из цикла
            else:
                continue  # Если медиафайл отсутствует, продолжаем итерацию

    # Закрытие базы данных после выполнения всех операций
    cursor.close()
    db.close()    

# Функция для публикации поста в сообщество ВКонтакте
def post_to_vk(photo_path):
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo_wall(photo_path)
    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
    
    # Публикация поста
    vk.wall.post(owner_id=vk_group_id, copyright=source_url, attachments=attachment)

# Функция для публикации поста в сообщество Инстаграм
def post_to_inst(photo_path, caption):
    media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), photo_path)

    cl = Client()
    cl.login(inst_username, inst_password)

    media = cl.photo_upload(media_path, caption)
    media.dict()

# Функция для запуска главной функции по расписанию
def job(session_name):
    # Запуск граббера
    asyncio.run(get_and_save_post(session_name))

# Установка расписания
schedule.every().day.at("09:00").do(job, session_name="session")
schedule.every().day.at("12:00").do(job, session_name="session")
schedule.every().day.at("15:00").do(job, session_name="session")
schedule.every().day.at("19:00").do(job, session_name="session")
schedule.every().day.at("21:00").do(job, session_name="session")

# Бесконечный цикл для выполнения задач по расписанию
while True:
    schedule.run_pending()
    time.sleep(1)
