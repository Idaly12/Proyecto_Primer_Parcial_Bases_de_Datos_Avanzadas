import customtkinter as ctk
from PIL import Image
from pathlib import Path
from tkinter import messagebox

# Importamos las funciones de base de datos y la app principal
# Asumimos que create_user ahora solo espera 3 argumentos y user_exists debe devolver 5
from ConexionBDD import user_exists, create_user 
from artCategorias_diseño import BlogApp

class AuthWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.master = master
        self.title("Blogs de Recetas")
        self.geometry("800x600")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)

        self.main_font = ("Arial", 14)
        self.bold_font = ("Arial", 14, "bold")
        self.title_font = ("Arial", 28, "bold")

        self._load_images()
        self._setup_ui()

    def _load_images(self):
        images_path = Path(__file__).parent / "Imagenes"
        print("--- Depurando Rutas de Imágenes ---")
        print(f"Ruta completa para adorno.png: {images_path / 'adorno.png'}")
        print("------------------------------------")
        
        self.login_logo = self._load_image_with_retry(images_path / "adorno.png", (150, 150), mode="fit")
        self.background_image = self._load_image_with_retry(images_path / "fondo.png", (400, 600), mode="cover")

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1, minsize=400)
        main_frame.grid_columnconfigure(1, weight=1, minsize=400)
        main_frame.grid_rowconfigure(0, weight=1)

        if self.background_image:
            image_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
            image_frame.grid(row=0, column=1, sticky="nsew")
            ctk.CTkLabel(image_frame, text="", image=self.background_image).pack(fill="both", expand=True)
        
        self.login_frame = self._create_login_frame(main_frame)
        self.register_frame = self._create_register_frame(main_frame)

        self.show_login_frame()

    def _create_login_frame(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        if self.login_logo:
            ctk.CTkLabel(container, text="", image=self.login_logo).pack(pady=(0, 5))
        ctk.CTkLabel(container, text="Bienvenido", font=self.title_font, text_color="black").pack(pady=(25, 10))
        ctk.CTkLabel(container, text="Inicia sesión en tu cuenta", font=self.main_font, text_color="gray").pack(pady=(0, 25))

        self.login_email_entry = ctk.CTkEntry(container, placeholder_text="Correo electrónico", font=self.main_font, width=300, height=40)
        self.login_email_entry.pack(fill="x", pady=8)
        self.login_password_entry = ctk.CTkEntry(container, placeholder_text="Contraseña", show="•", font=self.main_font, width=300, height=40)
        self.login_password_entry.pack(fill="x", pady=8)

        ctk.CTkButton(container, text="Iniciar Sesión", font=self.bold_font, command=self.handle_login, height=40).pack(fill="x", pady=15)
        ctk.CTkButton(container, text="Regístrate Aquí", font=self.bold_font, fg_color="transparent", text_color="#007BFF", hover=False, command=self.show_register_frame).pack()
        return frame

    # *** REVERSIÓN: Quitamos el campo de clave de administrador del registro ***
    def _create_register_frame(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        if self.login_logo:
            ctk.CTkLabel(container, text="", image=self.login_logo).pack(pady=(0, 5))
        ctk.CTkLabel(container, text="Crea tu Cuenta", font=self.title_font, text_color="black").pack(pady=(15, 5))

        self.register_username_entry = ctk.CTkEntry(container, placeholder_text="Nombre de Usuario", font=self.main_font, width=300, height=40)
        self.register_username_entry.pack(fill="x", pady=5)
        self.register_email_entry = ctk.CTkEntry(container, placeholder_text="Correo electrónico", font=self.main_font, width=300, height=40)
        self.register_email_entry.pack(fill="x", pady=5)
        self.register_password_entry = ctk.CTkEntry(container, placeholder_text="Contraseña", show="•", font=self.main_font, width=300, height=40)
        self.register_password_entry.pack(fill="x", pady=5)
        self.register_confirm_password_entry = ctk.CTkEntry(container, placeholder_text="Confirmar Contraseña", show="•", font=self.main_font, width=300, height=40)
        self.register_confirm_password_entry.pack(fill="x", pady=5)
        
        # El padding se ajusta al eliminar el campo de administrador
        ctk.CTkButton(container, text="Registrarse", font=self.bold_font, command=self.handle_register, height=40).pack(fill="x", pady=15) 
        ctk.CTkButton(container, text="Iniciar Sesión Aquí", font=self.bold_font, fg_color="transparent", text_color="#007BFF", hover=False, command=self.show_login_frame).pack()
        return frame

    # *** FUNCIÓN CLAVE: Verificación de Login y Lanzamiento ***
    # En AuthWindow.py (la clase AuthWindow)

    # En AuthWindow.py (la clase AuthWindow)
    # --- FUNCIÓN CORREGIDA DENTRO DE LA CLASE ---
    def handle_login(self):
        email = self.login_email_entry.get()
        password = self.login_password_entry.get()
        
        # user_exists debe devolver 5 elementos: (ID, NAME, EMAIL, PASS, IS_ADMIN)
        user_data = user_exists(email) 
        
        # user_data[3] es la contraseña, user_data[0] es el user_id
        if user_data and password == user_data[3]:
            db_user_id = user_data[0]
            
            # Ocultamos la ventana de login
            self.withdraw() 
            
            # Lanzamos BlogApp. BlogApp se encarga de llamar a is_user_admin(db_user_id) 
            # para verificar si el botón de Admin debe mostrarse.
            blog_app = BlogApp(master=self.master, user_id=db_user_id)
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    # --- FUNCIÓN DE REGISTRO CORREGIDA DENTRO DE LA CLASE ---
    def handle_register(self):
        username = self.register_username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        confirm = self.register_confirm_password_entry.get()
        
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "Todos los campos principales son obligatorios.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        
        # Usando la versión de 3 argumentos para el registro, ya que quitamos la clave de admin
        # NOTA: Debes asegurar que tu procedimiento ADD_USER en SQL acepte 3 argumentos o que 
        # tu función create_user en Python solo llame al procedimiento con 3 argumentos en este caso.
        if create_user(username, email, password): 
            messagebox.showinfo("Éxito", "Usuario registrado. Ahora puedes iniciar sesión.")
            self.show_login_frame()
        else:
            # create_user maneja el error de DB
            pass 
    
    def show_login_frame(self):
        self.register_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="nsew", padx=20)

    def show_register_frame(self):
        self.login_frame.grid_forget()
        self.register_frame.grid(row=0, column=0, sticky="nsew", padx=20)

    def _load_image_with_retry(self, filename, size, mode="fit"):
        try:
            pil_image = Image.open(filename)
            pil_image.thumbnail(size, Image.LANCZOS)
            return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
        except:
            return None