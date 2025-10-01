
import customtkinter as ctk
import ConexionBDD as db
from PIL import Image
from pathlib import Path

class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master, main_app):
        super().__init__(master=master, fg_color="white", corner_radius=0)
        self.main_app = main_app
        self.current_user_id = None

        self.main_font = ctk.CTkFont(family="Roboto", size=14)
        self.bold_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.title_font = ctk.CTkFont(family="Roboto", size=24, weight="bold")
        self.subtitle_font = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.text_font = ctk.CTkFont(family="Roboto", size=14)

        self._setup_layout()

    def _setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, fg_color="white", width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20), pady=0)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        header_sidebar_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_sidebar_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        back_button = ctk.CTkButton(header_sidebar_frame, text="← Volver", command=self.main_app.load_articles,
                                    fg_color="transparent", text_color="gray", hover_color="gray80",
                                    font=self.bold_font, anchor="w")
        back_button.pack(side="left")
        
        self.profile_info_container = ctk.CTkFrame(self.sidebar_frame, fg_color="white")
        self.profile_info_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.profile_info_container.grid_columnconfigure(0, weight=1)

        images_path = Path(__file__).parent / "Imagenes"
        user_icon_path = images_path / "user_icon.png"

        try:
            user_icon_image = ctk.CTkImage(Image.open(user_icon_path), size=(100, 100))
            profile_image_label = ctk.CTkLabel(self.profile_info_container, image=user_icon_image, text="")
            profile_image_label.grid(row=0, column=0, pady=(20, 10))
        except FileNotFoundError:
            print(f"ADVERTENCIA: No se encontró '{user_icon_path}'. Mostrando círculo gris.")
            profile_pic_canvas = ctk.CTkCanvas(self.profile_info_container, width=100, height=100,
                                                bg="white", highlightthickness=0)
            profile_pic_canvas.grid(row=0, column=0, pady=(20, 10))
            profile_pic_canvas.create_oval(2, 2, 98, 98, fill="gray80", outline="gray70", width=2)

        self.username_label = ctk.CTkLabel(self.profile_info_container, text="Nombre de Usuario", font=self.title_font, text_color="black")
        self.username_label.grid(row=1, column=0, pady=(10, 5))

        self.description_label = ctk.CTkLabel(self.profile_info_container, text="Usuario de Recetas", font=self.text_font, text_color="gray")
        self.description_label.grid(row=2, column=0, pady=(0, 20))

        ctk.CTkFrame(self.profile_info_container, height=1, fg_color="gray80").grid(row=3, column=0, sticky="ew", pady=(10,20))
        
        logout_button = ctk.CTkButton(self.profile_info_container, text="Cerrar Sesión", command=self.main_app.logout,
                                          fg_color="transparent", hover_color="gray80", text_color="gray",
                                          font=self.bold_font, height=40, corner_radius=8,
                                          border_color="gray", border_width=2)
        logout_button.grid(row=4, column=0, sticky="ew", pady=10)
        
        self.articles_display_frame = ctk.CTkScrollableFrame(self, fg_color="gray92", corner_radius=0)
        self.articles_display_frame.grid(row=0, column=1, sticky="nsew")
        self.articles_display_frame.grid_columnconfigure(0, weight=1)

        self.articles_title_label = ctk.CTkLabel(self.articles_display_frame, text="", font=self.title_font, text_color="black")
        self.articles_title_label.grid(row=0, column=0, sticky="w", padx=30, pady=(30, 20))
        
        self.no_articles_label = ctk.CTkLabel(self.articles_display_frame, text="Este usuario aún no ha publicado recetas.", font=self.text_font, text_color="gray")

    def load_user_data(self, user_id):
        self.current_user_id = user_id
        username = db.get_user_info(user_id)
        
        if username and username != "Usuario Desconocido":
            self.username_label.configure(text=username)
            self.articles_title_label.configure(text=f"Recetas de {username}")
            self.show_my_articles()
        else:
            self.username_label.configure(text="Usuario Desconocido")
            self.articles_title_label.configure(text="Recetas del Usuario")
            self.clear_articles_display()

    def show_my_articles(self):
        self.clear_articles_display()
        if not self.current_user_id:
            return

        articles = db.get_articles_by_user(self.current_user_id)

        if not articles:
            self.no_articles_label.grid(row=1, column=0, padx=30, pady=50)
        else:
            self.no_articles_label.grid_forget()

        for i, article_data in enumerate(articles):
            self._create_article_card(self.articles_display_frame, article_data, i + 1)

    def _create_article_card(self, parent_frame, article, row_index):
        card = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="white")
        card.grid(row=row_index, column=0, sticky="ew", padx=30, pady=10)
        card.grid_columnconfigure(0, weight=1)

        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
        inner_frame.grid_columnconfigure(0, weight=1)

        date_label = ctk.CTkLabel(inner_frame, text=article['created_at'], font=ctk.CTkFont(size=12, weight="bold"), text_color="#D32F2F")
        date_label.grid(row=0, column=0, sticky="w")

        title_label = ctk.CTkLabel(inner_frame, text=article['title'], font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        title_label.grid(row=1, column=0, pady=(5, 10), sticky="w")

        extract = (article['text'][:150] + '...') if len(article['text']) > 150 else article['text']
        extract_label = ctk.CTkLabel(inner_frame, text=extract, wraplength=700, text_color="gray50", anchor="w", justify="left")
        extract_label.grid(row=2, column=0, pady=(0, 15), sticky="w")
        
        view_button = ctk.CTkButton(inner_frame, text="Ver Receta Completa", 
                                    command=lambda art=article: self.main_app.show_article_detail(art),
                                    fg_color="transparent", hover_color="gray90", text_color="#1E90FF",
                                    font=self.bold_font, anchor="w", width=0)
        view_button.grid(row=3, column=0, sticky="w")

    def clear_articles_display(self):
        for widget in self.articles_display_frame.winfo_children():
            if widget not in [self.articles_title_label, self.no_articles_label]:
                widget.destroy()