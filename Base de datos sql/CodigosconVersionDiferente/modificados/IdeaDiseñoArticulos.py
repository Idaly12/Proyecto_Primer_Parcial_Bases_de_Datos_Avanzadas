import customtkinter as ctk

# --- Configuración Inicial ---
ctk.set_appearance_mode("Light") # Fondo blanco dominante
ctk.set_default_color_theme("blue") # Para el botón azul de "Subir Artículo"

class BlogApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blog Coranu Style - Python GUI")
        self.geometry("1200x800")
        
        # Configurar la rejilla principal: 2 filas (Header y Contenido)
        self.grid_rowconfigure(1, weight=1) # Fila 1 (Contenido) es expandible
        self.grid_columnconfigure(0, weight=1)

        # ---------------------------
        # 1. Barra Superior (Header)
        # ---------------------------
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="white")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Logo y Menú (Izquierda del Header)
        logo_label = ctk.CTkLabel(self.header_frame, text="Blogs de Recetas", 
                                  font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), 
                                  text_color="#720F0F")
        logo_label.grid(row=0, column=0, padx=(30, 0), pady=15, sticky="w")

        # Botón "Subir Artículo" (Derecha del Header, en azul)
        self.upload_button = ctk.CTkButton(self.header_frame, text="Subir Artículo →", 
                                            command=self.open_upload_window,
                                            width=150, corner_radius=8,
                                            fg_color="#1E90FF", hover_color="#007ACC")
        self.upload_button.grid(row=0, column=1, padx=30, pady=15, sticky="e")

        # ---------------------------
        # 2. Contenido Principal (Fila 1)
        # ---------------------------
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.content_container.grid(row=1, column=0, sticky="nsew")
        
        # Rejilla del Contenido Principal: 2 Columnas (Filtros y Artículos)
        self.content_container.grid_columnconfigure(0, minsize=250) # Columna de filtros (fija)
        self.content_container.grid_columnconfigure(1, weight=1) # Columna de artículos (expansiva)
        self.content_container.grid_rowconfigure(0, weight=1)

        # --- A. Barra Lateral Izquierda (Filtros/Categorías) ---
        self.sidebar_frame = ctk.CTkFrame(self.content_container, width=250, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(30, 0), pady=30)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # Título de las Categorías
        category_title = ctk.CTkLabel(self.sidebar_frame, text="Blog Topics", 
                                      font=ctk.CTkFont(size=16, weight="bold"), 
                                      anchor="w")
        category_title.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="w")
        
        # Simulación de Categorías (Botones con apariencia de enlace)
        categories = ["Company", "Design", "Technology", "Crypto", "AI", "Work"]
        for i, cat in enumerate(categories):
            cat_button = ctk.CTkButton(self.sidebar_frame, text=cat, 
                                        fg_color="transparent", 
                                        text_color="gray30", 
                                        hover_color="gray90", 
                                        font=ctk.CTkFont(size=14), 
                                        anchor="w")
            cat_button.grid(row=i+1, column=0, padx=0, pady=5, sticky="ew")


        # --- B. Área de Artículos ---
        self.articles_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")
        self.articles_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.articles_frame.grid_columnconfigure(0, weight=1)
        self.articles_frame.grid_rowconfigure(3, weight=1)

        # Título Principal (Insights from our team)
        title_insights = ctk.CTkLabel(self.articles_frame, text="Insights from our team", 
                                      font=ctk.CTkFont(size=36, weight="bold"), 
                                      anchor="w")
        title_insights.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="w")
        
        # Subtítulo
        subtitle_insights = ctk.CTkLabel(self.articles_frame, 
                                         text="Powerful Trading Tools and Features for Experienced Investors", 
                                         font=ctk.CTkFont(size=18), 
                                         text_color="gray50",
                                         anchor="w")
        subtitle_insights.grid(row=1, column=0, padx=0, pady=(0, 20), sticky="w")
        
        # Buscador secundario (Similar al de la imagen)
        search_secondary = ctk.CTkEntry(self.articles_frame, placeholder_text="search...", 
                                        width=300, corner_radius=8, 
                                        fg_color="gray95", border_width=0)
        search_secondary.grid(row=2, column=0, padx=0, pady=(0, 20), sticky="w")
        
        # Contenedor con Scroll para Artículos
        self.scrollable_frame = ctk.CTkScrollableFrame(self.articles_frame, label_text="Trending Topics", 
                                                       label_font=ctk.CTkFont(size=14), 
                                                       fg_color="white")
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Cargar artículos
        self.load_articles()

    def load_articles(self):
        # Datos de ejemplo, simulando la carga desde SQLite
        articles_data = [
            {"title": "Powerful Trading Tools and Features for Experienced Investors", 
             "extract": "I'm always trying to think of new and interesting business ideas...", 
             "tags": ["Tools", "Trading"], "date": "Mar 1", "time": "7 min read", "highlighted": True},
            {"title": "The Future of AI in Content Creation", 
             "extract": "Artificial Intelligence is rapidly changing how we generate media and text...", 
             "tags": ["AI", "Technology"], "date": "Feb 20", "time": "5 min read", "highlighted": False},
            {"title": "Minimalist Design Principles for Bloggers", 
             "extract": "Using white space effectively can significantly boost readability and focus.", 
             "tags": ["Design", "Minimalism"], "date": "Feb 10", "time": "8 min read", "highlighted": False},
        ]
        
        for i, article in enumerate(articles_data):
            self.create_article_card(self.scrollable_frame, article, i)

    def create_article_card(self, parent_frame, article, row_index):
        # La tarjeta tendrá 2 columnas: 
        # Col 0: Texto (80% ancho) | Col 1: Imagen/Gráfico (20% ancho)
        card = ctk.CTkFrame(parent_frame, corner_radius=0, fg_color="white")
        # Línea de separación sutil, excepto si es el primer artículo destacado
        if row_index > 0:
            separator = ctk.CTkFrame(parent_frame, height=1, fg_color="gray80", corner_radius=0)
            separator.grid(row=row_index*2, column=0, sticky="ew", pady=(20, 10))
            card.grid(row=row_index*2 + 1, column=0, padx=0, pady=(10, 20), sticky="ew")
        else:
             card.grid(row=row_index*2 + 1, column=0, padx=0, pady=(10, 20), sticky="ew")

        card.grid_columnconfigure(0, weight=4) # Texto
        card.grid_columnconfigure(1, weight=1) # Imagen

        # --- Columna de Texto (Izquierda) ---
        date_label = ctk.CTkLabel(card, text=article['date'], 
                                  font=ctk.CTkFont(size=14, weight="bold"), 
                                  text_color="gray50", anchor="w")
        date_label.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="w")

        title_label = ctk.CTkLabel(card, text=article['title'], 
                                   font=ctk.CTkFont(size=24, weight="bold"), 
                                   anchor="w", justify="left")
        title_label.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="w")

        extract_label = ctk.CTkLabel(card, text=article['extract'], 
                                     wraplength=600, text_color="gray40", 
                                     anchor="w", justify="left")
        extract_label.grid(row=2, column=0, padx=0, pady=(0, 10), sticky="w")

        # Metadatos (Tags, Autor, Tiempo)
        tags_text = f"{' '.join(article['tags'])} | Author Name | {article['time']}"
        meta_label = ctk.CTkLabel(card, text=tags_text, 
                                  font=ctk.CTkFont(size=12, weight="bold"), 
                                  text_color="#1E90FF", anchor="w")
        meta_label.grid(row=3, column=0, padx=0, pady=0, sticky="w")

        # --- Columna de Gráfico (Derecha) ---
        if article['highlighted']:
            # Simular el gráfico azul destacado de la imagen
            graphic_frame = ctk.CTkFrame(card, corner_radius=10, fg_color="#1E90FF", height=150)
            graphic_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(30, 0))
            # Opcional: añadir un icono blanco dentro para simular el logo
            ctk.CTkLabel(graphic_frame, text="⚙️", font=ctk.CTkFont(size=60), text_color="white").place(relx=0.5, rely=0.5, anchor="center")


    def open_upload_window(self):
        # Abre la ventana modal para subir artículos
        # (Usa la clase ArticleUploader definida en la respuesta anterior)
        if hasattr(self, 'toplevel_window') and self.toplevel_window.winfo_exists():
            self.toplevel_window.focus()
        else:
            self.toplevel_window = ArticleUploader(self)

