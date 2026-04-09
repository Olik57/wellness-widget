import os
from flask import Flask, jsonify
import httpx
from openai import OpenAI

app = Flask(__name__)

# Čtení nastavení z proměnných prostředí
client = OpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
    base_url= os.getenv("OPENAI_BASE_URL"),
    http_client=httpx.Client(verify=False)  # Školní server má self-signed certifikát
)

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "model": "gemma3:27b"})

@app.route('/ai', methods=['POST'])
def ai_tip():
    try:
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {
                    "role": "user",
                    "content": "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."
                }
            ],
            max_tokens=100
        )
        tip = response.choices[0].message.content.strip()
        return jsonify({"tip": tip})
    except Exception as e:
        return jsonify({"tip": "Nezapomeň se protáhnout!"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8081))  # Port z proměnné prostředí
    )
