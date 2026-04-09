import os
import json
import urllib.request
import ssl
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("OPENAI_BASE_URL")

# Hlavní stránka — otevře index.html
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "model": "gemma3:27b"})

@app.route('/ai', methods=['POST'])
def ai_tip():
    try:
        ctx = ssl._create_unverified_context()
        data = json.dumps({
            "model": "gemma3:27b",
            "messages": [{"role": "user", "content": "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."}],
            "max_tokens": 100
        }).encode()
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        resp = json.loads(urllib.request.urlopen(req, context=ctx).read())
        tip = resp["choices"][0]["message"]["content"].strip()
        return jsonify({"tip": tip})
    except Exception as e:
        return jsonify({"tip": "Nezapomeň se protáhnout!"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8081))
    )
