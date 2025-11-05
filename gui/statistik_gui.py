import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Statistiken – In Arbeit")

    message = (
        "Die Statistikfunktionen werden noch entwickelt.\n"
        "Bis dahin zeigt dieses Fenster einen Platzhalter an."
    )
    tk.Label(root, text=message, padx=20, pady=20, justify="center").pack()
    tk.Button(root, text="Fenster schließen", command=root.destroy).pack(pady=(10, 20))

    root.mainloop()


if __name__ == "__main__":
    main()
