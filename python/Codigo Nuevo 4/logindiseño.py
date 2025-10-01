import customtkinter as ctk
from PIL import Image
from pathlib import Path
from tkinter import messagebox
# Importar las funciones de la DB necesarias para autenticación y roles
from ConexionBDD import user_exists, create_user, is_user_admin 
# Importar las ventanas de la aplicación
from artCategorias_diseño import BlogApp 
from admin_diseño import AdminWindow 

class AuthWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.main_app_master = master
        self.title("Blogs de Recetas")
        self.geometry("800x600")
        self.resizable(False, False)

        # Si el usuario cierra esta ventana, toda la aplicación termina.
        self.protocol("WM_DELETE_WINDOW", self.main_app_master.destroy)

        self.main_font = ("Arial", 14)
        self.bold_font = ("Arial", 14, "bold")
        self.title_font = ("Arial", 28, "bold")

        self._load_images()
        self._setup_ui()
        self.grab_set()

    def handle_login(self):
        email = self.login_email_entry.get()
        password = self.login_password_entry.get()
        
        user_data = user_exists(email)
        
        if user_data and password == user_data[3]:
            db_user_id = user_data[0]
            
            self.grab_release()
            self.destroy()
            
            if is_user_admin(db_user_id):
                # Es Admin: Abrir Panel de Administración
                AdminWindow(master=self.main_app_master, user_id=db_user_id)
            else:
                # Es Usuario Normal: Abrir Blog App
                BlogApp(master=self.main_app_master, user_id=db_user_id)

        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    def _load_images(self):
        images_path = Path(__file__).parent / "Imagenes"
        ruta_adorno = images_path / "adorno.png"
        ruta_fondo = images_path / "fondo.png"
        self.login_logo = self._load_image_with_retry(ruta_adorno, (150, 150))
        self.background_image = self._load_image_with_retry(ruta_fondo, (400, 600))

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1, minsize=400)
        main_frame.grid_columnconfigure(1, weight=1, minsize=400)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Columna de la imagen de fondo
        if self.background_image:
            image_frame = ctk.CTkFrame(main_frame, fg_color="white")
            image_frame.grid(row=0, column=1, sticky="nsew")
            ctk.CTkLabel(image_frame, text="", image=self.background_image).pack(expand=True)
            
        self.login_frame = self._create_login_frame(main_frame)
        self.register_frame = self._create_register_frame(main_frame)
        self.show_login_frame()

    def show_login_frame(self):
        self.register_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="nsew", padx=20)

    def show_register_frame(self):
        self.login_frame.grid_forget()
        self.register_frame.grid(row=0, column=0, sticky="nsew", padx=20)

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
        
        ctk.CTkButton(container, text="Registrarse", font=self.bold_font, command=self.handle_register, height=40).pack(fill="x", pady=15)
        
        ctk.CTkButton(container, text="Iniciar Sesión Aquí", font=self.bold_font, fg_color="transparent", text_color="#007BFF", hover=False, command=self.show_login_frame).pack()
        return frame

    def handle_register(self):
        username = self.register_username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        confirm = self.register_confirm_password_entry.get()
        
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
            
        if create_user(username, email, password):
            messagebox.showinfo("Éxito", "Usuario registrado. Ahora puedes iniciar sesión.")
            self.show_login_frame()
            
    def _load_image_with_retry(self, filename, size):
        try:
            pil_image = Image.open(filename)
            return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
        except Exception as e:
            print(f"Error al cargar imagen {filename}: {e}")
            return None
