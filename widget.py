import tkinter as tk
import requests

def get_ai_tip():
    try:
        # Zavolá AI endpoint na školním serveru
        res = requests.post('https://olik.kurim.ithope.eu/ai', timeout=15)
        return res.json().get('tip', 'Nezapomeň se protáhnout!')
    except:
        # Při chybě spojení
        return 'Nelze se připojit k serveru.'

def show_tip():
    label.config(text='Načítám tip...', fg='white')
    title.config(text='Wellness Tip!')
    
    # Zavolá AI ve vlastním vlákně aby GUI nezamrzlo
    import threading
    def fetch():
        tip = get_ai_tip()
        # Aktualizace GUI v hlavním vlákně
        root.after(0, lambda: label.config(text=tip, fg='white'))
    threading.Thread(target=fetch, daemon=True).start()
    
    # Schová tip po 5 minutách
    root.after(300000, hide_tip)
    # Další tip za 1 hodinu
    root.after(3600000, show_tip)

def hide_tip():
    label.config(text='Jsi skvely! Pokracuj dal.', fg='#c8f5c8')
    title.config(text='Wellness')

root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.attributes('-alpha', 0.92)
root.configure(bg='#4CAF50')
w, h = 300, 110
x = root.winfo_screenwidth() - w - 20
y = root.winfo_screenheight() - h - 60
root.geometry(f'{w}x{h}+{x}+{y}')
title = tk.Label(root, text='Wellness', bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'))
title.pack(pady=5)
label = tk.Label(root, text='Jsi skvely! Pokracuj dal.', bg='#4CAF50', fg='#c8f5c8', font=('Arial', 9), wraplength=280)
label.pack()
tk.Button(root, text='X', command=root.destroy, bg='#388E3C', fg='white', border=0).place(x=278, y=2)

# První tip za 5 sekund po spuštění
root.after(5000, show_tip)
root.mainloop()
