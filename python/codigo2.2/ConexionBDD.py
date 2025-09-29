# database.py
import oracledb
from tkinter import messagebox
from datetime import datetime

# --- Configuración de Conexión ---
DB_USER = "proyecto"
DB_PASS = "proyecto"
DB_DSN = "localhost/XEPDB1"

def get_connection():
    """Establece conexión con la base de datos Oracle."""
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except oracledb.DatabaseError as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

# --- Funciones de Usuarios ---
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

def user_exists(email):
    """Verifica si un usuario existe por su email y retorna sus datos."""
    conn = get_connection()
    if conn is None: return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id, username, email, password FROM users WHERE email = :email", {"email": email})
        return cur.fetchone()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def create_user(username, email, password):
    """Crea un nuevo usuario llamando al procedimiento almacenado."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Artículos ---
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
            FROM articles a JOIN users u ON a.user_id = u.user_id
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

def get_articles_by_user(user_id):
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a JOIN users u ON a.user_id = u.user_id
            WHERE a.user_id = :1 ORDER BY a.article_date DESC
        """, [user_id])
        results = cur.fetchall()
        articles = []
        for row in results:
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            # Diccionario MODIFICADO para incluir el username
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": row[4],
                "user_id": row[5]
            })
        return articles
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar recetas del usuario: {e}")
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
            WHERE ac.category_id = :1 ORDER BY a.article_date DESC
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

def get_latest_article_id_by_user(user_id):
    conn = get_connection()
    if not conn: return None
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT article_id FROM articles
            WHERE user_id = :1 ORDER BY article_date DESC
            FETCH FIRST 1 ROWS ONLY
        """, [user_id])
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Categorías ---
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
        # Llama al nuevo procedimiento mejorado con 3 argumentos
        cur.callproc("add_comment", [article_id, user_id, text])
        conn.commit()
        messagebox.showinfo("Éxito", "Comentario publicado correctamente.")
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", f"No se pudo añadir el comentario: {e}")
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
            FROM comments WHERE article_id = :id ORDER BY created_at ASC
        """, {'id': article_id})
        return [{
            "username": row[0], "user_id": int(row[1]) if row[1] else None,
            "text": row[2].read() if hasattr(row[2], 'read') else row[2],
            "created_at": row[3].strftime('%d-%m-%Y %H:%M') if row[3] else ''
        } for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()