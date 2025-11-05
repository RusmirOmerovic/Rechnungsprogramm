import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Einstellungen – In Arbeit")

    message = (
        "Der Einstellungsbereich ist noch nicht verfügbar.\n"
        "Diese Ansicht dient zur Platzhalteranzeige."
    )
    tk.Label(root, text=message, padx=20, pady=20, justify="center").pack()
    tk.Button(root, text="Fenster schließen", command=root.destroy).pack(pady=(10, 20))

    root.mainloop()


if __name__ == "__main__":
    main()
