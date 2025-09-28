import customtkinter as ctk
import oracledb
from tkinter import messagebox
from datetime import datetime
from perfil_usuario import ProfileWindow 

# Configuración oracle/paloma
DB_USER = "bases"
DB_PASS = "bases"
DB_DSN = "localhost/XEPDB1"

# --- Funciones de Base de Datos ---

def get_connection():
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except oracledb.DatabaseError as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

def get_user_info(user_id):
    conn = get_connection()
    if not conn: return "Usuario Desconocido"
    cur = conn.cursor()
    try:
        cur.execute("SELECT username FROM users WHERE user_id = :1", [user_id])
        result = cur.fetchone()
        return result[0] if result else "Usuario Desconocido"
    finally:
        if cur: cur.close()
        if conn: conn.close()

def create_article(title, text, user_id):
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.callproc("add_article", [title, text, user_id])
        conn.commit()
        messagebox.showinfo("Éxito", "Receta publicada correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al publicar receta: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_articles():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.article_date DESC
        """)
        results = cur.fetchall()
        articles = []
        for row in results:
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": row[4],
                "user_id": row[5]
            })
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar recetas: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_articles_by_category(category_id):
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            JOIN article_categories ac ON a.article_id = ac.article_id
            WHERE ac.category_id = :1
            ORDER BY a.article_date DESC
        """, [category_id])
        results = cur.fetchall()
        articles = []
        for row in results:
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": row[4],
                "user_id": row[5]
            })
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al filtrar recetas: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def get_comments(article_id):
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT name, url, text, created_at
            FROM comments
            WHERE article_id = :id
            ORDER BY created_at ASC
        """, {'id': article_id})
        comments = [{
            "username": row[0],
            "user_id": int(row[1]) if row[1] else None,
            "text": row[2].read() if hasattr(row[2], 'read') else row[2],
            "created_at": row[3].strftime('%d-%m-%Y %H:%M') if row[3] else ''
        } for row in cur.fetchall()]
        return comments
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_latest_article_id_by_user(user_id):
    conn = get_connection()
    if not conn: return None
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT article_id FROM articles
            WHERE user_id = :1
            ORDER BY article_date DESC
            FETCH FIRST 1 ROWS ONLY
        """, [user_id])
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_categories():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def associate_article_categories(article_id, category_ids):
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        for cat_id in category_ids:
            cur.callproc("add_article_category", [article_id, cat_id])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Asociación", f"No se pudo asociar la categoría: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_comment(article_id, user_id, text):
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.callproc("add_comment", [article_id, user_id, text])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", f"No se pudo añadir el comentario: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
# --- Interfaz ---

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class BlogApp(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.title("Blog de Recetas - GUI")
        self.geometry("1200x800")
        self.user_id = user_id
        self.upload_window = None
        self.profile_window = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_main_content_area()
        self.show_frame(self.articles_frame)
        self.load_articles()

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="white")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        logo_label = ctk.CTkLabel(self.header_frame, text="Blogs de Recetas", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color="#720F0F")
        logo_label.grid(row=0, column=0, padx=(30, 0), pady=15, sticky="w")

        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, padx=30, pady=15, sticky="e")

        my_username = get_user_info(self.user_id)
        profile_button = ctk.CTkButton(right_header_frame, text=f"Mi Perfil ({my_username})", command=lambda: self.open_profile_window(self.user_id))
        profile_button.pack(side="right", padx=(10, 0))

        self.upload_button = ctk.CTkButton(right_header_frame, text="Subir Receta →", command=self.open_upload_window, width=150, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.upload_button.pack(side="right")

    def _create_main_content_area(self):
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.content_container.grid(row=1, column=0, sticky="nsew")
        self.content_container.grid_columnconfigure(1, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        self._create_sidebar()
        self._create_articles_frame()
        self._create_article_detail_frame()

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self.content_container, width=250, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(30, 0), pady=30)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        category_title = ctk.CTkLabel(self.sidebar_frame, text="Categorías", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        category_title.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="w")
        self.load_sidebar_categories()

    def _create_articles_frame(self):
        self.articles_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")
        self.articles_frame.grid_columnconfigure(0, weight=1)
        self.articles_frame.grid_rowconfigure(1, weight=1)
        header_frame = ctk.CTkFrame(self.articles_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        title_insights = ctk.CTkLabel(header_frame, text="¿Qué vamos a cocinar hoy?", font=ctk.CTkFont(size=36, weight="bold"), anchor="w")
        title_insights.grid(row=0, column=0, sticky="w")
        subtitle_insights = ctk.CTkLabel(header_frame, text="Recetas y consejos de nuestros mejores usuarios.", font=ctk.CTkFont(size=18), text_color="gray50", anchor="w")
        subtitle_insights.grid(row=1, column=0, sticky="w", pady=(0, 15))
        self.scrollable_frame = ctk.CTkScrollableFrame(self.articles_frame, label_text="Últimas Recetas", label_font=ctk.CTkFont(size=14), fg_color="white")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def _create_article_detail_frame(self):
        self.article_detail_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")

    def show_frame(self, frame_to_show):
        self.articles_frame.grid_forget()
        self.article_detail_frame.grid_forget()
        frame_to_show.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

    def show_article_detail(self, article):
        self.show_frame(self.article_detail_frame)
        for widget in self.article_detail_frame.winfo_children():
            widget.destroy()

        self.article_detail_frame.grid_columnconfigure(0, weight=1)
        self.article_detail_frame.grid_rowconfigure(3, weight=2)
        self.article_detail_frame.grid_rowconfigure(8, weight=1)

        back_button = ctk.CTkButton(self.article_detail_frame, text="< Volver a las Recetas", command=lambda: self.show_frame(self.articles_frame))
        back_button.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        title_label = ctk.CTkLabel(self.article_detail_frame, text=article['title'], font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        
        author_frame = ctk.CTkFrame(self.article_detail_frame, fg_color="transparent")
        author_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        author_button = ctk.CTkButton(
            author_frame,
            text=f"Publicado por: {article.get('username', 'N/A')}",
            command=lambda uid=article.get('user_id'): self.open_profile_window(uid) if uid else None,
            fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0",
            font=ctk.CTkFont(size=12), anchor="w", height=10, width=10
        )
        author_button.pack(side="left")

        date_label = ctk.CTkLabel(author_frame, text=f" el {article.get('created_at', 'N/A')}", font=ctk.CTkFont(size=12))
        date_label.pack(side="left")

        content_textbox = ctk.CTkTextbox(self.article_detail_frame, font=ctk.CTkFont(size=14), wrap="word")
        content_textbox.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        content_textbox.insert("1.0", article['text'])
        content_textbox.configure(state="disabled")

        ctk.CTkLabel(self.article_detail_frame, text="Deja tu comentario:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        
        new_comment_entry = ctk.CTkTextbox(self.article_detail_frame, height=80, wrap="word")
        new_comment_entry.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        def post_new_comment():
            comment_text = new_comment_entry.get("1.0", "end-1c").strip()
            if not comment_text:
                messagebox.showwarning("Atención", "El comentario no puede estar vacío.", parent=self)
                return
            add_comment(article['id'], self.user_id, comment_text)
            new_comment_entry.delete("1.0", "end")
            messagebox.showinfo("Éxito", "Comentario publicado.", parent=self)
            self.show_article_detail(article)

        post_comment_button = ctk.CTkButton(self.article_detail_frame, text="Publicar Comentario", command=post_new_comment)
        post_comment_button.grid(row=6, column=0, padx=20, pady=10, sticky="e")

        ctk.CTkLabel(self.article_detail_frame, text="Comentarios", font=ctk.CTkFont(size=18, weight="bold")).grid(row=7, column=0, padx=20, pady=(20, 5), sticky="w")
        
        comments_frame = ctk.CTkScrollableFrame(self.article_detail_frame, label_text="Conversación")
        comments_frame.grid(row=8, column=0, padx=20, pady=5, sticky="nsew")
        
        comments = get_comments(article['id'])
        if not comments:
            ctk.CTkLabel(comments_frame, text="Aún no hay comentarios. ¡Sé el primero!", text_color="gray").pack(pady=10)
        else:
            for comment in comments:
                if comment.get('user_id'):
                    comment_user_button = ctk.CTkButton(
                        comments_frame,
                        text=f"{comment['username']} ({comment['created_at']}):",
                        command=lambda uid=comment['user_id']: self.open_profile_window(uid),
                        fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0",
                        font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
                    )
                    comment_user_button.pack(anchor="w", padx=5)
                else:
                    header_label = ctk.CTkLabel(comments_frame, text=f"{comment['username']} ({comment['created_at']}):")
                    header_label.pack(anchor="w", padx=5)

                comment_text_label = ctk.CTkLabel(comments_frame, text=comment['text'], wraplength=500, justify="left")
                comment_text_label.pack(anchor="w", padx=25, pady=(0, 10))

    def open_upload_window(self):
        if self.upload_window is None or not self.upload_window.winfo_exists():
            self.upload_window = ArticleUploader(self, user_id=self.user_id)
            self.upload_window.grab_set()
        else:
            self.upload_window.focus()

    def open_profile_window(self, user_id_to_view):
        if self.profile_window is None or not self.profile_window.winfo_exists():
            self.withdraw()
            self.profile_window = ProfileWindow(master=self, user_id_to_view=user_id_to_view, main_app=self)
        else:
            self.profile_window.focus()

    def load_sidebar_categories(self):
        for widget in self.sidebar_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
        
        all_button = ctk.CTkButton(self.sidebar_frame, text="Mostrar Todas", fg_color="#D32F2F", hover_color="#B71C1C", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", command=self.load_articles)
        all_button.grid(row=1, column=0, padx=0, pady=5, sticky="ew")

        categories = get_all_categories()
        if not categories:
            no_cat_label = ctk.CTkLabel(self.sidebar_frame, text="No hay categorías.", text_color="gray50", font=ctk.CTkFont(size=12, slant="italic"))
            no_cat_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            cat_button = ctk.CTkButton(self.sidebar_frame, text=cat_name, fg_color="transparent", text_color="gray30", hover_color="gray90", font=ctk.CTkFont(size=14), anchor="w", command=lambda cid=cat_id: self.filter_by_category(cid))
            cat_button.grid(row=i + 2, column=0, padx=0, pady=5, sticky="ew")

    def filter_by_category(self, category_id):
        articles_from_db = get_articles_by_category(category_id)
        self.display_articles(articles_from_db)
        self.show_frame(self.articles_frame)

    def load_articles(self):
        articles_from_db = get_all_articles()
        self.display_articles(articles_from_db)
        self.show_frame(self.articles_frame)

    def display_articles(self, articles_list):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not articles_list:
            no_articles_label = ctk.CTkLabel(self.scrollable_frame, text="No hay recetas para mostrar.", font=ctk.CTkFont(size=18), text_color="gray50")
            no_articles_label.pack(pady=50)
            return

        for i, article_data in enumerate(articles_list):
            self.create_article_card(self.scrollable_frame, article_data, i)

    def create_article_card(self, parent_frame, article, row_index):
        card = ctk.CTkFrame(parent_frame, corner_radius=0, fg_color="white")
        separator = ctk.CTkFrame(parent_frame, height=1, fg_color="gray90", corner_radius=0)
        
        if isinstance(parent_frame, ctk.CTkScrollableFrame):
            separator.pack(fill="x", pady=(20, 10), padx=10)
            card.pack(fill="x", pady=(10, 20), padx=10)
        else:
            separator.grid(row=row_index * 2, column=0, sticky="ew", pady=(20, 10))
            card.grid(row=row_index * 2 + 1, column=0, padx=0, pady=(10, 20), sticky="ew")

        card.grid_columnconfigure(0, weight=1)

        date_label = ctk.CTkLabel(card, text=article['created_at'], font=ctk.CTkFont(size=14, weight="bold"), text_color="gray50", anchor="w")
        date_label.grid(row=0, column=0, sticky="w")

        title_label = ctk.CTkLabel(card, text=article['title'], font=ctk.CTkFont(size=24, weight="bold"), anchor="w", justify="left")
        title_label.grid(row=1, column=0, pady=(0, 10), sticky="w")
        title_label.bind("<Button-1>", lambda event, art=article: self.show_article_detail(art))
        title_label.bind("<Enter>", lambda event: title_label.configure(cursor="hand2", text_color="#D32F2F"))
        title_label.bind("<Leave>", lambda event: title_label.configure(cursor="", text_color="black"))

        extract = (article['text'][:100] + '...') if len(article['text']) > 100 else article['text']
        extract_label = ctk.CTkLabel(card, text=extract, wraplength=800, text_color="gray40", anchor="w", justify="left")
        extract_label.grid(row=2, column=0, pady=(0, 10), sticky="w")

        author_button = ctk.CTkButton(
            card, text=f"por {article['username']}",
            command=lambda uid=article['user_id']: self.open_profile_window(uid),
            fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w", height=10, width=10
        )
        author_button.grid(row=3, column=0, sticky="w")

class ArticleUploader(ctk.CTkToplevel):
    def __init__(self, master, user_id):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.title("Subir Nueva Receta")
        self.geometry("700x550")
        self.grid_columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Nombre de la Receta:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.title_entry = ctk.CTkEntry(self, width=500)
        self.title_entry.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(self, text="Instrucciones:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.content_textbox = ctk.CTkTextbox(self, height=200)
        self.content_textbox.grid(row=3, column=0, padx=20, pady=(0, 15), sticky="nsew")

        ctk.CTkLabel(self, text="Categoría:", font=ctk.CTkFont(size=14)).grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.categories_data = get_all_categories()
        category_names = [name for id, name in self.categories_data]
        self.category_combobox = ctk.CTkComboBox(self, values=category_names)
        self.category_combobox.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        if category_names:
            self.category_combobox.set(category_names[0])

        self.publish_button = ctk.CTkButton(self, text="Subir al blog", command=self.publish_article)
        self.publish_button.grid(row=6, column=0, padx=20, pady=20)

    def publish_article(self):
        title = self.title_entry.get()
        content = self.content_textbox.get("1.0", "end-1c")
        selected_category_name = self.category_combobox.get()

        if not title or not content.strip():
            messagebox.showerror("Error", "El título y el contenido no pueden estar vacíos.", parent=self)
            return
        if not selected_category_name:
            messagebox.showerror("Error", "Debes seleccionar una categoría.", parent=self)
            return

        create_article(title, content, self.user_id)
        new_article_id = get_latest_article_id_by_user(self.user_id)

        if new_article_id:
            selected_category_id = next((cat_id for cat_id, cat_name in self.categories_data if cat_name == selected_category_name), None)
            if selected_category_id:
                associate_article_categories(new_article_id, [selected_category_id])
        else:
            messagebox.showwarning("Advertencia", "Se creó la receta, pero no se pudo asociar la categoría.", parent=self)

        self.master.load_articles()
        self.master.load_sidebar_categories()
        self.destroy()

if __name__ == "__main__":
    print("Este archivo es un módulo. Ejecuta Login_y_diseño.py para iniciar.")