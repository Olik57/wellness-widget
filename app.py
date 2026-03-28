from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/status')
def status():
    return jsonify({
        "cas": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autor": "Olivier",
        "sluzba": "Wellness Widget"
    })

@app.route('/ai', methods=['POST'])
def ai():
    response = requests.post('http://host.docker.internal:11434/api/generate', json={
        "model": "llama3.2:1b",
        "prompt": "Dej mi jeden krátký wellness tip v češtině (max 1 věta).",
        "stream": False
    })
    tip = response.json()['response']
    return jsonify({"tip": tip})

@app.route('/')
def index():
    return open('index.html').read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
