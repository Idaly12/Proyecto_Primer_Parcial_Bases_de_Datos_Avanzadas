import oracledb
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
console = Console()


DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1"



#Configuración de la conexión Idaly
#DB_USER = "proyecto"
#DB_PASS = "proyecto"
#DB_DSN = "localhost/XEPDB1" 

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


    """Muestra el menú de opciones después de un login exitoso."""
    user_id = user_data[0]
    username = user_data[1]

    while True:
        console.print(Panel(f"[bold yellow]Bienvenido, {username}![/bold yellow]\n\n1. Ver mis artículos\n2. Crear nuevo artículo\n3. Actualizar un artículo\n4. Eliminar un artículo\n5. Volver al menú principal (Logout)", title="Menú de Artículos"))
        opcion = Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5"])

        if opcion == "1":
            # Función para ver artículos (la haremos después)
            console.print("[cyan]Funcionalidad 'Ver mis artículos' pendiente.[/cyan]")
            pass
        elif opcion == "2":
            # --- INICIO DE LA INTEGRACIÓN ---
            console.print(Panel("[bold cyan]NUEVO ARTÍCULO[/bold cyan]", expand=False))
            
            # Pedimos los datos al usuario
            article_title = Prompt.ask("Título del artículo")
            
            # Pedimos el contenido del artículo. El usuario puede escribir varias líneas.
            # Termina de escribir cuando presiona Ctrl+D (en Linux/Mac) o Ctrl+Z (en Windows).
            console.print("Escribe el contenido de tu artículo (Ctrl+D o Ctrl+Z para finalizar):")
            article_content_lines = []
            try:
                while True:
                    line = input()
                    article_content_lines.append(line)
            except EOFError:
                pass # Se presionó la combinación de teclas para finalizar

            article_content = "\n".join(article_content_lines)

            # Validamos que el contenido no esté vacío
            if not article_content.strip():
                console.print("[bold red]El contenido del artículo no puede estar vacío.[/bold red]")
            else:
                # Llamamos a la función para crear el artículo, pasándole el user_id
                create_article(article_title, article_content, user_id)
            # --- FIN DE LA INTEGRACIÓN ---
            
        elif opcion == "3":
            console.print("[cyan]Funcionalidad 'Actualizar un artículo' pendiente.[/cyan]")
            pass
        elif opcion == "4":
            console.print("[cyan]Funcionalidad 'Eliminar un artículo' pendiente.[/cyan]")
            pass
        elif opcion == "5":
            console.print("[bold yellow]Cerrando sesión...[/bold yellow]")
            break