import customtkinter as ctk
import oracledb
from tkinter import messagebox

# --- Configuración y Conexión a la Base de Datos ---
DB_USER = "bases"
DB_PASS = "bases"
DB_DSN = "localhost/XEPDB1"

def get_connection():
    """Establece conexión con la base de datos Oracle."""
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except oracledb.DatabaseError as e:
        # CORRECCIÓN: Se ha quitado el 'parent=self' de esta línea
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

# --- Funciones Específicas del Perfil ---
def get_user_info(user_id):
    """Obtiene el nombre de un usuario a partir de su ID."""
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

def get_articles_by_user(user_id):
    """Obtiene todas las recetas publicadas por un usuario específico."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT article_id, title, article_text, article_date, user_id
            FROM articles
            WHERE user_id = :1
            ORDER BY article_date DESC
        """, [user_id])
        results = cur.fetchall()
        articles = []
        for row in results:
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0],
                "title": row[1],
                "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'),
                "user_id": row[4],
                "username": get_user_info(row[4])
            })
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar recetas del usuario: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Clase de la Interfaz del Perfil ---
class ProfileWindow(ctk.CTkToplevel):
    def __init__(self, master, user_id_to_view, main_app):
        super().__init__(master)
        self.title("Perfil de Usuario")
        self.geometry("1000x700")
        self.main_app = main_app
        self.user_id = user_id_to_view

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        back_button = ctk.CTkButton(self, text="< Volver al Blog", command=self.close_profile)
        back_button.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.username = get_user_info(self.user_id)
        username_label = ctk.CTkLabel(self, text=f"Recetas de {self.username}", font=ctk.CTkFont(size=32, weight="bold"))
        username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.articles_frame = ctk.CTkScrollableFrame(self, label_text="Publicaciones")
        self.articles_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.articles_frame.grid_columnconfigure(0, weight=1)

        self.load_user_articles()

        self.protocol("WM_DELETE_WINDOW", self.close_profile)
        self.grab_set()

    def load_user_articles(self):
        """Carga y muestra las tarjetas de las recetas del usuario."""
        articles = get_articles_by_user(self.user_id)
        if not articles:
            no_articles_label = ctk.CTkLabel(self.articles_frame, text="Este usuario aún no ha publicado nada.", font=ctk.CTkFont(size=18), text_color="gray50")
            no_articles_label.pack(pady=50)
            return

        for i, article in enumerate(articles):
            self.main_app.create_article_card(self.articles_frame, article, i)

    def close_profile(self):
        """Cierra la ventana de perfil y muestra la ventana principal de nuevo."""
        self.grab_release()
        self.main_app.deiconify()
        self.destroy()