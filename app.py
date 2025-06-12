from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import pytesseract
from PIL import Image
from io import BytesIO
import os, uuid, threading

# === Загрузка переменных из .env ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Flask ===
app = Flask(__name__)
CORS(app)

# === Хранилище ответов ===
results = {}  # {task_id: {"status": "processing"/"done", "answer": "..." }}

@app.route('/', methods=['GET'])
def home():
    return "✅ AI сервер работает!"

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        task_id = str(uuid.uuid4())
        image_file = request.files['image']
        image_data = image_file.read()

        # Сохраняем задачу
        results[task_id] = {"status": "processing"}

        # Запускаем фоновую обработку
        threading.Thread(target=process_image_task, args=(task_id, image_data)).start()

        return jsonify({"task_id": task_id})

    except Exception as e:
        print("❌ Ошибка:", e)
        return jsonify({"error": str(e)}), 500

def process_image_task(task_id, image_data):
    try:
        image = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        print("📃 Распознанный текст:\n", text)

        prompt = (
            "Hi, I’m currently taking a test and need your help. "
            "Please look at the task below and provide the correct answer. "
            "Only reply with one single letter: A, B, C, or D — without any explanation. "
            "Which question is it (e.g., Q2: B)?\n\n"
            f"{text}"
        )

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        print(f"🤖 Готово [{task_id}]:", answer)

        results[task_id] = {"status": "done", "answer": answer}

    except Exception as e:
        print(f"❌ Ошибка в задаче {task_id}:", e)
        results[task_id] = {"status": "error", "error": str(e)}

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    if task_id not in results:
        return jsonify({"status": "not_found"}), 404

    result = results[task_id]
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Используй PORT, который задаёт Render
    app.run(host='0.0.0.0', port=port)
