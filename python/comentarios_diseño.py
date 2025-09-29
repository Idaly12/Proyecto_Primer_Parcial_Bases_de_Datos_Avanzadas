import customtkinter as ctk
import oracledb
from tkinter import messagebox
from datetime import datetime

# --- Configuración de Conexión ---
DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1" 

CURRENT_USER_ID = 1 

# --- Funciones de Base de Datos ---

def get_connection():
    """Establece conexión con la base de datos Oracle."""
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except oracledb.DatabaseError as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

def create_article(title, text, user_id):
    """Llama al procedimiento para crear un nuevo artículo."""
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

def _process_articles_query(cursor):
    """Función auxiliar para leer resultados de artículos y procesar CLOBs."""
    results = cursor.fetchall()
    processed_articles = []
    for row in results:
        content_clob = row[2] 
        content_str = content_clob.read() if content_clob else ""
        processed_row = (row[0], row[1], content_str, row[3], row[4])
        processed_articles.append(processed_row)
    return processed_articles

def get_all_articles():
    """Obtiene todos los artículos de la base de datos."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username
            FROM articles a 
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.article_date DESC
        """)
        return _process_articles_query(cur)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar recetas: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_articles_by_category(category_id):
    """Obtiene todos los artículos que pertenecen a una categoría específica."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            JOIN article_categories ac ON a.article_id = ac.article_id
            WHERE ac.category_id = :1
            ORDER BY a.article_date DESC
        """, [category_id])
        return _process_articles_query(cur)
    except Exception as e:
        messagebox.showerror("Error", f"Error al filtrar recetas: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def get_latest_article_id_by_user(user_id):
    """Obtiene el ID del último artículo creado por un usuario."""
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
    """Obtiene todas las categorías de la base de datos."""
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
    """Asocia un artículo con una o más categorías."""
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

def get_username_by_id(user_id):
    """Obtiene el nombre de un usuario a partir de su ID."""
    conn = get_connection()
    if not conn: return "Usuario Desconocido"
    cur = conn.cursor()
    try:
        cur.execute("SELECT username FROM users WHERE user_id = :1", [user_id])
        result = cur.fetchone()
        return result[0] if result else "Usuario Desconocido"
    except Exception:
        return "Usuario Desconocido"
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_comment(name, url, article_id, user_id):
    """Añade un nuevo comentario a un artículo."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.callproc("add_comment", [name, url, article_id, user_id])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Error al añadir comentario: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_comments(article_id):
    """Obtiene todos los comentarios de un artículo."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        result_cursor = cur.callfunc("get_comments_by_article", oracledb.DB_TYPE_CURSOR, [article_id])
        return result_cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar comentarios: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- INTERFAZ GRÁFICA ---

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class BlogApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blog de Recetas - GUI")
        self.geometry("1200x800")
        
        self.current_article_id = None
        
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
        
        self.upload_button = ctk.CTkButton(self.header_frame, text="Subir Receta →", command=self.open_upload_window, width=150, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.upload_button.grid(row=0, column=1, padx=30, pady=15, sticky="e")

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
        
        search_secondary = ctk.CTkEntry(header_frame, placeholder_text="Buscar receta...", width=300, corner_radius=8, fg_color="gray95", border_width=0)
        search_secondary.grid(row=2, column=0, sticky="w")
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.articles_frame, label_text="Últimas Recetas", label_font=ctk.CTkFont(size=14), fg_color="white")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def _create_article_detail_frame(self):
        self.article_detail_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")
        self.article_detail_frame.grid_columnconfigure(0, weight=1)
        self.article_detail_frame.grid_rowconfigure(1, weight=1) 
        self.article_detail_frame.grid_rowconfigure(3, weight=0)

        back_button = ctk.CTkButton(self.article_detail_frame, text="< Volver a Recetas",
                                    command=lambda: self.show_frame(self.articles_frame),
                                    fg_color="transparent", text_color="gray30", hover_color="gray90")
        back_button.grid(row=0, column=0, sticky="w", padx=0, pady=(0, 20))
        
        self.detail_content_frame = ctk.CTkScrollableFrame(self.article_detail_frame, fg_color="transparent")
        self.detail_content_frame.grid(row=1, column=0, sticky="nsew")
        self.detail_content_frame.grid_columnconfigure(0, weight=1)

        comments_title = ctk.CTkLabel(self.article_detail_frame, text="Comentarios", font=ctk.CTkFont(size=20, weight="bold"))
        comments_title.grid(row=2, column=0, sticky="w", pady=(20, 10))
        
        self.comments_list_frame = ctk.CTkScrollableFrame(self.article_detail_frame, fg_color="transparent")
        self.comments_list_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        self.comments_list_frame.grid_columnconfigure(0, weight=1)
        self.article_detail_frame.grid_rowconfigure(3, weight=1)

        add_comment_frame = ctk.CTkFrame(self.article_detail_frame, fg_color="transparent")
        add_comment_frame.grid(row=4, column=0, sticky="ew")
        add_comment_frame.grid_columnconfigure(0, weight=1)

        self.comment_entry = ctk.CTkEntry(add_comment_frame, placeholder_text="Escribe un comentario...")
        self.comment_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        post_comment_button = ctk.CTkButton(add_comment_frame, text="Publicar", width=100, command=self._post_comment)
        post_comment_button.grid(row=0, column=1, sticky="e")

    def show_frame(self, frame_to_show):
        self.articles_frame.grid_forget()
        self.article_detail_frame.grid_forget()
        frame_to_show.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
    
    def show_article_detail(self, article):
        self.current_article_id = article['id']
        
        for widget in self.detail_content_frame.winfo_children():
            widget.destroy()

        title_label = ctk.CTkLabel(self.detail_content_frame, text=article['title'], font=ctk.CTkFont(size=32, weight="bold"), wraplength=800, justify="left")
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 15))

        meta_text = f"Publicado el {article['date']} por {article['author']}"
        meta_label = ctk.CTkLabel(self.detail_content_frame, text=meta_text, font=ctk.CTkFont(size=14), text_color="gray50", justify="left")
        meta_label.grid(row=1, column=0, sticky="w", pady=(0, 20))

        separator = ctk.CTkFrame(self.detail_content_frame, height=2, fg_color="gray90")
        separator.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        content_label = ctk.CTkLabel(self.detail_content_frame, text=article['content'], font=ctk.CTkFont(size=16), wraplength=800, justify="left", anchor="nw")
        content_label.grid(row=3, column=0, sticky="w")
        
        self._load_comments()
        self.show_frame(self.article_detail_frame)
    
    def _load_comments(self):
        """Carga y muestra los comentarios con el nuevo diseño de burbuja."""
        for widget in self.comments_list_frame.winfo_children():
            widget.destroy()
        
        if self.current_article_id is None:
            return

        comments = get_comments(self.current_article_id)
        
        if not comments:
            no_comments_label = ctk.CTkLabel(self.comments_list_frame, text="Aún no hay comentarios. ¡Sé el primero!", text_color="gray50")
            no_comments_label.pack(pady=20)
            return

        for i, comment_tuple in enumerate(comments):
            comment_text = comment_tuple[1]
            user_id = comment_tuple[3]
            author_name = get_username_by_id(user_id)
            
            comment_bubble = ctk.CTkFrame(self.comments_list_frame, corner_radius=15, fg_color="gray92")
            comment_bubble.grid(row=i, column=0, sticky="ew", pady=(0, 10))
            comment_bubble.grid_columnconfigure(1, weight=1)

            profile_icon = ctk.CTkLabel(comment_bubble, text="👤", font=ctk.CTkFont(size=24))
            profile_icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")

            author_label = ctk.CTkLabel(comment_bubble, text=author_name, font=ctk.CTkFont(size=14, weight="bold"))
            author_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 2))

            comment_label = ctk.CTkLabel(comment_bubble, text=comment_text, wraplength=700, justify="left", anchor="w")
         
            comment_label.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

    def _post_comment(self):
        """Publica el nuevo comentario y refresca la lista."""
        comment_text = self.comment_entry.get()
        if not comment_text.strip():
            messagebox.showwarning("Aviso", "El comentario no puede estar vacío.", parent=self.article_detail_frame)
            return
        
        if self.current_article_id is None:
            messagebox.showerror("Error", "No se ha seleccionado ningún artículo.", parent=self.article_detail_frame)
            return
            
        add_comment(comment_text, "", self.current_article_id, CURRENT_USER_ID)
        
        self.comment_entry.delete(0, 'end')
        self._load_comments()

    def load_sidebar_categories(self):
        """Carga las categorías y las muestra."""
        for widget in self.sidebar_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) or (isinstance(widget, ctk.CTkLabel) and "No hay" in widget.cget("text")):
                widget.destroy()

        all_button = ctk.CTkButton(self.sidebar_frame, text="Mostrar Todas",
                                   fg_color="#D32F2F", hover_color="#B71C1C",
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w", command=self.load_articles)
        all_button.grid(row=1, column=0, padx=0, pady=5, sticky="ew")

        categories = get_all_categories()
        
        if not categories:
            no_cat_label = ctk.CTkLabel(self.sidebar_frame, text="No hay categorías.",
                                        text_color="gray50",
                                        font=ctk.CTkFont(size=12, slant="italic"))
            no_cat_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            cat_button = ctk.CTkButton(self.sidebar_frame, text=cat_name, 
                                       fg_color="transparent", text_color="gray30", 
                                       hover_color="gray90", font=ctk.CTkFont(size=14), 
                                       anchor="w",
                                       command=lambda cat_id=cat_id: self.filter_by_category(cat_id))
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
            no_articles_label = ctk.CTkLabel(self.scrollable_frame, 
                                             text="No hay recetas en esta categoría.",
                                             font=ctk.CTkFont(size=18), text_color="gray50")
            no_articles_label.pack(pady=50)
            return

        for i, article_tuple in enumerate(articles_list):
            article_data = {
                "id": article_tuple[0],
                "title": article_tuple[1],
                "content": article_tuple[2],
                "extract": (article_tuple[2][:100] + '...') if len(article_tuple[2]) > 100 else article_tuple[2],
                "date": article_tuple[3].strftime("%b %d, %Y") if isinstance(article_tuple[3], datetime) else "N/A",
                "author": article_tuple[4],
                "tags": ["Receta", "Consejo"], 
                "time": "5 min lectura" 
            }
            self.create_article_card(self.scrollable_frame, article_data, i)

    def create_article_card(self, parent_frame, article, row_index):
        card = ctk.CTkFrame(parent_frame, corner_radius=0, fg_color="white")
        separator = ctk.CTkFrame(parent_frame, height=1, fg_color="gray90", corner_radius=0)
        separator.grid(row=row_index * 2, column=0, sticky="ew", pady=(20, 10))
        card.grid(row=row_index * 2 + 1, column=0, padx=0, pady=(10, 20), sticky="ew")
        
        card.grid_columnconfigure(0, weight=1)
        
        date_label = ctk.CTkLabel(card, text=article['date'], font=ctk.CTkFont(size=14, weight="bold"), text_color="gray50", anchor="w")
        date_label.grid(row=0, column=0, sticky="w")
        
        title_label = ctk.CTkLabel(card, text=article['title'], font=ctk.CTkFont(size=24, weight="bold"), anchor="w", justify="left", text_color="black")
        title_label.grid(row=1, column=0, pady=(0, 10), sticky="w")
        
        title_label.bind("<Button-1>", lambda event, art=article: self.show_article_detail(art))
        title_label.bind("<Enter>", lambda event: title_label.configure(cursor="hand2", text_color="#D32F2F"))
        title_label.bind("<Leave>", lambda event: title_label.configure(cursor="", text_color="black"))
        
        extract_label = ctk.CTkLabel(card, text=article['extract'], wraplength=800, text_color="gray40", anchor="w", justify="left")
        extract_label.grid(row=2, column=0, pady=(0, 10), sticky="w")
        tags_text = f"{' '.join(article['tags'])} | por {article['author']} | {article['time']}"
        meta_label = ctk.CTkLabel(card, text=tags_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1E90FF", anchor="w")
        meta_label.grid(row=3, column=0, sticky="w")

    def open_upload_window(self):
        if not (hasattr(self, 'toplevel_window') and self.toplevel_window.winfo_exists()):
            self.toplevel_window = ArticleUploader(self)
            self.toplevel_window.grab_set()
        else:
            self.toplevel_window.focus()

class ArticleUploader(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
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
        self.category_combobox = ctk.CTkComboBox(self, values=category_names if category_names else ["Sin categorías"])
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
            
        if not selected_category_name or selected_category_name == "Sin categorías":
            messagebox.showerror("Error", "Debes seleccionar una categoría válida.", parent=self)
            return

        create_article(title, content, CURRENT_USER_ID)
        
        new_article_id = get_latest_article_id_by_user(CURRENT_USER_ID)
        
        if new_article_id:
            selected_category_id = None
            for cat_id, cat_name in self.categories_data:
                if cat_name == selected_category_name:
                    selected_category_id = cat_id
                    break
            
            if selected_category_id:
                associate_article_categories(new_article_id, [selected_category_id])
        else:
            messagebox.showwarning("Advertencia", "Se creó la receta, pero no se pudo asociar la categoría automáticamente.", parent=self)

        self.master.load_articles()
        self.master.load_sidebar_categories() 
        self.destroy()

if __name__ == "__main__":
    app = BlogApp()
    app.mainloop()