import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

# Fenster starten
root = tk.Tk()
root.title("Rechnungsprogramm – Hauptmenü")

BASE_DIR = os.path.dirname(__file__)


def starte_gui(script_name):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        messagebox.showerror("Fehler", f"Die Datei {script_name} wurde nicht gefunden.")
        return
    subprocess.Popen([sys.executable, script_path])


tk.Button(root, text="📄 Rechnung erstellen", width=30,
          command=lambda: starte_gui("rechnung_gui.py")).pack(pady=10)

# Button: Kunden verwalten
tk.Button(root, text="👤 Kunden verwalten", width=30,
          command=lambda: starte_gui("kunden_gui.py")).pack(pady=10)

# Button: Einstellungen
tk.Button(root, text="⚙️ Einstellungen", width=30,
          command=lambda: starte_gui("einstellungen_gui.py")).pack(pady=10)

# Button: Statistik anzeigen (später)
tk.Button(root, text="📊 Statistik anzeigen", width=30,
          command=lambda: starte_gui("statistik_gui.py")).pack(pady=10)

# Starten
root.mainloop()
