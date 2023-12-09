# Используем базовый образ Python
FROM python:3

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы из текущего каталога в контейнер
COPY . /app

# Активируем виртуальную среду
RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запускаем скрипт main.py при запуске контейнера
CMD ["python", "main.py"]