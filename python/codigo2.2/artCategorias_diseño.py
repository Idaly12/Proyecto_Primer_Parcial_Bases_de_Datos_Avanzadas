# blog_view.py - CÓDIGO COMPLETO Y MEJORADO
import customtkinter as ctk
from tkinter import messagebox

# Importaciones de los nuevos módulos
# Asegúrate de que estos módulos (ConexionBDD y perfilusuario) existen en tu proyecto
import ConexionBDD as db
from perfilusuario import ProfileWindow 

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class BlogApp(ctk.CTkToplevel):
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.title("Blog de Recetas")
        self.geometry("1200x800")
        self.user_id = user_id
        self.profile_window = None

        # Nuevo: para guardar la categoría seleccionada en la subida
        self.selected_category_id = None 

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1) 

        # --- Creación de Componentes de la UI ---
        self._create_header()
        self._create_main_content_area()
        self.show_frame(self.articles_frame) # Mostramos el frame de artículos al iniciar
        self.load_articles()

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="white")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        logo_label = ctk.CTkLabel(self.header_frame, text="Blogs de Recetas", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color="#720F0F")
        logo_label.grid(row=0, column=0, padx=(30, 0), pady=15, sticky="w")

        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, padx=30, pady=15, sticky="e")

        my_username = db.get_user_info(self.user_id)
        profile_button = ctk.CTkButton(right_header_frame, text=f"Mi Perfil ({my_username})", command=lambda: self.open_profile_window(self.user_id))
        profile_button.pack(side="right", padx=(10, 0))

        # El comando del botón ahora muestra el frame de subida
        self.upload_button = ctk.CTkButton(right_header_frame, text="Subir Receta →", command=self.show_upload_frame, width=150, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.upload_button.pack(side="right")

    def _create_main_content_area(self):
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.content_container.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.content_container.grid_columnconfigure(1, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_articles_frame()
        self._create_article_detail_frame()
        self._create_upload_frame()

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self.content_container, width=250, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(30, 0), pady=30)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        category_title = ctk.CTkLabel(self.sidebar_frame, text="Categorías", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        category_title.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="w")
        self.load_sidebar_categories()

    def _create_articles_frame(self):
        self.articles_frame = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="white")
        self.articles_frame.grid_columnconfigure(0, weight=1)
        self.articles_frame.grid_rowconfigure(1, weight=1)
        
        header_frame = ctk.CTkFrame(self.articles_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_insights = ctk.CTkLabel(header_frame, text="¿Qué vamos a cocinar hoy? 👩‍🍳", font=ctk.CTkFont(size=36, weight="bold"), anchor="w")
        title_insights.grid(row=0, column=0, sticky="w")
        subtitle_insights = ctk.CTkLabel(header_frame, text="Recetas y consejos de nuestros mejores usuarios.", font=ctk.CTkFont(size=18), text_color="gray50", anchor="w")
        subtitle_insights.grid(row=1, column=0, sticky="w", pady=(0, 15))
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.articles_frame, label_text="Últimas Recetas", label_font=ctk.CTkFont(size=14), fg_color="white")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    # MODIFICADO: El frame de detalle ahora es un CTkScrollableFrame
    def _create_article_detail_frame(self):
        self.article_detail_frame = ctk.CTkScrollableFrame(self.content_container, corner_radius=0, fg_color="white")

    # MODIFICADO: Estilo mejorado para el formulario de subida
    def _create_upload_frame(self):
        self.upload_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(4, weight=1) # El content_textbox ahora está en la fila 4

        ctk.CTkLabel(self.upload_frame, text="Publicar una Nueva Receta ✍️", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Nombre de la Receta
        ctk.CTkLabel(self.upload_frame, text="Nombre de la Receta:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        self.upload_title_entry = ctk.CTkEntry(self.upload_frame, height=40, placeholder_text="Ej. Pizza casera con masa madre")
        self.upload_title_entry.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Instrucciones
        ctk.CTkLabel(self.upload_frame, text="Instrucciones (Ingredientes y Pasos):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        # Textbox con placeholder y esquinas redondeadas
        self.upload_content_textbox = ctk.CTkTextbox(self.upload_frame, wrap="word", corner_radius=10, border_width=1, border_color="gray70", fg_color="gray95")
        self.upload_content_textbox.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="nsew")

        # Categoría (Usando un Frame para los botones de burbuja)
        ctk.CTkLabel(self.upload_frame, text="Categoría (Elige una):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.categories_button_frame = ctk.CTkFrame(self.upload_frame, fg_color="transparent")
        self.categories_button_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")
        self.load_category_buttons() # Llama a la nueva función

        # Botones de Acción
        buttons_frame = ctk.CTkFrame(self.upload_frame, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, padx=20, pady=20, sticky="e")
        
        self.cancel_button = ctk.CTkButton(buttons_frame, text="Cancelar", command=self.load_articles, fg_color="gray50", hover_color="gray30")
        self.cancel_button.pack(side="left", padx=(0, 10))

        self.publish_button = ctk.CTkButton(buttons_frame, text="Subir al blog 🚀", command=self.publish_article, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.publish_button.pack(side="left")

    # NUEVO: Función para crear los botones de categoría tipo 'burbuja'
    def load_category_buttons(self):
        for widget in self.categories_button_frame.winfo_children():
            widget.destroy()

        self.categories_data = db.get_all_categories()
        
        if not self.categories_data:
            ctk.CTkLabel(self.categories_button_frame, text="No hay categorías disponibles.").pack(pady=5)
            return

        for cat_id, cat_name in self.categories_data:
            btn = ctk.CTkButton(
                self.categories_button_frame, 
                text=cat_name, 
                command=lambda cid=cat_id: self.select_upload_category(cid),
                font=ctk.CTkFont(size=14),
                fg_color="gray80",
                text_color="black",
                hover_color="gray60",
                corner_radius=20, # Le da la forma ovalada/burbuja
                width=0 # Ajusta el ancho al texto
            )
            btn.pack(side="left", padx=(5, 5), pady=5)
            # Marcar la primera categoría como seleccionada por defecto si no hay ninguna
            if self.selected_category_id is None:
                self.select_upload_category(cat_id)

        self.update_category_button_styles()


    # NUEVO: Lógica para manejar la selección de categoría y actualizar el estilo
    def select_upload_category(self, cat_id):
        self.selected_category_id = cat_id
        self.update_category_button_styles()

    # NUEVO: Actualiza el estilo visual de los botones de categoría
    def update_category_button_styles(self):
        for widget in self.categories_button_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                cat_name = widget.cget("text")
                # Busca el ID de la categoría por su nombre
                current_cat_id = next((cid for cid, name in self.categories_data if name == cat_name), None)
                
                if current_cat_id == self.selected_category_id:
                    # Estilo seleccionado
                    widget.configure(fg_color="#720F0F", text_color="white", hover_color="#5D0C0C")
                else:
                    # Estilo no seleccionado
                    widget.configure(fg_color="gray80", text_color="black", hover_color="gray60")

    def show_frame(self, frame_to_show):
        # Ocultamos todos los frames principales
        self.articles_frame.grid_forget()
        self.article_detail_frame.grid_forget()
        self.upload_frame.grid_forget()
        # Mostramos solo el que nos interesa
        frame_to_show.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

    # MODIFICADO: Reconstruye la vista de detalle para una sola barra de scroll
    def show_article_detail(self, article):
        # Limpiamos el frame por si tenía contenido anterior
        for widget in self.article_detail_frame.winfo_children():
            widget.destroy()

        self.article_detail_frame.grid_columnconfigure(0, weight=1)

        # Frame contenedor para organizar todo dentro del scrollable
        container = ctk.CTkFrame(self.article_detail_frame, fg_color="transparent")
        container.pack(fill="x", expand=True, padx=20, pady=10)
        container.grid_columnconfigure(0, weight=1)

        # Botón de volver mejorado
        back_button = ctk.CTkButton(container, text="← Volver a las Recetas", command=self.load_articles, fg_color="#D32F2F", hover_color="#B71C1C", corner_radius=8)
        back_button.grid(row=0, column=0, pady=(0, 25), sticky="w")

        title_label = ctk.CTkLabel(container, text=article['title'], font=ctk.CTkFont(size=38, weight="bold"), wraplength=800, justify="left")
        title_label.grid(row=1, column=0, pady=(5, 10), sticky="w")
        
        author_frame = ctk.CTkFrame(container, fg_color="transparent")
        author_frame.grid(row=2, column=0, pady=(0, 20), sticky="w")

        author_button = ctk.CTkButton(
            author_frame, text=f"Publicado por: {article.get('username', 'N/A')}",
            command=lambda uid=article.get('user_id'): self.open_profile_window(uid) if uid else None,
            fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        author_button.pack(side="left")
        date_label = ctk.CTkLabel(author_frame, text=f" el {article.get('created_at', 'N/A')}", font=ctk.CTkFont(size=14), text_color="gray50")
        date_label.pack(side="left")

        # El contenido ahora es un CTkLabel que se expande automáticamente (muestra la receta completa)
        content_label = ctk.CTkLabel(container, text=article['text'], font=ctk.CTkFont(size=16), wraplength=800, justify="left", anchor="nw")
        content_label.grid(row=3, column=0, pady=(15, 30), sticky="ew")

        separator = ctk.CTkFrame(container, height=2, fg_color="gray80")
        separator.grid(row=4, column=0, pady=(10, 20), sticky="ew")
        
        # --- Sección de Comentarios ---
        ctk.CTkLabel(container, text="Deja tu comentario:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=5, column=0, pady=(0, 5), sticky="w")
        new_comment_entry = ctk.CTkTextbox(container, height=80, wrap="word", corner_radius=10, border_width=1, border_color="gray70")
        new_comment_entry.grid(row=6, column=0, pady=5, sticky="ew")
        
        def post_new_comment():
            comment_text = new_comment_entry.get("1.0", "end-1c").strip()
            if not comment_text:
                messagebox.showwarning("Atención", "El comentario no puede estar vacío.", parent=self)
                return
            db.add_comment(article['id'], self.user_id, comment_text)
            new_comment_entry.delete("1.0", "end")
            # Recargar la vista de detalle para mostrar el nuevo comentario
            self.show_article_detail(article)

        post_comment_button = ctk.CTkButton(container, text="Publicar Comentario", command=post_new_comment, fg_color="#1E90FF", hover_color="#176EBD")
        post_comment_button.grid(row=7, column=0, pady=10, sticky="e")

        ctk.CTkLabel(container, text="Comentarios 💬", font=ctk.CTkFont(size=20, weight="bold")).grid(row=8, column=0, pady=(30, 10), sticky="w")
        
        # El frame de comentarios
        comments_frame = ctk.CTkFrame(container, fg_color="transparent")
        comments_frame.grid(row=9, column=0, pady=5, sticky="nsew")
        
        comments = db.get_comments(article['id'])
        if not comments:
            ctk.CTkLabel(comments_frame, text="Aún no hay comentarios. ¡Sé el primero!", text_color="gray").pack(pady=10)
        else:
            for comment in comments:
                comment_card = ctk.CTkFrame(comments_frame, fg_color="gray95", corner_radius=10)
                comment_card.pack(fill="x", pady=5)
                comment_card.grid_columnconfigure(0, weight=1)

                # Encabezado del comentario (Usuario y fecha)
                user_date_frame = ctk.CTkFrame(comment_card, fg_color="transparent")
                user_date_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
                
                user_text = f"{comment['username']}"
                author_btn = ctk.CTkButton(user_date_frame, text=user_text, command=lambda uid=comment['user_id']: self.open_profile_window(uid),
                                        fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0", 
                                        font=ctk.CTkFont(size=14, weight="bold"), anchor="w", width=0)
                author_btn.pack(side="left")
                
                date_lbl = ctk.CTkLabel(user_date_frame, text=f" - {comment['created_at']}", font=ctk.CTkFont(size=12), text_color="gray50")
                date_lbl.pack(side="left")
                
                # Contenido del comentario
                ctk.CTkLabel(comment_card, text=comment['text'], wraplength=700, justify="left", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")


        self.show_frame(self.article_detail_frame)

    # MODIFICADO: Prepara el formulario de subida
    def show_upload_frame(self):
        # Limpiamos los campos antes de mostrar
        self.upload_title_entry.delete(0, "end")
        self.upload_content_textbox.delete("1.0", "end")
        self.selected_category_id = None # Reiniciar la categoría seleccionada
        self.load_category_buttons() # Recargar los botones
        self.show_frame(self.upload_frame)


    # NUEVO: Lógica para publicar el artículo
    def publish_article(self):
        title = self.upload_title_entry.get()
        content = self.upload_content_textbox.get("1.0", "end-1c").strip()

        if not title or not content:
            messagebox.showerror("Error", "El título y el contenido son obligatorios.", parent=self)
            return
        if self.selected_category_id is None:
            messagebox.showerror("Error", "Debes seleccionar una categoría.", parent=self)
            return

        db.create_article(title, content, self.user_id)
        new_article_id = db.get_latest_article_id_by_user(self.user_id)

        if new_article_id:
            db.associate_article_categories(new_article_id, [self.selected_category_id])
        
        messagebox.showinfo("Éxito", "¡Receta publicada con éxito!", parent=self)
        
        # Recargamos la lista de artículos para ver el nuevo
        self.load_articles()
        self.load_sidebar_categories()


    def open_profile_window(self, user_id_to_view):
        if self.profile_window is None or not self.profile_window.winfo_exists():
            self.withdraw()
            self.profile_window = ProfileWindow(master=self, user_id_to_view=user_id_to_view, main_app=self)
        else:
            self.profile_window.focus()

    def load_sidebar_categories(self):
        # Limpiamos solo los botones de categorías, no el título
        for widget in self.sidebar_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
        
        all_button = ctk.CTkButton(self.sidebar_frame, text="Mostrar Todas", fg_color="#D32F2F", hover_color="#B71C1C", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", command=self.load_articles)
        all_button.grid(row=1, column=0, padx=0, pady=5, sticky="ew")

        categories = db.get_all_categories()
        if not categories:
            ctk.CTkLabel(self.sidebar_frame, text="No hay categorías.", text_color="gray50").grid(row=2, column=0, sticky="w")
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            btn = ctk.CTkButton(self.sidebar_frame, text=cat_name, fg_color="transparent", text_color="gray30", hover_color="gray90", font=ctk.CTkFont(size=14), anchor="w", command=lambda cid=cat_id: self.filter_by_category(cid))
            btn.grid(row=i + 2, column=0, padx=0, pady=5, sticky="ew")

    def filter_by_category(self, category_id):
        articles = db.get_articles_by_category(category_id)
        self.display_articles(articles)
        self.show_frame(self.articles_frame)

    def load_articles(self):
        articles = db.get_all_articles()
        self.display_articles(articles)
        self.show_frame(self.articles_frame)

    def display_articles(self, articles_list):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not articles_list:
            ctk.CTkLabel(self.scrollable_frame, text="No hay recetas para mostrar. ¡Sé el primero en subir una! 🍜", font=ctk.CTkFont(size=18)).pack(pady=50)
            return

        for i, article_data in enumerate(articles_list):
            self.create_article_card(self.scrollable_frame, article_data, i)

    # MODIFICADO: Tarjeta mejorada con botón de "Ver Receta" explícito.
    def create_article_card(self, parent_frame, article, row_index):
        card = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="gray95", border_color="gray80", border_width=1)
        separator = ctk.CTkFrame(parent_frame, height=1, fg_color="gray90")
        
        separator.pack(fill="x", pady=(20, 10), padx=10)
        card.pack(fill="x", pady=(10, 0), padx=10)
        card.grid_columnconfigure(0, weight=1)

        date_label = ctk.CTkLabel(card, text=article['created_at'], font=ctk.CTkFont(size=14, weight="bold"), text_color="#720F0F")
        date_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))

        title_label = ctk.CTkLabel(card, text=article['title'], font=ctk.CTkFont(size=24, weight="bold"), anchor="w", justify="left")
        title_label.grid(row=1, column=0, pady=(0, 10), sticky="w", padx=15)

        # Muestra solo un extracto de la receta
        extract = (article['text'][:200] + '...') if len(article['text']) > 200 else article['text']
        extract_label = ctk.CTkLabel(card, text=extract, wraplength=800, text_color="gray40", anchor="w", justify="left")
        extract_label.grid(row=2, column=0, pady=(0, 10), sticky="w", padx=15)

        # Contenedor para el autor y el botón
        footer_frame = ctk.CTkFrame(card, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        footer_frame.grid_columnconfigure(0, weight=1)
        
        # Botón del Autor
        author_button = ctk.CTkButton(footer_frame, text=f"por {article['username']}", command=lambda uid=article['user_id']: self.open_profile_window(uid),
                                        fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=0)
        author_button.grid(row=0, column=0, sticky="w")
        
        # Botón de "Ver Receta" para ver el contenido COMPLETO
        view_button = ctk.CTkButton(footer_frame, text="Ver Receta →", command=lambda art=article: self.show_article_detail(art), 
                                    fg_color="#D32F2F", hover_color="#B71C1C", corner_radius=8)
        view_button.grid(row=0, column=1, sticky="e")