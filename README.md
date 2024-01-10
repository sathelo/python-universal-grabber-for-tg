# Universal grabber for tg

Full automation of posting posts from tg to VK and Instagram. This script collects old posts from tg and posts them at a given time to social networks such as VK and Instagram

# Use

- ✍️ Переименуйте `settings.example.json` на `settings.json` и заполните его необходимым
- ✍️ Переименуйте `database.example.db` на `database.db`
- 🛠 Создайте виртуальное окружение `python -m venv env` и активируйте его
- ⏳ Установите зависимости `pip install -r requirements.txt`
- 🚀 Запустите скрипт `python main.py`
- 😋 Наслаждайтесь

**ОБЯЗАТЕЛЬНО** Для работы скрипта создается сессия, при запуске скрипта необходимо будет для сессии ОДИН РАЗ предоставить доступ с телеграмм аккаунта (сообщение в виде кода подтверждения приходит от официального бота telegram). Скрипт может завершиться с ошибкой и необходимо будет его перезапустить

```python
# Установка расписания
schedule.every().day.at("09:00").do(job, session_name="session")
schedule.every().day.at("12:00").do(job, session_name="session")
schedule.every().day.at("15:00").do(job, session_name="session")
schedule.every().day.at("19:00").do(job, session_name="session")
schedule.every().day.at("21:00").do(job, session_name="session")
```

# Help

**settings.json**

| Поле                    | Описание                                                                      | Например                                                              |
| ----------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| phone                   | номер телефона от вк аккаунта                                                 | 71231231212                                                           |
| api_id                  | [подробнее про api_id](https://tlgrm.ru/docs/api/obtaining_api_id)            | 18723721                                                              |
| api_hash                | [подробнее про api_hash](https://tlgrm.ru/docs/api/obtaining_api_id)          | 1td913f19387d18w276df1927d123                                         |
| channel_username        | полное имя телеграмм сообщества                                               | ТгСообщество                                                          |
| channel_id              | id сообщества тг                                                              | -198237129836                                                         |
| vk_token                | [подробнее про vk_token (нас интересует VK Admin)](https://vkhost.github.io/) | vk1.123123k123123123123k123123123123k123123123123k123123123123k123123 |
| vk_group_id             | id сообщества вк                                                              | -128735612835                                                         |
| source_url              | ссылка добавляется в источник к вк посту                                      | https://www.google.com/                                               |
| inst_username           | логин в виде юзернейма (полное имя инстаграм сообщества)                      | username                                                              |
| inst_password           | пароль от инстаграм аккаунта                                                  | password                                                              |
| inst_caption            | комментарий под инстаграм постом (можно писать с хэштегами)                   | Test caption for photo with #hashtags                                 |
| watermark_text_for_vk   | водяной знак (текстовый) для вк поста                                         | example watermark text for vk                                         |
| watermark_text_for_inst | водяной знак (текстовый) для инстаграм поста                                  | example watermark text for inst                                       |
