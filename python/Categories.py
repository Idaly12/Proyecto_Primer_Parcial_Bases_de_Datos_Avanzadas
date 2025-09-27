import oracledb
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, StringVar, Frame, Listbox, Scrollbar, END

# Configuración de la base de datos
DB_USER = "proyecto"
DB_PASS = "proyecto"
DB_DSN = "localhost/XEPDB1"

# Función para obtener la conexión
def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# Función para crear categoría
def create_category(category_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_category", [category_name])
        conn.commit()
        messagebox.showinfo("Éxito", "Categoría creada correctamente 🎉")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear categoría: {e}")
    finally:
        cur.close()
        conn.close()

# Función para obtener todas las categorías
def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_id")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# Ventana de gestión de categorías
def categories_window(root):
    win = Toplevel(root)
    win.title("Gestión de Categorías")
    win.geometry("600x500")
    win.resizable(False, False)
    win.configure(bg="#FFF5EE")

    frame = Frame(win, bg="#FFF5EE")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    Label(frame, text="Nueva Categoría", font=("Helvetica", 16, "bold"), bg="#FFF5EE").pack(pady=(0,10))

    cat_var = StringVar()
    entry = Entry(frame, textvariable=cat_var, font=("Arial", 12))
    entry.pack(pady=5, fill="x")

    def refresh_listbox():
        listbox.delete(0, END)
        categories = get_all_categories()
        for cat in categories:
            listbox.insert(END, f"{cat[0]} - {cat[1]}")

    def save_category():
        nombre = cat_var.get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "El nombre no puede estar vacío")
            return
        create_category(nombre)
        cat_var.set("")
        refresh_listbox()

    Button(frame, text="Agregar Categoría", command=save_category,
           bg="#E74C3C", fg="white", font=("Arial", 12, "bold")).pack(pady=10, fill="x")

    Label(frame, text="Categorías existentes:", font=("Helvetica", 14, "bold"), bg="#FFF5EE").pack(pady=(20,5))

    # Listbox con scrollbar
    listbox_frame = Frame(frame, bg="#FFF5EE")
    listbox_frame.pack(fill="both", expand=True)

    scrollbar = Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = Listbox(listbox_frame, font=("Arial", 12), yscrollcommand=scrollbar.set)
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    refresh_listbox()

# Código principal para abrir la ventana
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    categories_window(root)
    root.mainloop()
