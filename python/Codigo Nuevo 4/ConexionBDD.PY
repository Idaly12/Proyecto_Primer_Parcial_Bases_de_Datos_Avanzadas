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
# --- FUNCIONES DE USUARIOS ---
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
    """
    Obtiene la lista completa de usuarios.
    Utiliza el procedimiento 'get_all_users' de Oracle.
    """
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        # Llamada a la función de Oracle que retorna el cursor
        r_cursor = cur.callfunc("get_all_users", oracledb.DB_TYPE_CURSOR, [])
        return r_cursor.fetchall()
    except Exception as e:
        print(f"Error al cargar la lista de usuarios para admin: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
# --- NUEVAS FUNCIONES DE ADMINISTRACIÓN DE USUARIOS ---

def is_user_admin(user_id):
    """
    Verifica si un usuario es administrador (IS_ADMIN = 1).
    Esta función estaba faltando y causó el ImportError.
    """
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

def update_admin_password(user_id, new_password):
    """Actualiza la contraseña de un usuario llamando al procedimiento 'update_user_password'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
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
    """Promueve un usuario al rol de administrador (IS_ADMIN = 1) usando el procedimiento 'promote_user'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("promote_user", [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Rol", f"Error al promover usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def demote_user(user_id):
    """Degrada un usuario al rol normal (IS_ADMIN = 0) usando el procedimiento 'demote_user'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("demote_user", [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Rol", f"Error al degradar usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def delete_user(user_id):
    """Elimina un usuario y su contenido asociado usando el procedimiento 'delete_user'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("delete_user", [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Eliminación", f"Error al eliminar usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()


# -----------------------------------
# --- FUNCIONES DE ARTÍCULOS ---
# -----------------------------------

def add_article(title, text, user_id):
    """
    Crea un nuevo artículo y retorna el ID generado.
    Llama al procedimiento 'add_article'.
    """
    conn = get_connection()
    if not conn: return None
    cur = conn.cursor()
    try:
        cur.callproc("add_article", [title, text, user_id])
        conn.commit()
        
        latest_id = get_latest_article_id_by_user(user_id)
        return latest_id
    except Exception as e:
        messagebox.showerror("Error", f"Error al publicar receta: {e}")
        return None
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

def get_all_articles_for_admin():
    """
    Obtiene la lista de artículos para el panel de administración.
    Utiliza el procedimiento 'get_all_articles_for_admin' de Oracle.
    """
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        r_cursor = cur.callfunc("get_all_articles_for_admin", oracledb.DB_TYPE_CURSOR, [])
        
        results = []
        for row in r_cursor.fetchall():
            article_id, title, date, username = row
            formatted_date = date.strftime('%d-%m-%Y') if date else ''
            results.append((article_id, title, formatted_date, username))
        return results
    except Exception as e:
        print(f"Error al cargar la lista de artículos para admin: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_article_details(article_id):
    """
    Obtiene los detalles de un artículo para la edición.
    Utiliza el procedimiento 'get_article_details' de Oracle.
    """
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        r_cursor = cur.callfunc("get_article_details", oracledb.DB_TYPE_CURSOR, [article_id])
        results = r_cursor.fetchall()
        
        # Lee article_text
        detailed_results = []
        for row in results:
            content = row[2].read() if hasattr(row[2], 'read') else row[2]
            detailed_results.append((row[0], row[1], content, row[3], row[4], row[5]))
        
        return detailed_results
    except Exception as e:
        print(f"Error al obtener detalles del artículo: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def update_article(article_id, title, text):
    """Actualiza un artículo existente usando el procedimiento 'update_article'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("update_article", [article_id, title, text])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Error al actualizar artículo: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def delete_article(article_id):
    """Elimina un artículo y sus relaciones usando el procedimiento 'delete_article'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("delete_article", [article_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Eliminación", f"Error al eliminar artículo: {e}")
        return False
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


# ----------------------------------
# --- FUNCIONES DE CATEGORÍAS (CRUD) ---
# ----------------------------------

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
        messagebox.showerror("Error de Admin", f"Error al insertar categoría: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_categories():
    """Obtiene todas las categorías utilizando la función de Oracle."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        # Llamada a la función de Oracle
        r_cursor = cur.callfunc("get_all_categories", oracledb.DB_TYPE_CURSOR, [])
        return r_cursor.fetchall()
    except Exception as e:
        print(f"Error al cargar categorías: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def update_category(category_id, new_name):
    """Actualiza una categoría existente usando el procedimiento 'update_category'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("update_category", [category_id, new_name])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Error al actualizar categoría: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def delete_category(category_id):
    """Elimina una categoría y sus relaciones usando el procedimiento 'delete_category'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("delete_category", [category_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Eliminación", f"Error al eliminar categoría. Podría tener relaciones activas: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
# --------------------------------
# --- FUNCIONES DE ETIQUETAS (TAGS) ---
# --------------------------------

def add_tag(tag_name):
    """Agrega una nueva etiqueta usando el procedimiento 'add_tag'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("add_tag", [tag_name])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Creación", f"Error al insertar etiqueta: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_tags():
    """Obtiene todos los tags disponibles utilizando la función de Oracle 'get_all_tags'."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        # Llamada a la función de Oracle
        r_cursor = cur.callfunc("get_all_tags", oracledb.DB_TYPE_CURSOR, [])
        return r_cursor.fetchall()
    except Exception as e:
        print(f"Error al cargar tags: {e}") 
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def update_tag(tag_id, new_name):
    """Actualiza una etiqueta existente usando el procedimiento 'update_tag'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("update_tag", [tag_id, new_name])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Error al actualizar etiqueta: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def delete_tag(tag_id):
    """Elimina una etiqueta y sus relaciones usando el procedimiento 'delete_tag'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("delete_tag", [tag_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Eliminación", f"Error al eliminar etiqueta. Podría tener relaciones activas: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# -----------------------------------
# --- FUNCIONES DE COMENTARIOS (CRUD) ---
# -----------------------------------

def get_all_comments_for_admin():
    """
    Obtiene todos los comentarios para moderación.
    Utiliza el procedimiento 'get_all_comments_for_admin' de Oracle.
    """
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        # Llamada a la función de Oracle
        r_cursor = cur.callfunc("get_all_comments_for_admin", oracledb.DB_TYPE_CURSOR, [])
        
        results = []
        for row in r_cursor.fetchall():
            # 0: id, 1: name, 2: text, 3: title, 4: date
            comment_text = row[2].read() if hasattr(row[2], 'read') else row[2]
            created_at = row[4].strftime('%d-%m-%Y %H:%M') if row[4] else ''
            results.append((row[0], row[1], comment_text, row[3], created_at))
        return results
    except Exception as e:
        print(f"Error al obtener comentarios para admin: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def delete_comment(comment_id):
    """Elimina un comentario usando el procedimiento 'delete_comment'."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("delete_comment", [comment_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de Eliminación", f"Error al eliminar comentario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- FUNCIONES DE ASOCIACIÓN ---
def associate_article_categories(article_id, category_id):
    """Asocia un artículo con una categoría (simplificado para el admin panel)."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM article_categories WHERE article_id = :1", [article_id])
        cur.callproc("add_article_category", [article_id, category_id])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Asociación", f"No se pudo asociar la categoría: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
def associate_article_tags(article_id, tag_ids):
    """Asocia múltiples tags a un artículo llamando al procedimiento almacenado."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM article_tags WHERE article_id = :1", [article_id])
        
        for tag_id in tag_ids:
            cur.callproc("add_article_tag", [article_id, tag_id]) 
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Asociación", f"No se pudo asociar la etiqueta: {e}")
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
            SELECT name, user_id, text, created_at
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