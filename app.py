import os
import psycopg2
import time
import requests # Přidáme pro jistotu jako alternativu
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Nastavení AI klienta
# DŮLEŽITÉ: base_url musí končit /v1, pokud používáš OpenAI knihovnu
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://kurim.ithope.eu/v1"
)

def get_db_connection():
    try:
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    except:
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
        # Volání modelu Gemma 3
        # Model se musí jmenovat přesně "gemma3:27b"
        completion = client.chat.completions.create(
            model="gemma3:27b",
            messages=[
                {"role": "system", "content": "Jsi wellness asistent."},
                {"role": "user", "content": user_msg}
            ]
        )
        ai_reply = completion.choices[0].message.content

        # Zápis do databáze (dobrovolné, ale pro maturitu nutné)
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO history (msg, reply) VALUES (%s, %s)', (user_msg, ai_reply))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as db_err:
            print(f"DB Error: {db_err}")

        return jsonify({"reply": ai_reply})

    except Exception as e:
        # Pokud to spadne, vypíšeme chybu přímo do webu, abychom věděli proč
        return jsonify({"reply": f"Chyba API: {str(e)}"}), 500

if __name__ == '__main__':
    # Počkáme 5 sekund, než databáze v Dockeru opravdu nastartuje
    time.sleep(5)
    init_db()
    app.run(host='0.0.0.0', port=8081)
