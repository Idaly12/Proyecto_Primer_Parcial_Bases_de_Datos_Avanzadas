<<<<<<< HEAD:Proyecto Primer Parcial/Base de datos sql/python/logincontinker.py
import oracledb
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, StringVar

DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1"



#Configuración de la conexión Idaly
#DB_USER = "proyecto"
#DB_PASS = "proyecto"
#DB_DSN = "localhost/XEPDB1" 
def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

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

def login_window(root):
    win = Toplevel(root)
    win.title("Login")
    win.geometry("350x250")
    win.configure(bg="#1e1e2f")  # Fondo custom

    # Centrar la ventana
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
        if not correo or "@gmail.com" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return

        usuario = user_exists(correo)
        if usuario:
            if password_input == usuario[3]:
                messagebox.showinfo("Bienvenido", f"Hola {usuario[1]}")
                win.destroy()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def register_window(root):
    win = Toplevel(root)
    win.title("Registro")
    win.geometry("350x350")
    win.configure(bg="#2f2f3f")

    # Centrar ventana
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
        win.destroy()

    Button(win, text="Registrarse", command=attempt_register, bg="#98c379", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def main_menu():
    root = tk.Tk()
    root.title("Gestión de Usuarios")
    root.geometry("400x300")
    root.configure(bg="#282c34")

    # Configuración de grid para expandir botones
    root.columnconfigure(0, weight=1)
    for i in range(3):
        root.rowconfigure(i, weight=1)

    # Botones con estilo custom
    btn_login = Button(root, text="Login", command=lambda: login_window(root), bg="#61afef", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_login.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

    btn_register = Button(root, text="Registrarse", command=lambda: register_window(root), bg="#98c379", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_register.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    btn_exit = Button(root, text="Salir", command=root.destroy, bg="#e06c75", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_exit.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
=======
import oracledb
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, StringVar, Listbox, Scrollbar, Text, Frame

DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1"

#Configuración de la conexión Idaly
#DB_USER = "proyecto"
#DB_PASS = "proyecto"
#DB_DSN = "localhost/XEPDB1" 

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def user_exists(email):
    conn = get_connection()
    cur = conn.cursor()
    # Devolvemos el user_id también, lo necesitaremos
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

## NUEVO ## - Función para crear un artículo en la base de datos
def create_article(title, text, user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Llama al procedimiento almacenado 'add_article'
        cur.callproc("add_article", [title, text, user_id])
        conn.commit()
        messagebox.showinfo("Éxito", "Artículo publicado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al publicar artículo: {e}")
    finally:
        cur.close()
        conn.close()


## NUEVO ## - Función para obtener los artículos de un usuario (CORREGIDA)
def get_user_articles(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # --- ESTA ES LA PARTE CORREGIDA ---
        # En lugar de crear una variable con cur.var(), pasamos el TIPO directamente a callfunc.
        result_cursor = cur.callfunc("get_articles_by_user", oracledb.DB_TYPE_CURSOR, [user_id])
        
        # Leemos los resultados del cursor
        articles = result_cursor.fetchall()
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar artículos: {e}")
        return []
    finally:
        cur.close()
        conn.close()

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
        if not correo or "@" not in correo: # Verificación más genérica
            messagebox.showerror("Error", "Correo no válido")
            return

        usuario = user_exists(correo)
        if usuario:
            # usuario[0] = user_id, usuario[1] = username, usuario[3] = password
            if password_input == usuario[3]:
                ## MODIFICADO ## - En lugar de un mensaje, abrimos la ventana del blog
                win.destroy() # Cerramos la ventana de login
                root.withdraw() # Ocultamos la ventana principal del menú
                blog_window(root, usuario[0], usuario[1]) # Abrimos la ventana del blog
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

## NUEVO ## - Ventana principal del Blog para crear y ver artículos
def blog_window(root, user_id, username):
    blog_win = Toplevel(root)
    blog_win.title(f"Blog de {username}")
    blog_win.geometry("800x600")
    blog_win.configure(bg="#282c34")

    # Frame principal
    main_frame = Frame(blog_win, bg="#282c34")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # --- Columna izquierda: Crear nuevo artículo ---
    create_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
    create_frame.grid(row=0, column=0, sticky="nsew", padx=5)
    main_frame.columnconfigure(0, weight=2) # La columna de creación es más ancha
    main_frame.rowconfigure(0, weight=1)

    Label(create_frame, text="Nuevo Artículo", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)
    
    Label(create_frame, text="Título:", font=("Arial", 12), bg="#2f2f3f", fg="white").pack(anchor="w", pady=(10,0))
    title_entry = Entry(create_frame, font=("Arial", 12), width=50)
    title_entry.pack(fill="x", pady=5)
    
    Label(create_frame, text="Contenido:", font=("Arial", 12), bg="#2f2f3f", fg="white").pack(anchor="w", pady=(10,0))
    content_text = Text(create_frame, font=("Arial", 11), height=20, wrap="word")
    content_text.pack(fill="both", expand=True, pady=5)

    # --- Columna derecha: Lista de artículos existentes ---
    list_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
    list_frame.grid(row=0, column=1, sticky="nsew", padx=5)
    main_frame.columnconfigure(1, weight=1) # La columna de lista es más estrecha

    Label(list_frame, text="Mis Artículos", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)
    
    articles_listbox = Listbox(list_frame, font=("Arial", 11), bg="#3c3c4c", fg="white")
    articles_listbox.pack(fill="both", expand=True)

    # --- Funciones internas de la ventana del blog ---
    def refresh_articles():
        # Limpiar la lista actual
        articles_listbox.delete(0, 'end')
        # Obtener los artículos de la BD
        articles = get_user_articles(user_id)
        # Poblar la lista
        if articles:
            for article in articles:
                # article[1] es el título según tu función get_articles_by_user
                articles_listbox.insert('end', article[1])

    def publish_article():
        title = title_entry.get()
        content = content_text.get("1.0", "end-1c") # Obtener todo el texto del widget
        if not title or not content:
            messagebox.showerror("Error", "El título y el contenido no pueden estar vacíos.")
            return
        
        create_article(title, content, user_id)
        # Limpiar campos y refrescar la lista
        title_entry.delete(0, 'end')
        content_text.delete("1.0", 'end')
        refresh_articles()

    # Botón para publicar
    Button(create_frame, text="Publicar Artículo", command=publish_article, bg="#98c379", fg="white", font=("Arial", 12)).pack(pady=15)

    # Al cerrar esta ventana, volver a mostrar el menú principal
    def on_close():
        blog_win.destroy()
        root.deiconify()
    blog_win.protocol("WM_DELETE_WINDOW", on_close)

    # Cargar los artículos por primera vez al abrir la ventana
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
>>>>>>> b5da796a02062c19bb90cf4df7221bd204b00638:Proyecto Primer Parcial/Base de datos sql/python/login/logincontinker.py
