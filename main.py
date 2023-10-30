import os
import asyncio
import json
import vk_api
import sqlite3
import schedule
import time
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto

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

# Скачивание фотографии, по индентификатоиру поста в канале
async def download_photo(client: TelegramClient, message_id: int, channel_id: int):
    message = await client.get_messages(channel_id, ids=message_id)
    if message and message.media:
        path = await client.download_media(message.media)
        return path
    else:
        return None

# Асинхронная функция для получения и сохранения поста
async def get_and_save_post(session_name):
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
                    post_to_vk(photo_path)
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

    # Удаление файла после использования
    os.remove(photo_path)

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
