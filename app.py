import os                                                      # Pro čtení API klíčů a URL z prostředí [cite: 4, 140]
import requests                                                # Pro odesílání dotazů na AI backend [cite: 4, 140]
from flask import Flask, render_template, jsonify, request     # Webový framework a práce s JSONem [cite: 4, 140]

app = Flask(__name__)                                          # Inicializace Flask aplikace [cite: 4, 140]

# --- CESTY (ROUTES) ---

@app.route('/')                                                # Hlavní stránka (pokud bys ji chtěl v prohlížeči) [cite: 79]
def index():
    return render_template('index.html')                       # Zobrazí tvůj HTML web [cite: 79, 80]

@app.route('/ping', methods=['GET'])                           # Testovací endpoint pro kontrolu běhu [cite: 127, 128]
def ping():
    return "pong"

@app.route('/status', methods=['GET'])                         # Informace o běžícím modelu [cite: 46, 48]
def status():
    return jsonify({"status": "ok", "model": "gemma3:27b"})

@app.route('/ai', methods=['POST'])                            # Hlavní brána pro tvůj widget [cite: 5, 50, 140]
def ai_handler():
    # Načtení tajných údajů ze systému (prostředí) [cite: 135, 137]
    api_key = os.getenv("OPENAI_API_KEY")                      
    base_url = os.getenv("OPENAI_BASE_URL")                    

    # Zpracování dat, která přišla z tvého Python widgetu [cite: 4, 140]
    user_data = request.json
    user_message = user_data.get("message", "")                # Co jsi napsal do okýnka [cite: 67]

    # ROZHODOVACÍ LOGIKA: Rozlišíme, jestli chceš tip nebo se ptáš [cite: 62, 65]
    if not user_message or user_message == "POŠLI_WELLNESS_TIP":
        # Pokud přišel požadavek na tip, dáme AI tento příkaz: [cite: 4, 140]
        prompt_for_ai = "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."
    else:
        # Pokud jsi něco napsal, pošleme to AI jako otázku k zodpovězení: [cite: 4, 140]
        prompt_for_ai = f"Jsi užitečný asistent. Odpověz stručně na otázku: {user_message}"

    # Příprava datového balíčku pro model Gemma 3 [cite: 16, 21]
    payload = {
        "model": "gemma3:27b",
        "messages": [
            {"role": "user", "content": prompt_for_ai}
        ],
        "stream": False                                        # Odpověď chceme najednou [cite: 4, 140]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",                  # Tvá legitimace pro AI server [cite: 135, 138]
        "Content-Type": "application/json"
    }

    try:
        # Samotné odeslání dotazu do AI světa [cite: 131, 134]
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        result = response.json()
        
        # Vytažení textu odpovědi z hluboké struktury JSONu [cite: 83, 85]
        answer = result['choices'][0]['message']['content']
        
        # Vrátíme odpověď widgetu (klíč 'tip' zachováme pro kompatibilitu) [cite: 4, 140]
        return jsonify({"tip": answer})
    
    except Exception as e:
        # Pokud se něco pokazí (výpadek AI, špatný klíč), vrátíme nouzovou hlášku [cite: 4, 140]
        print(f"Chyba na serveru: {e}")
        return jsonify({"tip": "Nezapomeň se protáhnout! (AI momentálně neodpovídá)"})

# --- SPUŠTĚNÍ --- [cite: 4, 140]
if __name__ == '__main__':
    # Server poběží na portu 8081 a bude viditelný v síti [cite: 122, 127]
    app.run(host='0.0.0.0', port=8081)
