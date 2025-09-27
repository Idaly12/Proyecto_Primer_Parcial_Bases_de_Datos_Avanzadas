import oracledb
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, StringVar, Listbox, Text, Frame

# Configuración de la conexión
DB_USER = "proyecto"
DB_PASS = "proyecto"
DB_DSN = "localhost/XEPDB1"

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# --- Usuarios ---
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

# --- Artículos ---
def create_article(title, text, user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_article", [title, text, user_id])
        conn.commit()
        messagebox.showinfo("Éxito", "Artículo publicado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al publicar artículo: {e}")
    finally:
        cur.close()
        conn.close()

def get_user_articles(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        result_cursor = cur.callfunc("get_articles_by_user", oracledb.DB_TYPE_CURSOR, [user_id])
        articles = result_cursor.fetchall()
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar artículos: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# --- Categorías ---
def get_all_categories():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def associate_article_categories(article_id, category_ids):
    conn = get_connection()
    cur = conn.cursor()
    try:
        for cat_id in category_ids:
            cur.callproc("add_article_category", [article_id, cat_id])
        conn.commit()
    finally:
        cur.close()
        conn.close()

# --- Ventanas ---
def login_window(root):
    win = Toplevel(root)
    win.title("Login")
    win.geometry("350x250")
    win.configure(bg="#1e1e2f")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    Label(win, text="Email:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    email_var = StringVar()
    Entry(win, textvariable=email_var, width=30).pack(pady=5)

    Label(win, text="Contraseña:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_var = StringVar()
    Entry(win, textvariable=password_var, show="*", width=30).pack(pady=5)

    def attempt_login():
        correo = email_var.get()
        password_input = password_var.get()
        if not correo or "@" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return

        usuario = user_exists(correo)
        if usuario:
            if password_input == usuario[3]:
                win.destroy()
                root.withdraw()
                blog_window(root, usuario[0], usuario[1])
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def blog_window(root, user_id, username):
    blog_win = Toplevel(root)
    blog_win.title(f"Blog de {username}")
    blog_win.geometry("900x600")
    blog_win.configure(bg="#282c34")

    main_frame = Frame(blog_win, bg="#282c34")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Crear artículo ---
    create_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
    create_frame.grid(row=0, column=0, sticky="nsew", padx=5)
    main_frame.columnconfigure(0, weight=2)
    main_frame.rowconfigure(0, weight=1)

    Label(create_frame, text="Nuevo Artículo", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)

    Label(create_frame, text="Título:", font=("Arial", 12), bg="#2f2f3f", fg="white").pack(anchor="w", pady=(10,0))
    title_entry = Entry(create_frame, font=("Arial", 12), width=50)
    title_entry.pack(fill="x", pady=5)

    Label(create_frame, text="Contenido:", font=("Arial", 12), bg="#2f2f3f", fg="white").pack(anchor="w", pady=(10,0))
    content_text = Text(create_frame, font=("Arial", 11), height=15, wrap="word")
    content_text.pack(fill="both", expand=True, pady=5)

    Label(create_frame, text="Categorías:", font=("Arial", 12), bg="#2f2f3f", fg="white").pack(anchor="w", pady=(10,0))
    categories_listbox = Listbox(create_frame, selectmode="multiple", bg="#3c3c4c", fg="white", height=6)
    categories_listbox.pack(fill="x", pady=5)

    all_categories = get_all_categories()
    for cat in all_categories:
        categories_listbox.insert('end', f"{cat[1]}")  # cat[1] = nombre

    # --- Lista de artículos ---
    list_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
    list_frame.grid(row=0, column=1, sticky="nsew", padx=5)
    main_frame.columnconfigure(1, weight=1)

    Label(list_frame, text="Mis Artículos", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)
    articles_listbox = Listbox(list_frame, font=("Arial", 11), bg="#3c3c4c", fg="white")
    articles_listbox.pack(fill="both", expand=True)

    def refresh_articles():
        articles_listbox.delete(0, 'end')
        articles = get_user_articles(user_id)
        if articles:
            for article in articles:
                articles_listbox.insert('end', article[1])

    def publish_article():
        title = title_entry.get()
        content = content_text.get("1.0", "end-1c")
        if not title or not content:
            messagebox.showerror("Error", "El título y el contenido no pueden estar vacíos.")
            return

        create_article(title, content, user_id)

        # Obtener el article_id recién creado
        articles = get_user_articles(user_id)
        article_id = articles[-1][0]

        # Asociar categorías
        selected_indices = categories_listbox.curselection()
        selected_ids = [all_categories[i][0] for i in selected_indices]
        associate_article_categories(article_id, selected_ids)

        title_entry.delete(0, 'end')
        content_text.delete("1.0", 'end')
        categories_listbox.selection_clear(0, 'end')
        refresh_articles()

    Button(create_frame, text="Publicar Artículo", command=publish_article, bg="#98c379", fg="white", font=("Arial", 12)).pack(pady=15)

    def on_close():
        blog_win.destroy()
        root.deiconify()
    blog_win.protocol("WM_DELETE_WINDOW", on_close)
    refresh_articles()

def register_window(root):
    win = Toplevel(root)
    win.title("Registro")
    win.geometry("350x350")
    win.configure(bg="#2f2f3f")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

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

        if not correo or "@" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return
        if user_exists(correo):
            messagebox.showwarning("Aviso", "Email ya existente")
            return
        if password != password_confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        create_user(nombre, correo, password)
        win.destroy()

    Button(win, text="Registrarse", command=attempt_register, bg="#98c379", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def main_menu():
    root = tk.Tk()
    root.title("Gestión de Usuarios")
    root.geometry("400x300")
    root.configure(bg="#282c34")

    root.columnconfigure(0, weight=1)
    for i in range(3):
        root.rowconfigure(i, weight=1)

    btn_login = Button(root, text="Login", command=lambda: login_window(root), bg="#61afef", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_login.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

    btn_register = Button(root, text="Registrarse", command=lambda: register_window(root), bg="#98c379", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_register.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    btn_exit = Button(root, text="Salir", command=root.destroy, bg="#e06c75", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_exit.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
