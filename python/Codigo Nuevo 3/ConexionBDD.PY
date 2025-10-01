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

# --- Funciones de Usuarios y Administración ---
def is_user_admin(user_id):
    """Verifica si el usuario es administrador (IS_ADMIN = 1)."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute('SELECT "IS_ADMIN" FROM "USERS" WHERE "USER_ID" = :1', [user_id])
        result = cur.fetchone()
        
        return result[0] == 1 if result else False
    except Exception as e:
        print(f"Error al verificar rol de admin: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_user_info(user_id):
    """Obtiene el nombre de un usuario a partir de su ID."""
    conn = get_connection()
    if not conn: return "Usuario Desconocido"
    cur = conn.cursor()
    try:
        cur.execute('SELECT "USERNAME" FROM "USERS" WHERE "USER_ID" = :1', [user_id])
        result = cur.fetchone()
        return result[0] if result else "Usuario Desconocido"
    finally:
        if cur: cur.close()
        if conn: conn.close()

def user_exists(email):
    """Verifica si un usuario existe por su email y retorna sus datos, incluyendo IS_ADMIN."""
    conn = get_connection()
    if conn is None: return None
    cur = conn.cursor()
    try:
        # CORRECCIÓN CLAVE: Seleccionamos 5 columnas (IS_ADMIN es la última)
        cur.execute('SELECT "USER_ID", "USERNAME", "EMAIL", "PASSWORD", "IS_ADMIN" FROM "USERS" WHERE "EMAIL" = :email', {"email": email})
        return cur.fetchone() # Ahora devuelve una tupla de 5 elementos
    finally:
        if cur: cur.close()
        if conn: conn.close()

# ...
def create_user(username, email, password, admin_key=None):
    """Crea un nuevo usuario, pasando opcionalmente la clave de administrador."""
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password, admin_key])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# **** NUEVAS FUNCIONES DE ADMINISTRACIÓN ****

def update_admin_password(user_id, new_password):
    """Permite al administrador cambiar su propia contraseña."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute('UPDATE "USERS" SET "PASSWORD" = :new_pass WHERE "USER_ID" = :uid', 
                    {"new_pass": new_password, "uid": user_id})
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al cambiar la contraseña: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def demote_user(user_id):
    """Cambia el rol de un usuario de Administrador (1) a Normal (0)."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute('UPDATE "USERS" SET "IS_ADMIN" = 0 WHERE "USER_ID" = :uid', [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al degradar usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def promote_user(user_id):
    """Cambia el rol de un usuario de Normal (0) a Administrador (1)."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute('UPDATE "USERS" SET "IS_ADMIN" = 1 WHERE "USER_ID" = :uid', [user_id])
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al promover usuario: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()
        
def get_all_users():
    """Obtiene una lista de todos los usuarios (ID, Nombre, Email, Rol)."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT "USER_ID", "USERNAME", "EMAIL", "IS_ADMIN" FROM "USERS" ORDER BY "USERNAME"')
        return cur.fetchall() 
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener lista de usuarios: {e}")
        return []
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
             SELECT a."ARTICLE_ID", a."TITLE", a."ARTICLE_TEXT", a."ARTICLE_DATE", u."USERNAME", u."USER_ID"
             FROM "ARTICLES" a JOIN "USERS" u ON a."USER_ID" = u."USER_ID"
             ORDER BY a."ARTICLE_DATE" DESC
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
             SELECT a."ARTICLE_ID", a."TITLE", a."ARTICLE_TEXT", a."ARTICLE_DATE", u."USERNAME", u."USER_ID"
             FROM "ARTICLES" a JOIN "USERS" u ON a."USER_ID" = u."USER_ID"
             WHERE a."USER_ID" = :1 ORDER BY a."ARTICLE_DATE" DESC
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
             SELECT a."ARTICLE_ID", a."TITLE", a."ARTICLE_TEXT", a."ARTICLE_DATE", u."USERNAME", u."USER_ID"
             FROM "ARTICLES" a
             JOIN "USERS" u ON a."USER_ID" = u."USER_ID"
             JOIN "ARTICLE_CATEGORIES" ac ON a."ARTICLE_ID" = ac."ARTICLE_ID"
             WHERE ac."CATEGORY_ID" = :1 ORDER BY a."ARTICLE_DATE" DESC
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
            SELECT "ARTICLE_ID" FROM "ARTICLES"
            WHERE "USER_ID" = :1 ORDER BY "ARTICLE_DATE" DESC
            FETCH FIRST 1 ROWS ONLY
        """, [user_id])
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- Funciones de Categorías (CRUD por Admin) ---
def get_all_categories():
    conn = get_connection()
    if not conn: 
        return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT "CATEGORY_ID", "CATEGORY_NAME" FROM "CATEGORIES" ORDER BY "CATEGORY_NAME"')
        
        categories = cur.fetchall()
        return categories
    except Exception as e:
        messagebox.showerror("Error de Base de Datos (Categorías)", f"Fallo al obtener categorías: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def add_category(category_name):
    """Agrega una nueva categoría llamando al procedimiento almacenado."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.callproc("add_category", [category_name])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Error al insertar categoría: {e}")
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

# --- Funciones de Comentarios ---
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

def get_comments(article_id):
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("""
             SELECT c."NAME", c."USER_ID", c."TEXT", c."CREATED_AT"
             FROM "COMMENTS" c WHERE c."ARTICLE_ID" = :id ORDER BY c."CREATED_AT" ASC
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

# --- Funciones de Etiquetas (Tags) ---
def get_all_tags():
    """Obtiene todas las etiquetas de la base de datos."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT "TAG_ID", "TAG_NAME" FROM "TAGS" ORDER BY "TAG_NAME"')
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def associate_article_tags(article_id, tag_ids):
    """Asocia un artículo con una lista de IDs de etiquetas."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        for tag_id in tag_ids:
            cur.callproc("add_article_tag", [article_id, tag_id])
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error de Asociación", f"No se pudo asociar la etiqueta: {e}")
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
             SELECT t."TAG_NAME"
             FROM "TAGS" t
             JOIN "ARTICLE_TAGS" at ON t."TAG_ID" = at."TAG_ID"
             WHERE at."ARTICLE_ID" = :1
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
             SELECT a."ARTICLE_ID", a."TITLE", a."ARTICLE_TEXT", a."ARTICLE_DATE", u."USERNAME", u."USER_ID"
             FROM "ARTICLES" a
             JOIN "USERS" u ON a."USER_ID" = u."USER_ID"
             JOIN "ARTICLE_TAGS" at ON a."ARTICLE_ID" = at."ARTICLE_ID"
             WHERE at."TAG_ID" = :1 ORDER BY a."ARTICLE_DATE" DESC
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
        messagebox.showerror("Error", f"Error al filtrar recetas por etiqueta: {e}")
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()