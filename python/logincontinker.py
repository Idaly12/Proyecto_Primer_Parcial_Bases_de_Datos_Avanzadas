import oracledb
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, StringVar, Frame, Listbox, Scrollbar, END

# Configuración de la base de datos
DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1"

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# --- Funciones de usuario ---
def user_exists(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, email, password FROM users WHERE email = :email", {"email": email})
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        messagebox.showinfo("Éxito", "Usuario creado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear usuario: {e}")
    finally:
        cur.close()
        conn.close()

# --- Ventana de categorías ---
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

def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_id")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

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

    listbox_frame = Frame(frame, bg="#FFF5EE")
    listbox_frame.pack(fill="both", expand=True)

    scrollbar = Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    listbox = Listbox(listbox_frame, font=("Arial", 12), yscrollcommand=scrollbar.set)
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    refresh_listbox()

# --- Ventanas de login y registro ---
def login_window(root, on_success):
    win = Toplevel(root)
    win.title("Login")
    win.geometry("350x250")
    win.configure(bg="#1e1e2f")

    Label(win, text="Email:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    email_var = StringVar()
    Entry(win, textvariable=email_var, width=30).pack(pady=5)

    Label(win, text="Contraseña:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_var = StringVar()
    Entry(win, textvariable=password_var, show="*", width=30).pack(pady=5)

    def attempt_login():
        correo = email_var.get()
        password_input = password_var.get()
        if not correo or "@gmail.com" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return

        usuario = user_exists(correo)
        if usuario:
            if password_input == usuario[3]:
                messagebox.showinfo("Bienvenido", f"Hola {usuario[1]}")
                win.destroy()
                on_success(usuario)
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def register_window(root, on_success):
    win = Toplevel(root)
    win.title("Registro")
    win.geometry("350x350")
    win.configure(bg="#2f2f3f")

    Label(win, text="Nombre:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    nombre_var = StringVar()
    Entry(win, textvariable=nombre_var, width=30).pack(pady=5)

    Label(win, text="Email:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    email_var = StringVar()
    Entry(win, textvariable=email_var, width=30).pack(pady=5)

    Label(win, text="Contraseña:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_var = StringVar()
    Entry(win, textvariable=password_var, show="*", width=30).pack(pady=5)

    Label(win, text="Confirmar contraseña:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_confirm_var = StringVar()
    Entry(win, textvariable=password_confirm_var, show="*", width=30).pack(pady=5)

    def attempt_register():
        nombre = nombre_var.get()
        correo = email_var.get()
        password = password_var.get()
        password_confirm = password_confirm_var.get()

        if not correo or "@gmail.com" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return
        if user_exists(correo):
            messagebox.showwarning("Aviso", "Email ya existente")
            return
        if password != password_confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        create_user(nombre, correo, password)
        messagebox.showinfo("Éxito", "Usuario registrado")
        win.destroy()
        on_success(user_exists(correo))

    Button(win, text="Registrarse", command=attempt_register, bg="#98c379", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

# --- Menú principal después de login/registro ---
def app_menu(user):
    root = tk.Tk()
    root.title(f"Panel de {user[1]}")
    root.geometry("400x400")
    root.configure(bg="#282c34")

    Button(root, text="Categorías", command=lambda: categories_window(root),
           bg="#E74C3C", fg="white", font=("Arial", 14)).pack(pady=20, fill="x", padx=40)

    # Aquí puedes agregar más botones para otras tablas: Users, Articles, Comments, Tags, Article_Tags, Article_Categories
    # Ejemplo:
    # Button(root, text="Gestionar Artículos", command=lambda: articles_window(root), ...)

    Button(root, text="Salir", command=root.destroy, bg="#e06c75", fg="white", font=("Arial", 14)).pack(pady=20, fill="x", padx=40)

    root.mainloop()

# --- Ventana inicial ---
def main_menu():
    root = tk.Tk()
    root.title("Gestión de Usuarios")
    root.geometry("400x300")
    root.configure(bg="#282c34")

    Button(root, text="Login", command=lambda: login_window(root, app_menu),
           bg="#61afef", fg="white", font=("Arial", 14), relief="ridge", bd=3).pack(pady=20, fill="x", padx=40)

    Button(root, text="Registrarse", command=lambda: register_window(root, app_menu),
           bg="#98c379", fg="white", font=("Arial", 14), relief="ridge", bd=3).pack(pady=20, fill="x", padx=40)

    Button(root, text="Salir", command=root.destroy, bg="#e06c75", fg="white", font=("Arial", 14), relief="ridge", bd=3).pack(pady=20, fill="x", padx=40)

    root.mainloop()

if __name__ == "__main__":
    main_menu()

if __name__ == "__main__":
    main_menu()