FROM python:3.10-slim

# Установка Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Установка зависимостей
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Запуск сервера
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5050"]
