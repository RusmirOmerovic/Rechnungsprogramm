import tkinter as tk
import os

# Fenster starten
root = tk.Tk()
root.title("Rechnungsprogramm – Hauptmenü")

# Button: Rechnung erstellen
tk.Button(root, text="📄 Rechnung erstellen", width=30,
          command=lambda: os.system("python3 gui/rechnung_gui.py")).pack(pady=10)

# Button: Kunden verwalten
tk.Button(root, text="👤 Kunden verwalten", width=30,
          command=lambda: os.system("python3 gui/kunden_gui.py")).pack(pady=10)

# Button: Einstellungen
tk.Button(root, text="⚙️ Einstellungen", width=30,
          command=lambda: os.system("python3 gui/einstellungen_gui.py")).pack(pady=10)

# Button: Statistik anzeigen (später)
tk.Button(root, text="📊 Statistik anzeigen", width=30,
          command=lambda: os.system("python3 gui/statistik_gui.py")).pack(pady=10)

# Starten
root.mainloop()
