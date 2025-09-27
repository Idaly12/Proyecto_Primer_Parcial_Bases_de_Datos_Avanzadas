import customtkinter as ctk
from PIL import Image
from pathlib import Path
import tkinter.messagebox as messagebox
import oracledb 

# Conexion

# Configuración oracle/paloma
DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1" 

# Configuración oracle/idaly
#DB_USER = "proyectob"
#DB_PASS = "proyectob"
#DB_DSN = "localhost/XEPDB1" 

def get_connection():   
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    except Exception as e:
        print(f"ERROR DE CONEXIÓN A ORACLE: {e}")
        messagebox.showerror("Error de Conexión")
        return None

def user_exists(email):
    conn = get_connection()
    if conn is None: return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id, username, email, password FROM users WHERE email = :email", {"email": email})
        row = cur.fetchone()
        return row
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def create_user(username, email, password):
    conn = get_connection()
    if conn is None: return False
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        return True
    except Exception as e:
        if "unique constraint" in str(e).lower():
            messagebox.showerror("El correo electrónico ya está registrado.")
        else:
            messagebox.showerror(f"Error al crear usuario: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def handle_login():
    email = login_email_entry.get()
    password = login_password_entry.get()
    
    if not email or not password:
        messagebox.showerror("Por favor, introduce tu correo electrónico y contraseña.")
        return
        
    user_data = user_exists(email)
    
    if user_data:
        db_stored_password = user_data[3]
        if password == db_stored_password: 
            messagebox.showinfo("Éxito", f"¡Bienvenido, {user_data[1]}! Inicio de Sesión Exitoso.")
            # Aquí se añadiría la lógica para abrir la ventana principal de la aplicación.
            return

    messagebox.showerror("Correo electrónico o contraseña incorrectos.")

def handle_register():
    """Maneja el evento de registro de nuevo usuario."""
    username = register_username_entry.get()
    email = register_email_entry.get()
    password = register_password_entry.get()
    confirm_password = register_confirm_password_entry.get() 
    
    if not username or not email or not password or not confirm_password:
        messagebox.showerror("Todos los campos son obligatorios.")
        return
        
    if password != confirm_password:
        messagebox.showerror("Las contraseñas no coinciden.")
        return
        
    if create_user(username, email, password):
        show_login_frame()
        register_username_entry.delete(0, 'end')
        register_email_entry.delete(0, 'end')
        register_password_entry.delete(0, 'end')
        register_confirm_password_entry.delete(0, 'end')

def show_register_frame():
    """Muestra el frame de Registro y oculta el de Login."""
    login_frame.grid_forget()
    register_frame.grid(row=0, column=0, sticky="nsew", padx=20) 

def show_login_frame():
    """Muestra el frame de Login y oculta el de Registro."""
    register_frame.grid_forget()
    login_frame.grid(row=0, column=0, sticky="nsew", padx=20) 

# Configuración de la Ventana e Interfaz

app = ctk.CTk()
app.title("Blogs de Recetas")
app.geometry("800x600")
app.resizable(False, False)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

main_font = ("Arial", 14)
bold_font = ("Arial", 14, "bold")
title_font = ("Arial", 28, "bold")

login_logo = None
background_image = None

def load_image_with_retry(filename, target_size, mode="fit"):
    paths_to_try = [
        Path(__file__).parent / filename,
        Path(__file__).parent.parent / filename,
        Path(__file__).parent / "Imagenes" / filename,
        Path(__file__).parent.parent / "Imagenes" / filename,
        Path(filename) 
    ]

    for p in paths_to_try:
        try:
            pil_image = Image.open(p)
            original_width, original_height = pil_image.size
            target_width, target_height = target_size

            if mode == "cover":
              
                ratio_w = target_width / original_width
                ratio_h = target_height / original_height
                
                if ratio_w > ratio_h:
                    new_width = target_width
                    new_height = int(original_height * ratio_w)
                else:
                    new_height = target_height
                    new_width = int(original_width * ratio_h)
                
                resized_pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                
                left = (new_width - target_width) / 2
                top = (new_height - target_height) / 2
                right = (new_width + target_width) / 2
                bottom = (new_height + target_height) / 2
                resized_pil_image = resized_pil_image.crop((left, top, right, bottom))

            elif mode == "fit":
                pil_image.thumbnail(target_size, Image.LANCZOS)
                resized_pil_image = pil_image 

            else: 
                resized_pil_image = pil_image.resize(target_size, Image.LANCZOS)

            return ctk.CTkImage(light_image=resized_pil_image, dark_image=resized_pil_image, size=target_size)
        except FileNotFoundError:
            continue 
        except Exception as e:
            break 

    return None

image_size = (150, 150)
login_logo = load_image_with_retry("adorno.png", image_size, mode="fit") 

fondo_size = (400, 600) 
background_image = load_image_with_retry("fondo.png", fondo_size, mode="cover")


# Frame principal usa GRID para las dos columnas
main_frame = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
main_frame.pack(fill="both", expand=True)

# Configuramos dos columnas en main_frame: Col 0 (400px), Col 1 (400px)
main_frame.grid_columnconfigure(0, weight=1, minsize=400) 
main_frame.grid_columnconfigure(1, weight=1, minsize=400) 
main_frame.grid_rowconfigure(0, weight=1)

# --- Contenedor de la Imagen de Fondo (Columna 1, lado derecho) ---
if background_image:
    image_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
    image_frame.grid(row=0, column=1, sticky="nsew") 
    
    # El Label se expande completamente
    ctk.CTkLabel(image_frame, text="", image=background_image).grid(row=0, column=0, sticky="nsew")
    image_frame.grid_rowconfigure(0, weight=1)
    image_frame.grid_columnconfigure(0, weight=1)
else:
    # Si la imagen falla, muestra un color de fondo gris claro en su lugar
    ctk.CTkFrame(main_frame, fg_color="#E0E0E0", corner_radius=0).grid(row=0, column=1, sticky="nsew")


login_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
login_container = ctk.CTkFrame(login_frame, fg_color="transparent")
login_container.place(relx=0.5, rely=0.5, anchor="center") 

if login_logo:
    ctk.CTkLabel(login_container, text="", image=login_logo).pack(pady=(0, 5))

ctk.CTkLabel(login_container, text="Bienvenido", font=title_font, text_color="black").pack(pady=(25, 10))
ctk.CTkLabel(login_container, text="Inicia sesión en tu cuenta", font=main_font, text_color="gray").pack(pady=(0, 25))

# Campos de entrada de Login
login_email_entry = ctk.CTkEntry(login_container, placeholder_text="Correo electrónico", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
login_email_entry.pack(fill="x", pady=8)
login_password_entry = ctk.CTkEntry(login_container, placeholder_text="Contraseña", show="•", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
login_password_entry.pack(fill="x", pady=8)

ctk.CTkButton(login_container, text="Iniciar Sesión", font=bold_font, fg_color="#FF5733", hover_color="#D32F2F", corner_radius=10, height=40, command=handle_login).pack(fill="x", pady=15)

ctk.CTkLabel(login_container, text="¿No tienes una cuenta?", font=main_font, text_color="gray").pack(pady=10)
ctk.CTkButton(login_container, text="Regístrate Aquí", font=bold_font, fg_color="transparent", text_color="#007BFF", hover=False, command=show_register_frame).pack()


# --- B. Frame de REGISTRO 

register_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
register_container = ctk.CTkFrame(register_frame, fg_color="transparent")
register_container.place(relx=0.5, rely=0.5, anchor="center")

# Se añade el logo al frame de registro
if login_logo:
    ctk.CTkLabel(register_container, text="", image=login_logo).pack(pady=(0, 5))

ctk.CTkLabel(register_container, text="Crea tu Cuenta", font=title_font, text_color="black").pack(pady=(15, 5)) 
ctk.CTkLabel(register_container, text="Comparte tus recetas!", font=main_font, text_color="gray").pack(pady=(0, 15))

# Campos de entrada de Registro
register_username_entry = ctk.CTkEntry(register_container, placeholder_text="Nombre de Usuario", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
register_username_entry.pack(fill="x", pady=5) 
register_email_entry = ctk.CTkEntry(register_container, placeholder_text="Correo electrónico", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
register_email_entry.pack(fill="x", pady=5) 
register_password_entry = ctk.CTkEntry(register_container, placeholder_text="Contraseña", show="•", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
register_password_entry.pack(fill="x", pady=5)

register_confirm_password_entry = ctk.CTkEntry(register_container, placeholder_text="Confirmar Contraseña", show="•", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
register_confirm_password_entry.pack(fill="x", pady=5)

ctk.CTkButton(register_container, text="Registrarse", font=bold_font, fg_color="#FF5733", hover_color="#D32F2F", corner_radius=10, height=40, command=handle_register).pack(fill="x", pady=(15, 15))

ctk.CTkLabel(register_container, text="¿Ya tienes una cuenta?", font=main_font, text_color="gray").pack(pady=5)
ctk.CTkButton(register_container, text="Iniciar Sesión Aquí", font=bold_font, fg_color="transparent", text_color="#007BFF", hover=False, command=show_login_frame).pack()


show_login_frame() 

app.mainloop()
