import oracledb
import getpass

# Configuración de la conexión
DB_USER = "proyecto"
DB_PASS = "proyecto"
DB_DSN = "localhost/XEPDB1"

def get_connection():
    """Conexión con Oracle"""
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def user_exists(email):
    """Verifica si un usuario existe por email"""
    conn = get_connection()
    cur = conn.cursor()
    # Seleccionamos todas las columnas relevantes
    cur.execute("SELECT user_id, username, email, password FROM users WHERE email = :email", {"email": email})
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row  # None si no existe

def create_user(username, email, password):
    """Crea un nuevo usuario usando el procedimiento add_user"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        print("Usuario creado correctamente")
    except Exception as e:
        print("Error al crear usuario:", e)
    finally:
        cur.close()
        conn.close()

def login_user():
    """Login de usuario existente"""
    correo = input("Ingresa tu email: ")

    if "@gmail.com" not in correo:
        print("No es un correo válido")
        return

    usuario = user_exists(correo)
    if usuario:
        password_input = getpass.getpass("Ingresa la contraseña: ")
        if password_input == usuario[3]:  # contraseña
            print(f"Hola {usuario[1]}")
        else:
            print("Contraseña incorrecta")
    else:
        print("Usuario no encontrado")

def register_user():
    """Registro de nuevo usuario"""
    nombre = input("Ingresa tu nombre: ")
    correo = input("Ingresa tu email: ")

    if "@gmail.com" not in correo:
        print("Correo no válido")
        return

    usuario = user_exists(correo)
    if usuario:
        print("Email ya existente")
    else:
        password = getpass.getpass("Crea tu contraseña: ")
        password_confirmar = getpass.getpass("Confirma la contraseña: ")
        if password != password_confirmar:
            print("Las contraseñas no son iguales")
            return
        create_user(nombre, correo, password)

def main_menu():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Login")
        print("2. Registrarse")
        print("3. Salir")
        opcion = input("Selecciona una opción (1-3): ")

        if opcion == "1":
            login_user()
        elif opcion == "2":
            register_user()
        elif opcion == "3":
            break
        else:
            print("Opción inválida")

if __name__ == "__main__":
    main_menu()
