import tkinter as tk
import subprocess

root = tk.Tk()
root.title("Rechnungsprogramm – Startmenü")

tk.Button(root, text="📄 Rechnung erstellen", width=30,
          command=lambda: subprocess.Popen(["python3", "gui/rechnung_gui.py"])).pack(pady=5)

tk.Button(root, text="👤 Kunden verwalten", width=30,
          command=lambda: subprocess.Popen(["python3", "gui/kunden_gui.py"])).pack(pady=5)

tk.Button(root, text="⚙️ Einstellungen", width=30,
          command=lambda: subprocess.Popen(["python3", "gui/einstellungen_gui.py"])).pack(pady=5)

tk.Button(root, text="📊 Statistik anzeigen", width=30,
          command=lambda: subprocess.Popen(["python3", "gui/statistik_gui.py"])).pack(pady=5)

root.mainloop()
