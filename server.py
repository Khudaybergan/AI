from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import pytesseract
from PIL import Image
from io import BytesIO
import os

# === Загрузка переменных из .env ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Инициализация Flask ===
app = Flask(__name__)
CORS(app)

# Хранилище последнего ответа
last_answer = ""

@app.route('/', methods=['GET'])
def home():
    return "✅ AI сервер работает!"

@app.route('/upload', methods=['POST'])
def upload_image():
    global last_answer
    try:
        # Получаем изображение
        image_file = request.files['image']
        image = Image.open(image_file.stream)

        # OCR
        text = pytesseract.image_to_string(image)
        print("📃 Распознанный текст:\n", text)

        # Создаём промпт для AI
        prompt = (
           "Привет, вот тестовое задание, которое я сейчас прохожу во время сессии. "
           "Пожалуйста, помоги мне. В тексте может быть несколько вопросов, но мне нужен ответ "
           "только на **последний вопрос с вариантами ответа** (A, B, C или D). "
           "Укажи, какой это по счёту вопрос (например, Q3: C»), и ответь **только одной буквой**, без пояснений. "
           "Вот сам текст задания:\n\n"
           f"{text}"
        )       

        # Отправка в OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        print("🤖 Ответ от AI:", answer)

        # Сохраняем ответ для повторного открытия popup
        last_answer = answer

        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ Ошибка:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/last', methods=['GET'])
def get_last_answer():
    return jsonify({"answer": last_answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
