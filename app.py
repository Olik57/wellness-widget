import os                                                      # Pro čtení API klíčů
import requests                                                # Pro posílání dotazů na AI
from flask import Flask, render_template, jsonify, request     # Webový framework

app = Flask(__name__)

# --- PAMĚŤ PRO TIPY ---
# Sem si budeme ukládat poslední tipy, abychom se neopakovali
used_tips = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai', methods=['POST'])
def ai_handler():
    api_key = os.getenv("OPENAI_API_KEY")                      
    base_url = os.getenv("OPENAI_BASE_URL")                    

    user_data = request.json
    user_message = user_data.get("message", "")

    # Rozlišení mezi wellness tipem a chatem
    if not user_message or user_message == "POŠLI_WELLNESS_TIP":
        # Do instrukce přidáme seznam již použitých tipů, aby se AI vyhnula opakování
        history_str = ", ".join(used_tips[-5:]) # Vezmeme posledních 5 tipů
        prompt_for_ai = (f"Dej mi jeden krátký wellness tip pro práci u počítače. "
                         f"Max 2 věty. Česky. Nepoužívej tyto tipy: {history_str}")
    else:
        prompt_for_ai = f"Jsi užitečný asistent. Odpověz stručně na otázku: {user_message}"

    payload = {
        "model": "gemma3:27b",
        "messages": [{"role": "user", "content": prompt_for_ai}],
        "temperature": 0.9,                                    # Vyšší teplota = větší kreativita a méně opakování
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        # Pokud šlo o tip, uložíme si ho do paměti (pokud tam už není)
        if not user_message or user_message == "POŠLI_WELLNESS_TIP":
            if answer not in used_tips:
                used_tips.append(answer)
            # Udržujeme paměť rozumně velkou (posledních 20 položek)
            if len(used_tips) > 20:
                used_tips.pop(0)

        return jsonify({"tip": answer})
    
    except Exception as e:
        print(f"Chyba: {e}")
        return jsonify({"tip": "Nezapomeň pít hodně vody a protáhnout se!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
