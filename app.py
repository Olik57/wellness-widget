import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "model": "gemma3:27b"})

@app.route('/ai', methods=['POST'])
def ai_tip():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    payload = {
        "model": "gemma3:27b",
        "messages": [
            {"role": "user", "content": "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."}
        ],
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        result = response.json()
        tip = result['choices'][0]['message']['content']
        return jsonify({"tip": tip})
    except Exception as e:
        return jsonify({"tip": "Nezapomeň se protáhnout!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
