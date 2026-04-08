import tkinter as tk
import requests
import threading
import time

# Nastavení spojení na tvůj VirtualBox server
SERVER_URL = "http://10.10.10.1:8081/ai"

class WellnessWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Wellness Assistant")
        
        # Nastavení okna (vpravo dole, vždy navrchu)
        self.root.geometry("300x120+10+10") # Pozici si uprav podle monitoru
        self.root.overrideredirect(True) # Odstraní rám okna
        self.root.attributes("-topmost", True) # Vždy navrchu
        self.root.configure(bg='#2c3e50')

        # Textové pole pro tip
        self.label_title = tk.Label(root, text="🌿 Wellness Tip", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50")
        self.label_title.pack(pady=5)

        self.label_text = tk.Label(root, text="Načítám tip...", wraplength=250, fg="#ecf0f1", bg="#2c3e50", font=("Arial", 10))
        self.label_text.pack(pady=5)

        # Tlačítko pro zavření
        self.close_button = tk.Button(root, text="X", command=self.root.withdraw, bd=0, bg="#c0392b", fg="white")
        self.close_button.place(x=275, y=5)

        # Spuštění smyčky pro aktualizaci v samostatném vlákně
        self.update_thread = threading.Thread(target=self.periodic_update, daemon=True)
        self.update_thread.start()

    def get_ai_tip(self):
        try:
            # Volání tvého Flask endpointu na Ubuntu
            response = requests.post(SERVER_URL, timeout=10)
            if response.status_code == 200:
                return response.json().get('tip', 'Nezapomeň se protáhnout!')
            return "Server neodpovídá, zkus se napít vody!"
        except Exception as e:
            return f"Chyba spojení: {e}"

    def periodic_update(self):
        while True:
            novy_tip = self.get_ai_tip()
            
            # Aktualizace textu v GUI
            self.label_text.config(text=novy_tip)
            
            # Zobrazení okna (pokud bylo schované)
            self.root.deiconify()
            
            # Čekání 1 hodinu (3600 sekund)
            time.sleep(3600)

if __name__ == "__main__":
    root = tk.Tk()
    app = WellnessWidget(root)
    root.mainloop()
