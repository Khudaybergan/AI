FROM python:3.10-slim

# Установка Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean

# Установка зависимостей Python
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Запуск
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
