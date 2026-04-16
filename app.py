import os
import psycopg2
import requests
import time
from flask import Flask, render_template, request, jsonify

# Inicializace Flask aplikace
app = Flask(__name__)

# --- DATABÁZOVÉ FUNKCE ---

def get_db_connection():
    """Vytvoří spojení s PostgreSQL databází pomocí údajů z Dockeru."""
    try:
        # os.environ.get bere URL z compose.yml (postgresql://postgres:heslo123@db:5432/wellness_db)
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Chyba připojení k DB: {e}")
        return None

def init_db():
    """Vytvoří tabulku v databázi při startu aplikace, pokud tam ještě není."""
    print("Inicializuji databázi...")
    # Čekáme 5 sekund, aby databázový kontejner stihl nastartovat dříve než Python
    time.sleep(5)
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # SQL příkaz pro vytvoření tabulky 'history'
            cur.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    msg TEXT NOT NULL,
                    reply TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit() # Potvrzení změn v databázi
            cur.close()
            conn.close()
            print("Databáze je připravena.")
        except Exception as e:
            print(f"Chyba při tvorbě tabulky: {e}")

# --- TRASY (ROUTES) ---

@app.route('/')
def index():
    """Zobrazí hlavní webovou stránku (fialový chat)."""
    return render_template('index.html')

@app.route('/historie')
def zobraz_historii():
    """Vytáhne všechna data z DB a zobrazí je v přehledné tabulce."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # SQL dotaz: Vyber vše a seřaď od nejnovějšího (ID DESC)
            cur.execute('SELECT id, msg, reply, created_at FROM history ORDER BY id DESC;')
            vysledky = cur.fetchall() # Načtení všech řádků
            cur.close()
            conn.close()
            # Pošle data do souboru historie.html
            return render_template('historie.html', data=vysledky)
        except Exception as e:
            return f"Chyba při čtení z DB: {e}"
    return "Nepodařilo se připojit k databázi."

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    """Zpracuje dotaz z webu nebo widgetu, zavolá AI a uloží výsledek."""
    data = request.get_json() # Načte JSON data (zprávu) od uživatele
    if not data or 'message' not in data:
        return jsonify({"reply": "Chyba: Žádná zpráva neposlána."}), 400

    user_msg = data.get('message', '')
    
    # Načtení API klíče z prostředí portálu
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://kurim.ithope.eu/v1/chat/completions"
    
    # Příprava dat pro školní AI server (Gemma 3)
    payload = {
        "model": "gemma3:27b",
        "messages": [{"role": "user", "content": user_msg}]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Odeslání požadavku na AI server pomocí knihovny requests
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status() # Vyhodí chybu, pokud server vrátí např. 404 nebo 500
        ai_reply = response.json()['choices'][0]['message']['content']

        # Zápis konverzace do databáze (SQL INSERT)
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO history (msg, reply) VALUES (%s, %s)', (user_msg, ai_reply))
            conn.commit()
            cur.close()
            conn.close()

        # Vrátí odpověď jako JSON zpět do prohlížeče nebo widgetu
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"Chyba AI endpointu: {e}")
        return jsonify({"reply": f"Chyba na serveru: {str(e)}"}), 500

# --- START ---

if __name__ == '__main__':
    # Spustí inicializaci DB a následně Flask server
    init_db()
    # Host '0.0.0.0' je nutný, aby aplikace byla dostupná v Docker síti
    app.run(host='0.0.0.0', port=8081)
