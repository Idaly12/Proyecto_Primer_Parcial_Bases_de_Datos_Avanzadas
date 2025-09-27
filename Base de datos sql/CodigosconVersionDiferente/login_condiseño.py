import customtkinter as ctk
from PIL import Image
from pathlib import Path

# --- Configuración de la ventana principal ---
app = ctk.CTk()
app.title("Login de Usuario")
app.geometry("800x600")
app.resizable(False, False)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --- Fuentes ---
main_font = ("Arial", 14)
bold_font = ("Arial", 14, "bold")
title_font = ("Arial", 28, "bold")
icon_font = ("Arial", 20, "bold")

# --- Cargar la imagen de fondo (MÉTODO DEFINITIVO) ---
bg_image = None # Inicializamos bg_image para que siempre exista
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
    IMAGE_PATH = SCRIPT_DIR / "Imagenes" / "adorno.png"
    
    bg_image_data = Image.open(IMAGE_PATH)
    
    # --- ¡INICIO DEL BLOQUE MODIFICADO PARA REDIMENSIONAR PROPORCIONALMENTE! ---
    # Obtener el ancho y alto originales de la imagen
    original_width, original_height = bg_image_data.size
    
    # Definir el nuevo ancho deseado (ajusta este valor para hacerla más grande o pequeña)
    new_width = 150  # Por ejemplo, 180 píxeles de ancho
    
    # Calcular la nueva altura manteniendo la relación de aspecto
    if original_height > 0: # Evitar división por cero
        aspect_ratio = original_width / original_height
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = new_width # Fallback si la altura original es 0
    
    # Crear la imagen de CTkImage con el nuevo tamaño proporcional
    bg_image = ctk.CTkImage(light_image=bg_image_data, size=(new_width, new_height))
    # --- ¡FIN DEL BLOQUE MODIFICADO! ---

except Exception as e:
    print(f"ERROR: No se pudo cargar la imagen. Revisa la ruta: {IMAGE_PATH}")
    print(f"Detalle del error: {e}")
    bg_image = None


# Frame principal blanco que ocupa toda la ventana
main_frame = ctk.CTkFrame(app, fg_color="white", corner_radius=0)
main_frame.pack(fill="both", expand=True)

# Etiqueta para mostrar la imagen de fondo en la parte superior
if bg_image:
    bg_label = ctk.CTkLabel(main_frame, image=bg_image, text="")
    bg_label.place(relx=0.5, rely=0, anchor="n") 

# --- Contenedor del Formulario (para centrarlo) ---
form_container = ctk.CTkFrame(main_frame, fg_color="transparent")
form_container.place(relx=0.5, rely=0.6, anchor="center") # <-- 2. MÁS ESPACIO ARRIBA
# --- Widgets dentro del contenedor ---
welcome_label = ctk.CTkLabel(form_container, text="Welcome back", font=title_font, text_color="black")
welcome_label.pack(pady=(20, 5))

login_prompt_label = ctk.CTkLabel(form_container, text="Login to your account", font=main_font, text_color="gray")
login_prompt_label.pack(pady=(0, 25))

email_entry = ctk.CTkEntry(form_container, placeholder_text="correo@ejemplo.com", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
email_entry.pack(fill="x", pady=8)

password_entry = ctk.CTkEntry(form_container, placeholder_text="••••••••", show="•", font=main_font, border_width=2, corner_radius=10, height=40, width=300)
password_entry.pack(fill="x", pady=8)

options_frame = ctk.CTkFrame(form_container, fg_color="transparent")
options_frame.pack(fill="x", pady=10)

remember_me_check = ctk.CTkCheckBox(options_frame, text="remember me", font=main_font, text_color="gray")
remember_me_check.pack(side="left")

forgot_password_button = ctk.CTkButton(options_frame, text="Forgot Password?", font=bold_font, fg_color="transparent", text_color="#FFC107", hover=False)
forgot_password_button.pack(side="right")

login_button = ctk.CTkButton(form_container, text="Log In", font=bold_font, fg_color="#FFC107", hover_color="#E0A800", corner_radius=10, height=40)
login_button.pack(fill="x", pady=15)

or_label = ctk.CTkLabel(form_container, text="OR", font=main_font, text_color="gray")
or_label.pack()

social_buttons_frame = ctk.CTkFrame(form_container, fg_color="transparent")
social_buttons_frame.pack(pady=10)

google_button = ctk.CTkButton(social_buttons_frame, text="G", font=icon_font, width=50, height=50, fg_color="white", text_color="black", border_width=1, border_color="lightgray", hover_color="#F0F0F0")
google_button.pack(side="left", padx=10)
facebook_button = ctk.CTkButton(social_buttons_frame, text="f", font=icon_font, width=50, height=50, fg_color="white", text_color="black", border_width=1, border_color="lightgray", hover_color="#F0F0F0")
facebook_button.pack(side="left", padx=10)
apple_button = ctk.CTkButton(social_buttons_frame, text="", font=icon_font, width=50, height=50, fg_color="white", text_color="black", border_width=1, border_color="lightgray", hover_color="#F0F0F0")
apple_button.pack(side="left", padx=10)

app.mainloop()