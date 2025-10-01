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

# ----------------------------------
# --- FUNCIONES DE USUARIOS (CRUD) ---
# ----------------------------------

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
        # Se asume que el procedimiento add_user maneja el rol de administrador
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_users():
    """Obtiene la lista completa de usuarios con su ID, nombre, email y rol de admin."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT user_id, username, email, is_admin
            FROM users
            ORDER BY username
        """)
        return cur.fetchall()
    except Exception as e:
        print(f"Error al cargar la lista de usuarios para admin: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

# -----------------------------------
# --- FUNCIONES DE ARTÍCULOS (CRUD) ---
# -----------------------------------

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
        
def get_articles_by_tag(tag_id):
    """Obtiene artículos filtrados por una etiqueta (tag)."""
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
        messagebox.showerror("Error", f"Error al filtrar recetas por tag: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_tags_for_article(article_id):
    """Obtiene los nombres de los tags asociados a un artículo específico."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.tag_name FROM tags t
            JOIN article_tags at ON t.tag_id = at.tag_id
            WHERE at.article_id = :1
            ORDER BY t.tag_name
        """, [article_id])
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al obtener tags para el artículo {article_id}: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def associate_article_tags(article_id, tag_ids):
    """Asocia múltiples tags a un artículo llamando al procedimiento almacenado."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        for tag_id in tag_ids:
            # Llama al procedimiento que creaste en Oracle: add_article_tag
            cur.callproc("add_article_tag", [article_id, tag_id]) 
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Asociación", f"No se pudo asociar la etiqueta: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()


# --- FUNCIONES DE ADMINISTRACIÓN FALTANTES ---

def update_admin_password(user_id, new_password):
    """
    Actualiza la contraseña de un usuario (asumiendo que solo se usa para el administrador).
    Requiere que el procedimiento almacenado 'update_user_password' exista en Oracle.
    """
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        # Debes asegurarte de que este procedimiento exista en Oracle:
        cur.callproc("update_user_password", [user_id, new_password])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Contraseña", f"Error al actualizar contraseña: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def promote_user(user_id):
    """Promueve un usuario al rol de administrador (IS_ADMIN = 1)."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        # Ejecuta la actualización directamente en SQL (o usa un procedimiento si lo creaste)
        cur.execute("UPDATE users SET is_admin = 1 WHERE user_id = :1", [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Rol", f"Error al promover usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def demote_user(user_id):
    """Degrada un usuario al rol normal (IS_ADMIN = 0)."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        # Ejecuta la actualización directamente en SQL (o usa un procedimiento si lo creaste)
        cur.execute("UPDATE users SET is_admin = 0 WHERE user_id = :1", [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Rol", f"Error al degradar usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# -----------------------------------
# --- FUNCIONES DE COMENTARIOS (CRUD) ---
# -----------------------------------

def add_comment(article_id, user_id, text):
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
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


# ----------------------------------
# --- FUNCIONES DE ADMINISTRACIÓN ---
# ----------------------------------

def is_user_admin(user_id):
    """Verifica si un usuario es administrador (IS_ADMIN = 1)."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT is_admin FROM users WHERE user_id = :1", [user_id])
        result = cur.fetchone()
        return result[0] == 1 if result else False
    except Exception as e:
        print(f"Error al verificar rol de administrador: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def admin_add_category(category_name):
    """Llama al procedimiento almacenado para agregar una nueva categoría."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("add_category", [category_name])
        conn.commit()
        return True
    except Exception as e:
        # Nota: El procedimiento almacenado puede lanzar un error -20005
        messagebox.showerror("Error de Admin", f"Error al insertar categoría: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ----------------------------------
# --- FUNCIONES DE CATEGORÍAS (CRUD) ---
# ----------------------------------

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

# --------------------------------
# --- FUNCIONES DE ETIQUETAS (TAGS) ---
# --------------------------------

def get_all_tags():
    """Obtiene todos los tags disponibles (necesario para la sidebar)."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
        return cur.fetchall()
    except Exception as e:
        print(f"Error al cargar tags: {e}") 
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()
