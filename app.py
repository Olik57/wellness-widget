import os
import psycopg2
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Připojení k DB
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Inicializace tabulky
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS history (id SERIAL PRIMARY KEY, msg TEXT, reply TEXT, is_tip BOOLEAN);')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    user_data = request.json
    user_msg = user_data.get('message', '')
    is_tip_request = user_data.get('is_tip', False)
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    # Rozlišení mezi tipem a chatem
    if is_tip_request:
        prompt = "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."
    else:
        prompt = f"Jsi užitečný asistent. Odpověz stručně na otázku: {user_msg}"

    payload = {
        "model": "gemma3:27b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        ai_reply = response.json()['choices'][0]['message']['content']

        # ULOŽENÍ DO DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO history (msg, reply, is_tip) VALUES (%s, %s, %s)', 
                    (user_msg if not is_tip_request else "TIP", ai_reply, is_tip_request))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": "Chyba serveru."}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8081)
