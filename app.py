from flask import Flask, jsonify  # Flask pro webový server, jsonify pro JSON odpovědi
from openai import OpenAI  # OpenAI klient pro komunikaci s AI modelem

app = Flask(__name__)  # Vytvoření Flask aplikace

# Nastavení připojení k OpenAI-compatible API
client = OpenAI(
    api_key="sk-ivPZMD_qRIv0vyeGo4a43A",  # API klíč pro autentizaci
    base_url="https://kurim.ithope.eu/v1"   # Vlastní server místo oficiálního OpenAI
)

# Endpoint /ai přijímá POST requesty z widget.py
@app.route('/ai', methods=['POST'])
def ai_tip():
    try:
        # Zavolání AI modelu s požadavkem na wellness tip
        response = client.chat.completions.create(
            model="gemma3:27b",  # Model který chceme použít
            messages=[
                {
                    "role": "user",
                    # Prompt pro AI - krátký wellness tip v češtině
                    "content": "Dej mi jeden krátký wellness tip pro práci u počítače. Max 2 věty. Česky."
                }
            ],
            max_tokens=100  # Maximální délka odpovědi
        )
        # Vytažení textu z odpovědi a oříznutí mezer
        tip = response.choices[0].message.content.strip()
        # Vrácení tipu jako JSON: {"tip": "..."}
        return jsonify({"tip": tip})
    except Exception as e:
        # Při chybě vrátíme záložní tip místo pádu serveru
        return jsonify({"tip": "Nezapomeň se protáhnout!"}), 500

# Spuštění serveru
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # Naslouchá na všech rozhraních (dostupné z VirtualBoxu)
        port=8081         # Port musí odpovídat SERVER_URL v widget.py
    )
