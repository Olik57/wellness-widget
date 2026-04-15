import os
import psycopg2
import requests
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    try:
        # Připojení k DB definované v compose.yml
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    except:
        return None

def init_db():
    # Počkáme, až se databáze nastartuje
    time.sleep(5)
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS history (id SERIAL PRIMARY KEY, msg TEXT, reply TEXT);')
        conn.commit()
        cur.close()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    data = request.get_json()
    user_msg = data.get('message', '')
    
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://kurim.ithope.eu/v1/chat/completions"
    
    payload = {
        "model": "gemma3:27b",
        "messages": [{"role": "user", "content": user_msg}]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        ai_reply = response.json()['choices'][0]['message']['content']

        # Zápis do databáze
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO history (msg, reply) VALUES (%s, %s)', (user_msg, ai_reply))
            conn.commit()
            cur.close()
            conn.close()

        # VRACÍME KLÍČ "reply" - důležité pro widget!
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"Chyba na serveru: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8081)
