import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Kundenverwaltung – In Arbeit")

    message = (
        "Die Kundenverwaltung befindet sich noch in Entwicklung.\n"
        "Diese Ansicht dient als Platzhalter."
    )
    tk.Label(root, text=message, padx=20, pady=20, justify="center").pack()
    tk.Button(root, text="Fenster schließen", command=root.destroy).pack(pady=(10, 20))

    root.mainloop()


if __name__ == "__main__":
    main()