# ---------------------------
# La clase ArticleUploader se usaría tal cual la de la respuesta previa
# ---------------------------

class ArticleUploader(ctk.CTkToplevel):
    # Usar la implementación de la respuesta anterior, que tiene Título, Contenido, 
    # Categoría y Tags
    # ... (código de ArticleUploader aquí)
    def __init__(self, master):
        super().__init__(master)
        self.title("Subir Nuevo Artículo")
        self.geometry("600x500")
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Título del Artículo:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.title_entry = ctk.CTkEntry(self, width=500)
        self.title_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self, text="Contenido:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.content_textbox = ctk.CTkTextbox(self, height=200)
        self.content_textbox.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self, text="Categoría (Ej: Tecnología, Viajes):", font=ctk.CTkFont(size=14)).grid(row=4, column=0, padx=20, pady=(5, 0), sticky="w")
        self.category_entry = ctk.CTkEntry(self)
        self.category_entry.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self, text="Tags (Separados por coma):", font=ctk.CTkFont(size=14)).grid(row=6, column=0, padx=20, pady=(5, 0), sticky="w")
        self.tags_entry = ctk.CTkEntry(self)
        self.tags_entry.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.publish_button = ctk.CTkButton(self, text="✅ Publicar", command=self.publish_article)
        self.publish_button.grid(row=8, column=0, padx=20, pady=10)

    def publish_article(self):
        title = self.title_entry.get()
        content = self.content_textbox.get("0.0", "end")
        category = self.category_entry.get()
        tags = [t.strip() for t in self.tags_entry.get().split(',') if t.strip()]

        if title and content.strip():
            # Aquí iría la lógica para GUARDAR el artículo en la DB o archivo
            print(f"Publicado: Título='{title}', Categoría='{category}', Tags={tags}")
            self.master.load_articles() 
            self.destroy()
        else:
            # Usar CTkMessagebox si deseas una alerta modal
            print("Error: El título y el contenido no pueden estar vacíos.")

if __name__ == "__main__":
    app = BlogApp()
    app.mainloop()