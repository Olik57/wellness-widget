import tkinter as tk
import requests

TIPS_SCHEDULE = [
    (60, "Napij se vody!"),
    (180, "Cas se protahnout!"),
    (60, "Dej si pauzu od obrazovky."),
    (120, "Zhluboka se nadychni 3x."),
]

tip_index = 0

def get_ai_tip(base_tip):
    try:
        res = requests.post('http://127.0.0.1:8081/ai', timeout=10)
        return res.json().get('tip', base_tip)
    except:
        return base_tip

def show_tip():
    global tip_index
    interval, base_tip = TIPS_SCHEDULE[tip_index % len(TIPS_SCHEDULE)]
    tip_index += 1
    tip = get_ai_tip(base_tip)
    label.config(text=tip, fg='white')
    title.config(text="Wellness Tip!")
    next_minutes = TIPS_SCHEDULE[tip_index % len(TIPS_SCHEDULE)][0]
    root.after(next_minutes * 60000, show_tip)
    root.after(300000, hide_tip)

def hide_tip():
    label.config(text="Jsi skvely! Pokracuj dal.", fg='#c8f5c8')
    title.config(text="Wellness")

root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.attributes('-alpha', 0.92)
root.configure(bg='#4CAF50')
w, h = 300, 110
x = root.winfo_screenwidth() - w - 20
y = root.winfo_screenheight() - h - 60
root.geometry(f'{w}x{h}+{x}+{y}')

title = tk.Label(root, text="Wellness", bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'))
title.pack(pady=5)

label = tk.Label(root, text="Jsi skvely! Pokracuj dal.", bg='#4CAF50', fg='#c8f5c8', font=('Arial', 9), wraplength=280)
label.pack()

tk.Button(root, text="X", command=root.destroy, bg='#388E3C', fg='white', border=0).place(x=278, y=2)

root.after(5000, show_tip)
root.mainloop()
