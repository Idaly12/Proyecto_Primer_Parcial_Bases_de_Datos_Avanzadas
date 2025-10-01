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
        # Usamos messagebox aquí porque es un error crítico que impide que la app funcione
        messagebox.showerror("Error de Conexión Crítico", f"No se pudo conectar a la base de datos: {e}")
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
        cur.execute("SELECT user_id, password FROM users WHERE email = :1", [email])
        return cur.fetchone()
    except Exception as e:
        print(f"Error al verificar si el usuario existe: {e}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def create_user(username, email, password):
    """Crea un nuevo usuario en la base de datos."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password) VALUES (:1, :2, :3)", [username, email, password])
        conn.commit()
        return True
    except oracledb.IntegrityError:
        messagebox.showerror("Error de Registro", "El nombre de usuario o el correo electrónico ya existen.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Artículos (Recetas) ---
def get_all_articles():
    """Obtiene todos los artículos ordenados por fecha."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    articles = []
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a JOIN users u ON a.user_id = u.user_id
            ORDER BY a.article_date DESC
        """)
        for row in cur.fetchall():
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": row[4],
                "user_id": row[5]
            })
    except Exception as e:
        print(f"Error al obtener todos los artículos: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return articles

def get_articles_by_user(user_id):
    """Obtiene todos los artículos de un usuario específico."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    articles = []
    try:
        cur.execute("""
            SELECT article_id, title, article_text, article_date
            FROM articles WHERE user_id = :1 ORDER BY article_date DESC
        """, [user_id])
        for row in cur.fetchall():
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": get_user_info(user_id),
                "user_id": user_id
            })
    except Exception as e:
        print(f"Error al obtener artículos por usuario: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return articles

def create_article(title, content, user_id):
    """Crea un nuevo artículo."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO articles (title, article_text, user_id) VALUES (:1, :2, :3)", [title, content, user_id])
        conn.commit()
    except Exception as e:
        print(f"Error al crear el artículo: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_latest_article_id_by_user(user_id):
    """Obtiene el ID del último artículo creado por un usuario."""
    conn = get_connection()
    if not conn: return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(article_id) FROM articles WHERE user_id = :1", [user_id])
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error al obtener el último ID de artículo: {e}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Comentarios ---
def get_comments(article_id):
    """Obtiene todos los comentarios de un artículo."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.comment_text, c.comment_date, u.username
            FROM comments c JOIN users u ON c.user_id = u.user_id
            WHERE c.article_id = :1 ORDER BY c.comment_date ASC
        """, [article_id])
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_comment(article_id, user_id, comment_text):
    """Añade un nuevo comentario a un artículo."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO comments (article_id, user_id, comment_text) VALUES (:1, :2, :3)", [article_id, user_id, comment_text])
        conn.commit()
    except Exception as e:
        print(f"Error al añadir comentario: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Categorías ---
def get_all_categories():
    """Obtiene todas las categorías."""
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
        cur.executemany("INSERT INTO article_categories (article_id, category_id) VALUES (:1, :2)", [(article_id, cat_id) for cat_id in category_ids])
        conn.commit()
    except Exception as e:
        print(f"Error al asociar categorías: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_articles_by_category(category_id):
    """Obtiene todos los artículos de una categoría específica."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    articles = []
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            JOIN article_categories ac ON a.article_id = ac.article_id
            WHERE ac.category_id = :1 ORDER BY a.article_date DESC
        """, [category_id])
        for row in cur.fetchall():
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            articles.append({
                "id": row[0], "title": row[1], "text": content,
                "created_at": row[3].strftime('%d-%m-%Y'), "username": row[4],
                "user_id": row[5]
            })
    except Exception as e:
        print(f"Error al obtener artículos por categoría: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return articles

# --- Funciones de Etiquetas (Tags) ---
def get_all_tags():
    """Obtiene todas las etiquetas."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def associate_article_tags(article_id, tag_ids):
    """Asocia un artículo con una o más etiquetas."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.executemany("INSERT INTO article_tags (article_id, tag_id) VALUES (:1, :2)", [(article_id, tag_id) for tag_id in tag_ids])
        conn.commit()
    except Exception as e:
        print(f"Error al asociar etiquetas: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_tags_for_article(article_id):
    """Obtiene las etiquetas de un artículo específico."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.tag_name FROM tags t
            JOIN article_tags at ON t.tag_id = at.tag_id
            WHERE at.article_id = :1
        """, [article_id])
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al obtener etiquetas del artículo: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_articles_by_tag(tag_id):
    """Obtiene todos los artículos asociados a una etiqueta específica."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            JOIN article_tags at ON a.article_id = at.article_id
            WHERE at.tag_id = :1 ORDER BY a.article_date DESC
        """, [tag_id])
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
        print(f"Error al obtener artículos por etiqueta: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

# >>>>> INICIO: NUEVAS FUNCIONES AÑADIDAS <<<<<

def get_tags_for_category(category_id):
    """Obtiene las etiquetas únicas para todos los artículos de una categoría específica."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT t.tag_id, t.tag_name
            FROM tags t
            JOIN article_tags at ON t.tag_id = at.tag_id
            JOIN article_categories ac ON at.article_id = ac.article_id
            WHERE ac.category_id = :1
            ORDER BY t.tag_name
        """, [category_id])
        return cur.fetchall()
    except Exception as e:
        print(f"Error al obtener etiquetas para la categoría: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_articles_by_category_and_tag(category_id, tag_id):
    """Obtiene todos los artículos que pertenecen a una categoría Y tienen una etiqueta específica."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.article_id, a.title, a.article_text, a.article_date, u.username, u.user_id
            FROM articles a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.article_id IN (
                SELECT ac.article_id FROM article_categories ac
                WHERE ac.category_id = :cat_id
            ) AND a.article_id IN (
                SELECT at.article_id FROM article_tags at
                WHERE at.tag_id = :tag_id
            )
            ORDER BY a.article_date DESC
        """, {'cat_id': category_id, 'tag_id': tag_id})
        
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
        # En lugar de messagebox, imprimimos el error en la consola
        print(f"Error al filtrar recetas por categoría y etiqueta: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

# >>>>> FIN: NUEVAS FUNCIONES AÑADIDAS <<<<<