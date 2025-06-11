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

# === Инициализация Flask-приложения ===
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "✅ AI сервер работает!"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        # Получаем изображение
        image_file = request.files["image"]
        image = Image.open(image_file.stream)

        # OCR — распознаём текст
        text = pytesseract.image_to_string(image)
        print("📃 Распознанный текст:\n", text)

        # Создаём промпт для AI
        prompt = (
            "Привет, вот тестовое задание, которое я сейчас прохожу во время сессии. "
            "Пожалуйста, помоги мне. В тексте может быть несколько вопросов, но мне нужен ответ "
            "только на последний вопрос с вариантами ответа (A, B, C или D). "
            "Ответь одной буквой и напиши, к какому вопросу она относится. Вот текст:\n\n"
            f"{text}"
        )

        # Обращение к OpenAI
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        print("🤖 Ответ от AI:", answer)

        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ Ошибка:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)))
