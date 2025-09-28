import oracledb
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, StringVar, Listbox, Text, Frame, Scrollbar, Canvas # --- CAMBIO: Se añaden Scrollbar y Canvas


# Configuración de la conexión Idaly
DB_USER = "proyecto"
DB_PASS = "proyecto"
DB_DSN = "localhost/XEPDB1"


# Configuración de la conexión Paloma
#DB_USER = "proyectob"
#DB_PASS = "proyectob"
#DB_DSN = "localhost/XEPDB1"

def get_connection():
    """Establece y retorna una conexión con la base de datos."""
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# --- Gestión de Usuarios ---
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

# --- Gestión de Artículos ---
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
        processed_articles = []
        for row in result_cursor:
            content_lob = row[3]
            content_str = content_lob.read() if content_lob else ""
            processed_articles.append((row[0], row[1], row[2], content_str))
        return processed_articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar artículos: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# --- Gestión de Categorías ---
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

# --- Gestión de Comentarios ---
def add_comment(name, url, article_id, user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_comment", [name, url, article_id, user_id])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Error al añadir comentario: {e}")
    finally:
        cur.close()
        conn.close()

def get_comments(article_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # --- CAMBIO: La función SQL ahora devuelve más datos (username)
        result_cursor = cur.callfunc("get_comments_by_article", oracledb.DB_TYPE_CURSOR, [article_id])
        return result_cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar comentarios: {e}")
        return []
    finally:
        cur.close()
        conn.close()

# ==============================================================================
# --- VENTANAS DE LA APLICACIÓN ---
# ==============================================================================

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
                # --- CAMBIO: Se pasa el ID del usuario actual para distinguir entre perfil propio y ajeno
                blog_window(root, usuario[0], usuario[1], usuario[0])
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def view_article_window(root, article_data, current_user_id):
    article_id, article_title, _, article_content = article_data

    win = Toplevel(root)
    win.title(article_title)
    win.geometry("700x650")
    win.configure(bg="#282c34")

    article_frame = Frame(win, bg="#2f2f3f", padx=10, pady=10)
    article_frame.pack(fill="x", padx=10, pady=10)
    Label(article_frame, text=article_title, font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(anchor="w")
    article_text_widget = Text(article_frame, font=("Arial", 11), height=8, wrap="word", bg="#2f2f3f", fg="white", relief="flat")
    article_text_widget.insert("1.0", article_content)
    article_text_widget.config(state="disabled")
    article_text_widget.pack(fill="x", pady=5)

    # --- CAMBIO: Se reemplaza Listbox por un Frame con scroll para poder añadir botones ---
    comments_outer_frame = Frame(win, bg="#282c34")
    comments_outer_frame.pack(fill="both", expand=True, padx=10, pady=5)
    Label(comments_outer_frame, text="Comentarios", font=("Arial", 14), bg="#282c34", fg="white").pack(anchor="w")
    
    canvas = Canvas(comments_outer_frame, bg="#3c3c4c", highlightthickness=0)
    scrollbar = Scrollbar(comments_outer_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="#3c3c4c")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # --- FIN DEL CAMBIO DE LISTBOX ---

    def refresh_comments():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        comments = get_comments(article_id)
        
        # --- CAMBIO: Nueva función para abrir el perfil de un usuario desde un comentario
        def show_user_profile(profile_user_id, profile_username):
            blog_window(root, profile_user_id, profile_username, current_user_id)

        if not comments:
            Label(scrollable_frame, text="No hay comentarios aún.", bg="#3c3c4c", fg="white").pack(anchor="w", padx=5, pady=5)
            return

        for comment in comments:
            # La nueva consulta SQL devuelve: comment_id, username, comment_text, user_id
            commenter_username = comment[1]
            comment_text = comment[2]
            commenter_id = comment[3]
            
            comment_frame = Frame(scrollable_frame, bg="#3c3c4c")
            comment_frame.pack(fill="x", pady=2, padx=5)

            # Botón clickeable con el nombre del usuario
            user_button = Button(
                comment_frame,
                text=commenter_username,
                font=("Arial", 10, "bold", "underline"),
                bg="#3c3c4c", fg="#61afef",
                relief="flat", cursor="hand2", anchor="w",
                command=lambda uid=commenter_id, uname=commenter_username: show_user_profile(uid, uname)
            )
            user_button.pack(side="left")

            # Texto del comentario
            Label(comment_frame, text=f": {comment_text}", font=("Arial", 10), bg="#3c3c4c", fg="white", anchor="w").pack(side="left")

    add_comment_frame = Frame(win, bg="#282c34")
    add_comment_frame.pack(fill="x", padx=10, pady=10)
    Label(add_comment_frame, text="Comentario:", bg="#282c34", fg="white").pack(anchor="w")
    comment_entry = Entry(add_comment_frame, font=("Arial", 11))
    comment_entry.pack(fill="x", ipady=4, pady=(0, 5))
    Label(add_comment_frame, text="URL (Opcional):", bg="#282c34", fg="white").pack(anchor="w")
    url_entry = Entry(add_comment_frame, font=("Arial", 11))
    url_entry.pack(fill="x", ipady=4)

    def post_comment():
        comment_text = comment_entry.get()
        url_text = url_entry.get()
        if comment_text:
            add_comment(comment_text, url_text, article_id, current_user_id)
            comment_entry.delete(0, 'end')
            url_entry.delete(0, 'end')
            refresh_comments()

    Button(add_comment_frame, text="Comentar", command=post_comment, bg="#61afef", fg="white").pack(pady=10)
    refresh_comments()

# --- CAMBIO: La firma de la función ahora distingue el perfil visitado del usuario logueado
def blog_window(root, profile_user_id, username, current_user_id):
    blog_win = Toplevel(root)
    blog_win.title(f"Blog de {username}")
    blog_win.geometry("900x600")
    blog_win.configure(bg="#282c34")

    main_frame = Frame(blog_win, bg="#282c34")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    main_frame.rowconfigure(0, weight=1)

    is_owner = profile_user_id == current_user_id

    # --- CAMBIO: El panel para crear artículos solo aparece si el usuario está viendo su propio perfil
    if is_owner:
        create_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
        create_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        main_frame.columnconfigure(0, weight=2)

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
            categories_listbox.insert('end', f"{cat[1]}")
    
    list_frame = Frame(main_frame, bg="#2f2f3f", padx=10, pady=10)
    # --- CAMBIO: La posición del panel de artículos depende de si se muestra el panel de creación
    if is_owner:
        list_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        main_frame.columnconfigure(1, weight=1)
        Label(list_frame, text="Mis Artículos", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)
    else:
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, columnspan=2)
        main_frame.columnconfigure(0, weight=1)
        Label(list_frame, text=f"Artículos de {username}", font=("Arial", 16, "bold"), bg="#2f2f3f", fg="white").pack(pady=10)

    articles_listbox = Listbox(list_frame, font=("Arial", 11), bg="#3c3c4c", fg="white")
    articles_listbox.pack(fill="both", expand=True)

    def refresh_articles():
        articles_listbox.delete(0, 'end')
        articles = get_user_articles(profile_user_id) # Usa el ID del perfil que se está viendo
        articles_listbox.articles_data = articles
        if articles:
            for article in articles:
                articles_listbox.insert('end', article[1])

    def on_article_select(event):
        selected_indices = articles_listbox.curselection()
        if not selected_indices: return
        selected_index = selected_indices[0]
        article_data = articles_listbox.articles_data[selected_index]
        view_article_window(root, article_data, current_user_id)
    
    def publish_article():
        title = title_entry.get()
        content = content_text.get("1.0", "end-1c")
        if not title or not content:
            messagebox.showerror("Error", "El título y el contenido no pueden estar vacíos.")
            return
        create_article(title, content, current_user_id) # El artículo lo crea el usuario logueado
        articles = get_user_articles(current_user_id)
        if not articles: return
        # Esto podría ser frágil, es mejor obtener el ID del artículo recién creado de otra forma, pero se mantiene por ahora.
        article_id = articles[-1][0] 
        selected_indices = categories_listbox.curselection()
        selected_ids = [all_categories[i][0] for i in selected_indices]
        associate_article_categories(article_id, selected_ids)
        title_entry.delete(0, 'end')
        content_text.delete("1.0", 'end')
        categories_listbox.selection_clear(0, 'end')
        refresh_articles()

    if is_owner:
        Button(create_frame, text="Publicar Artículo", command=publish_article, bg="#98c379", fg="white", font=("Arial", 12)).pack(pady=15)

    def on_close():
        blog_win.destroy()
        root.deiconify()

    articles_listbox.bind("<Double-1>", on_article_select)
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
    root.title("Gestión de Blog")
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