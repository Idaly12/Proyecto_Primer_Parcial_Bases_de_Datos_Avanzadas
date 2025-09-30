# profile_view.py
import customtkinter as ctk
from tkinter import messagebox
# Importamos solo lo necesario de la base de datos
from ConexionBDD import get_user_info, get_articles_by_user

class ProfileWindow(ctk.CTkToplevel):
    def __init__(self, master, user_id_to_view, main_app):
        super().__init__(master=master)
        self.title("Perfil de Usuario")
        self.geometry("1000x700")
        self.main_app = main_app
        self.user_id = user_id_to_view

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        back_button = ctk.CTkButton(self, text="< Volver al Blog", command=self.close_profile)
        back_button.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.username = get_user_info(self.user_id)
        username_label = ctk.CTkLabel(self, text=f"Recetas de {self.username}", font=ctk.CTkFont(size=32, weight="bold"))
        username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.articles_frame = ctk.CTkScrollableFrame(self, label_text="Publicaciones")
        self.articles_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.articles_frame.grid_columnconfigure(0, weight=1)

        self.load_user_articles()
        self.protocol("WM_DELETE_WINDOW", self.close_profile)
        self.grab_set()

    def load_user_articles(self):
        articles = get_articles_by_user(self.user_id)
        if not articles:
            no_articles_label = ctk.CTkLabel(self.articles_frame, text="Este usuario aún no ha publicado nada.", font=ctk.CTkFont(size=18))
            no_articles_label.pack(pady=50)
            return

        for i, article in enumerate(articles):
            # Usamos el método de la app principal para crear las tarjetas
            self.main_app.create_article_card(self.articles_frame, article, i)

    def close_profile(self):
        self.grab_release()
        self.main_app.deiconify()
        self.destroy()