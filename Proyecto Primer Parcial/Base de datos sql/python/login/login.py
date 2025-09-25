import oracledb
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
console = Console()
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
        console.print("[green]Usuario creado correctamente[/green]")
    except Exception as e:
        console.print(f"[red]Error al crear usuario: {e}[/red]")
    finally:
        cur.close()
        conn.close()

def login_user():
    """Login de usuario existente"""
    console.print(Panel("[bold cyan]LOGIN[/bold cyan]", expand=False))
    correo = Prompt.ask("Ingresa tu email: ")

    if "@gmail.com" not in correo:
        console.print("[red]No es un correo válido[/red]")
        return

    usuario = user_exists(correo)
    if usuario:
        password_input = getpass.getpass("Ingresa la contraseña: ")
        if password_input == usuario[3]:  # contraseña
            console.print(f"[green]Hola {usuario[1]}[/green]")
        else:
            console.print("[red]Contraseña incorrecta[/red]")
    else:
        console.print("[red]Usuario no encontrado[/red]")

def register_user():
    """Registro de nuevo usuario"""
    console.print(Panel("[bold magenta]REGISTRO[/bold magenta]", expand=False))
    nombre = Prompt.ask("Ingresa tu nombre: ")
    correo = Prompt.ask("Ingresa tu email: ")

    if "@gmail.com" not in correo:
        console.print("[red]Correo no válido[/red]")
        return

    usuario = user_exists(correo)
    if usuario:
        console.print("[yellow]Email ya existente[/yellow]")
    else:
        password = getpass.getpass("Crea tu contraseña: ")
        password_confirmar = getpass.getpass("Confirma la contraseña: ")
        if password != password_confirmar:
            console.print("[red]Las contraseñas no son iguales[/red]")
            return
        create_user(nombre, correo, password)

def main_menu():
    while True:
        console.print(Panel("[bold blue]MENÚ PRINCIPAL[/bold blue]\n1. Login\n2. Registrarse\n3. Salir", expand=False))
        opcion = Prompt.ask("Selecciona una opción", choices=["1", "2", "3"])
        
        if opcion == "1":
            login_user()
        elif opcion == "2":
            register_user()
        elif opcion == "3":
            console.print("[bold green] saliendo [bold green]")
            
            break
if __name__ == "__main__":
    main_menu()

