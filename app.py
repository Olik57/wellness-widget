import os                                                      # Knihovna pro čtení proměnných prostředí (API klíč, URL)
import requests                                                # Knihovna pro posílání HTTP dotazů na AI server
from flask import Flask, render_template, jsonify              # Flask = webový server, render_template = zobrazení HTML, jsonify = JSON odpovědi

app = Flask(__name__)                                          # Vytvoření Flask aplikace

@app.route('/')                                                # Hlavní stránka webu
def index():
    return render_template('index.html')                       # Zobrazí soubor templates/index.html

@app.route('/ping', methods=['GET'])                           # Endpoint pro otestování jestli server běží
def ping():
    return "pong"                                              # Vrátí "pong" — server žije

@app.route('/status', methods=['GET'])                         # Endpoint pro zjištění stavu serveru
def status():
    return jsonify({"status": "ok", "model": "gemma3:27b"})   # Vrátí JSON s informací o modelu

@app.route('/ai', methods=['POST'])                            # Endpoint pro získání wellness tipu od AI
def ai_tip():
    api_key = os.getenv("OPENAI_API_KEY")                      # Načte API klíč z proměnné prostředí
    base_url = os.getenv("OPENAI_BASE_URL")                    # Načte adresu AI serveru z proměnné prostředí

    payload = {
        "model": "gemma3:27b",                                 # Určení AI modelu
        "messages": [
            {"role": "user", "content": "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."}
        ],                                                     # Zpráva odeslaná AI modelu
        "stream": False                                        # Odpověď přijde celá naráz, ne po kouskách
    }

    headers = {
        "Authorization": f"Bearer {api_key}",                  # Autorizace pomocí API klíče
        "Content-Type": "application/json"                     # Formát dat je JSON
    }

    try:
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)  # Odeslání dotazu na AI server
        result = response.json()                               # Převedení odpovědi na JSON
        tip = result['choices'][0]['message']['content']       # Vytažení textu tipu z odpovědi
        return jsonify({"tip": tip})                           # Vrácení tipu jako JSON
    except Exception as e:
        return jsonify({"tip": "Nezapomeň se protáhnout!"})    # Při chybě vrátí záložní tip

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)                        # Spuštění serveru — dostupný zvenčí na portu 8081
