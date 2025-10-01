import customtkinter as ctk
from tkinter import messagebox
# Importamos las funciones necesarias directamente (como en tu código original)
from ConexionBDD import get_user_info, get_articles_by_user

class ProfileWindow(ctk.CTkToplevel):
    """
    Ventana flotante utilizada para mostrar el perfil de un usuario, incluyendo
    sus artículos publicados.
    """
    def __init__(self, master, user_id_to_view, main_app):
        super().__init__(master=master)
        
        # Ocultamos la ventana principal cuando se abre el perfil
        master.withdraw() 
        
        self.title("Perfil de Usuario")
        self.geometry("1000x700")
        self.main_app = main_app
        self.user_id = user_id_to_view

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Botón de regreso: Cierra esta ventana y muestra la principal (main_app)
        back_button = ctk.CTkButton(self, text="← Volver al Blog", command=self.close_profile, 
                                     fg_color="#D32F2F", hover_color="#B71C1C", corner_radius=8)
        back_button.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.username = get_user_info(self.user_id)
        username_label = ctk.CTkLabel(self, text=f"Recetas de {self.username}", 
                                     font=ctk.CTkFont(size=32, weight="bold"))
        username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # 2. Marco Scrollable para los artículos
        self.articles_frame = ctk.CTkScrollableFrame(self, label_text="Publicaciones", fg_color="white")
        self.articles_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.articles_frame.grid_columnconfigure(0, weight=1)

        self.load_user_articles()
        
        # Manejo de cierre de ventana para restaurar la principal
        self.protocol("WM_DELETE_WINDOW", self.close_profile)
        self.grab_set()

    def load_user_articles(self):
        """Carga y muestra los artículos publicados por el usuario."""
        
        # Limpiar frame antes de cargar
        for widget in self.articles_frame.winfo_children():
            widget.destroy()
            
        articles = get_articles_by_user(self.user_id)
        
        if not articles:
            no_articles_label = ctk.CTkLabel(self.articles_frame, text="Este usuario aún no ha publicado nada.", 
                                             font=ctk.CTkFont(size=18))
            no_articles_label.pack(pady=50)
            return

        for i, article in enumerate(articles):
            # Usamos el método de la app principal para crear las tarjetas
            self.main_app.create_article_card(self.articles_frame, article, i)

    def close_profile(self):
        """Cierra la ventana de perfil y restaura la ventana principal del blog."""
        self.grab_release()
        self.main_app.deiconify() # Muestra la ventana principal
        self.destroy()
