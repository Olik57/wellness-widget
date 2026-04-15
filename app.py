import os
import psycopg2
import time
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Klient pro AI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def get_db_connection():
    # Zkusí se připojit k DB (čeká, dokud DB nenaběhne)
    for i in range(10):
        try:
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            return conn
        except:
            time.sleep(2)
    return None

def init_db():
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
    data = request.json
    user_msg = data.get('message', '')
    
    try:
        # Volání AI modelu
        response = client.chat.completions.create(
            model="gemma3:27b",
            messages=[{"role": "user", "content": user_msg}]
        )
        ai_reply = response.choices[0].message.content

        # Zápis do databáze
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO history (msg, reply) VALUES (%s, %s)', (user_msg, ai_reply))
            conn.commit()
            cur.close()
            conn.close()

        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"Chyba serveru: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8081)
