import oracledb

# Configuración de la conexión
DB_USER = "system"   #cambia aqui tu usuario y contrasena del sql para que jale 
DB_PASS = "123"
DB_DSN = "localhost/XEPDB1"   

def get_connection():
    """AQUI SE CONECTA CON EL SQL"""
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def user_exists(email):
    """VERIFICACION"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE email = :email", {"email": email})
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_user(name, email):
    """Crea un nuevo usuario"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        output_id = cur.var(oracledb.NUMBER)
        cur.callproc("blog_pkg.create_user", [name, email, output_id])
        conn.commit()
        print(f"Usuario creado")
        return output_id.getvalue()
    except Exception as e:
        print("Error al crear usuario", e)
    finally:
        cur.close()
        conn.close()

def login_user():
    """EL USUARIO YA EXISTE"""
    correo = input("Ingresa tu email: 1")

    if "@gmail.com" not in correo:
        print("no es un correo valido ")
        return

    usuario = user_exists(correo)
    if usuario:
        print(f"ola, {usuario[1]}")
    else:
        print("Usuario no encontrado. Primero debes registrarte.")

def register_user():
    """Registro de un nuevo usuario"""
    nombre = input("Ingresa tu nombre: ")
    correo = input("Ingresa tu email: ")

    if "@gmail.com" not in correo:
        print("correo no valido")
        return

    usuario = user_exists(correo)
    if usuario:
        print(f"email ya existente ")
    else:
        create_user(nombre, correo)

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
            print("Opción invalida")

if __name__ == "__main__":
    main_menu()
