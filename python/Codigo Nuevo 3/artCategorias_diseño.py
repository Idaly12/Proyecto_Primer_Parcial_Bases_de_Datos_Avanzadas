import customtkinter as ctk
from tkinter import messagebox
import ConexionBDD as db
from perfilusuario import ProfileFrame # <-- MODIFICACIÓN 1: Se importa la clase correcta

# --- SE ELIMINÓ LA CLASE "ProfileFrame" TEMPORAL DE AQUÍ ---

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class BlogApp(ctk.CTkToplevel):
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.title("Blog de Recetas")
        self.geometry("1200x800")
        self.user_id = user_id
        
        self.selected_category_id = None 
        self.tag_checkboxes = {}
        self.is_admin = db.is_user_admin(self.user_id)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) 

        self._create_main_content_area()
        self._create_header()
        
        self.show_frame(self.articles_frame)
        self.load_articles()

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
    
    def logout(self):
        try:
            # Importación local para evitar dependencia circular
            from logindiseño import AuthWindow
            self.destroy()
            AuthWindow(master=self.master)
        except ImportError:
            messagebox.showerror("Error de Cierre", "No se encontró logindiseño.AuthWindow.", parent=self)
            self.master.destroy()

## --- ESTRUCTURA PRINCIPAL Y ENCABEZADO ---
    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="white")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        logo_label = ctk.CTkLabel(self.header_frame, text="Blogs de Recetas", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color="#720F0F")
        logo_label.grid(row=0, column=0, padx=(30, 0), pady=15, sticky="w")

        right_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_frame.grid(row=0, column=1, padx=30, pady=15, sticky="e")

        my_username = db.get_user_info(self.user_id)
        profile_button = ctk.CTkButton(right_header_frame, text=f"Mi Perfil ({my_username})", command=lambda: self.show_profile_frame(self.user_id))
        profile_button.pack(side="right", padx=(10, 0))

        self.upload_button = ctk.CTkButton(right_header_frame, text="Subir Receta →", command=self.show_upload_frame, width=150, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.upload_button.pack(side="right")
        
        if self.is_admin:
            self.admin_button = ctk.CTkButton(right_header_frame, text="⚙️ Admin Panel", command=self.show_admin_panel_frame, width=140, corner_radius=8, fg_color="#388E3C", hover_color="#2E7D32")
            self.admin_button.pack(side="right", padx=(10, 0))

    def _create_main_content_area(self):
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.content_container.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.content_container.grid_columnconfigure(1, weight=1) 
        self.content_container.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_articles_frame()
        self._create_article_detail_frame()
        self._create_upload_frame()
        self._create_profile_frame()
        self._create_admin_panel() 
        
    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self.content_container, width=250, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(30, 0), pady=30)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        category_title = ctk.CTkLabel(self.sidebar_frame, text="Categorías", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        category_title.pack(padx=0, pady=(0, 5), anchor="w", fill="x")
        
        self.categories_sidebar_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.categories_sidebar_frame.pack(fill="x", expand=True, anchor="w")
        self.load_sidebar_categories()

        tag_title = ctk.CTkLabel(self.sidebar_frame, text="Etiquetas", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        tag_title.pack(padx=0, pady=(20, 5), anchor="w", fill="x")

        self.tags_sidebar_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.tags_sidebar_frame.pack(fill="x", expand=True, anchor="w")
        self.load_sidebar_tags()

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

    def _create_article_detail_frame(self):
        self.article_detail_frame = ctk.CTkScrollableFrame(self.content_container, corner_radius=0, fg_color="white")

    def _create_upload_frame(self):
        self.upload_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(0, weight=1) 
        
        upload_content_scroll = ctk.CTkScrollableFrame(self.upload_frame, fg_color="transparent")
        upload_content_scroll.grid(row=0, column=0, sticky="nsew", padx=20)
        upload_content_scroll.grid_columnconfigure(0, weight=1)
        
        row_counter = 0

        ctk.CTkLabel(upload_content_scroll, text="Publicar una Nueva Receta ✍️", font=ctk.CTkFont(size=28, weight="bold")).grid(row=row_counter, column=0, padx=0, pady=(20, 15), sticky="w"); row_counter+=1
        
        # Título
        ctk.CTkLabel(upload_content_scroll, text="Nombre de la Receta:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, padx=0, pady=(10, 5), sticky="w"); row_counter+=1
        self.upload_title_entry = ctk.CTkEntry(upload_content_scroll, placeholder_text="Ej. Pizza casera con masa madre", height=40)
        self.upload_title_entry.grid(row=row_counter, column=0, padx=0, pady=(0, 15), sticky="ew"); row_counter+=1
        
        # Contenido (Instrucciones)
        ctk.CTkLabel(upload_content_scroll, text="Instrucciones (Ingredientes y Pasos):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, padx=0, pady=(10, 5), sticky="w"); row_counter+=1
        self.upload_content_textbox = ctk.CTkTextbox(upload_content_scroll, wrap="word", corner_radius=10, border_width=1, border_color="gray70", fg_color="gray95", height=200)
        self.upload_content_textbox.grid(row=row_counter, column=0, padx=0, pady=(0, 15), sticky="ew")
        
        row_counter+=1
        
        # Categoría
        ctk.CTkLabel(upload_content_scroll, text="Categoría (Elige una):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, padx=0, pady=(10, 5), sticky="w"); row_counter+=1
        self.categories_button_frame = ctk.CTkFrame(upload_content_scroll, fg_color="transparent")
        self.categories_button_frame.grid(row=row_counter, column=0, padx=0, pady=(0, 20), sticky="w"); row_counter+=1
        self.load_category_buttons()

        # Etiquetas
        ctk.CTkLabel(upload_content_scroll, text="Etiquetas (Elige las que apliquen):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row_counter, column=0, padx=0, pady=(10, 5), sticky="w"); row_counter+=1
        self.tags_checkbox_frame = ctk.CTkFrame(upload_content_scroll, fg_color="transparent")
        self.tags_checkbox_frame.grid(row=row_counter, column=0, padx=0, pady=(0, 20), sticky="w"); row_counter+=1
        self.load_tag_checkboxes()

        # Botones de Acción (Cancelar y Publicar Receta)
        buttons_frame = ctk.CTkFrame(upload_content_scroll, fg_color="transparent")
        buttons_frame.grid(row=row_counter, column=0, padx=0, pady=20, sticky="e"); row_counter+=1
        
        self.cancel_button = ctk.CTkButton(buttons_frame, text="Cancelar", command=self.load_articles, fg_color="gray50", hover_color="gray30")
        self.cancel_button.pack(side="left", padx=(0, 10))
        
        self.publish_button = ctk.CTkButton(buttons_frame, text="Subir al blog 🚀", command=self.publish_article, corner_radius=8, fg_color="#D32F2F", hover_color="#B71C1C")
        self.publish_button.pack(side="left")

    def _create_profile_frame(self):
        # Esta función ahora crea una instancia de la clase importada de perfilusuario.py
        self.profile_frame = ProfileFrame(master=self.content_container, main_app=self)

    def _create_admin_panel(self):
        self.admin_panel_frame = ctk.CTkFrame(self.content_container, fg_color="white")
        self.admin_panel_frame.grid_columnconfigure(0, weight=1)
        self.admin_panel_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.admin_panel_frame, text="⚙️ Panel de Administración", font=ctk.CTkFont(size=32, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        self.admin_tabview = ctk.CTkTabview(self.admin_panel_frame, fg_color="gray95", corner_radius=10)
        self.admin_tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_categories = self.admin_tabview.add("Categorías")
        self.tab_users = self.admin_tabview.add("Usuarios y Roles")
        self.tab_password = self.admin_tabview.add("Contraseña Admin")
        
        self._setup_categories_tab()
        self._setup_users_tab()
        self._setup_password_tab()

    # --- Funciones de soporte CRUD y UI ---

    def load_category_buttons(self):
        for widget in self.categories_button_frame.winfo_children():
            widget.destroy()
        self.categories_data = db.get_all_categories()
        if not self.categories_data:
            ctk.CTkLabel(self.categories_button_frame, text="No hay categorías disponibles.").pack(pady=5)
            return
        for cat_id, cat_name in self.categories_data:
            btn = ctk.CTkButton(
                self.categories_button_frame, text=cat_name, command=lambda cid=cat_id: self.select_upload_category(cid),
                font=ctk.CTkFont(size=14), fg_color="gray80", text_color="black", hover_color="gray60",
                corner_radius=20, width=0
            )
            btn.pack(side="left", padx=(5, 5), pady=5)
            if self.selected_category_id is None:
                self.select_upload_category(cat_id)
        self.update_category_button_styles()

    def load_tag_checkboxes(self):
        for widget in self.tags_checkbox_frame.winfo_children():
            widget.destroy()
        self.tag_checkboxes.clear()
        tags_data = db.get_all_tags()
        if not tags_data:
            ctk.CTkLabel(self.tags_checkbox_frame, text="No hay etiquetas disponibles.").pack(pady=5)
            return
        for i, (tag_id, tag_name) in enumerate(tags_data):
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(
                self.tags_checkbox_frame, text=tag_name, variable=var,
                onvalue=str(tag_id), offvalue="off"
            )
            cb.pack(side="left", padx=5, pady=5)
            self.tag_checkboxes[tag_id] = var

    def select_upload_category(self, cat_id):
        self.selected_category_id = cat_id
        self.update_category_button_styles()

    def update_category_button_styles(self):
        for widget in self.categories_button_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                cat_name = widget.cget("text")
                current_cat_id = next((cid for cid, name in self.categories_data if name == cat_name), None)
                if current_cat_id == self.selected_category_id:
                    widget.configure(fg_color="#720F0F", text_color="white", hover_color="#5D0C0C")
                else:
                    widget.configure(fg_color="gray80", text_color="black", hover_color="gray60")

    def show_frame(self, frame_to_show):
        self.articles_frame.grid_forget()
        self.article_detail_frame.grid_forget()
        self.upload_frame.grid_forget()
        self.admin_panel_frame.grid_forget()
        self.profile_frame.grid_forget()
        
        frame_to_show.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
    def show_article_detail(self, article):
        for widget in self.article_detail_frame.winfo_children():
            widget.destroy()

        self.article_detail_frame.grid_columnconfigure(0, weight=1)
        container = ctk.CTkFrame(self.article_detail_frame, fg_color="transparent")
        container.pack(fill="x", expand=True, padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)
        
        back_button = ctk.CTkButton(container, text="← Volver a las Recetas", command=self.load_articles, fg_color="#D32F2F", hover_color="#B71C1C", corner_radius=8)
        back_button.grid(row=0, column=0, pady=(0, 25), sticky="w")
        title_label = ctk.CTkLabel(container, text=article['title'], font=ctk.CTkFont(size=38, weight="bold"), wraplength=800, justify="left")
        title_label.grid(row=1, column=0, pady=(5, 10), sticky="w")
        author_frame = ctk.CTkFrame(container, fg_color="transparent")
        author_frame.grid(row=2, column=0, pady=(0, 5), sticky="w")
        author_button = ctk.CTkButton(author_frame, text=f"Publicado por: {article.get('username', 'N/A')}", command=lambda uid=article.get('user_id'): self.show_profile_frame(uid) if uid else None, fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        author_button.pack(side="left")
        date_label = ctk.CTkLabel(author_frame, text=f" el {article.get('created_at', 'N/A')}", font=ctk.CTkFont(size=14), text_color="gray50")
        date_label.pack(side="left")
        
        tags_frame = ctk.CTkFrame(container, fg_color="transparent")
        tags_frame.grid(row=3, column=0, sticky="w", pady=(5, 10))
        article_tags = db.get_tags_for_article(article['id'])
        if article_tags:
            ctk.CTkLabel(tags_frame, text="Etiquetas: ", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
            for tag_name in article_tags:
                tag_label = ctk.CTkLabel(tags_frame, text=tag_name, fg_color="gray80", text_color="black", corner_radius=10, font=ctk.CTkFont(size=12))
                tag_label.pack(side="left", padx=(0, 5), ipady=2, ipadx=5)
        
        content_label = ctk.CTkLabel(container, text=article['text'], font=ctk.CTkFont(size=16), wraplength=800, justify="left", anchor="nw")
        content_label.grid(row=4, column=0, pady=(15, 30), sticky="ew")
        separator = ctk.CTkFrame(container, height=2, fg_color="gray80")
        separator.grid(row=5, column=0, pady=(10, 20), sticky="ew")
        
        ctk.CTkLabel(container, text="Deja tu comentario:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=6, column=0, pady=(0, 5), sticky="w")
        new_comment_entry = ctk.CTkTextbox(container, height=80, wrap="word", corner_radius=10, border_width=1, border_color="gray70")
        new_comment_entry.grid(row=7, column=0, pady=5, sticky="ew")
        
        def post_new_comment():
            comment_text = new_comment_entry.get("1.0", "end-1c").strip()
            if not comment_text:
                messagebox.showwarning("Atención", "El comentario no puede estar vacío.", parent=self)
                return
            db.add_comment(article['id'], self.user_id, comment_text)
            new_comment_entry.delete("1.0", "end")
            self.show_article_detail(article)
            
        post_comment_button = ctk.CTkButton(container, text="Publicar Comentario", command=post_new_comment, fg_color="#1E90FF", hover_color="#176EBD")
        post_comment_button.grid(row=8, column=0, pady=10, sticky="e")
        ctk.CTkLabel(container, text="Comentarios 💬", font=ctk.CTkFont(size=20, weight="bold")).grid(row=9, column=0, pady=(30, 10), sticky="w")
        comments_frame = ctk.CTkFrame(container, fg_color="transparent")
        comments_frame.grid(row=10, column=0, pady=5, sticky="nsew")
        
        comments = db.get_comments(article['id'])
        if not comments:
            ctk.CTkLabel(comments_frame, text="Aún no hay comentarios. ¡Sé el primero!", text_color="gray").pack(pady=10)
        else:
            for comment in comments:
                self.create_comment_card(comments_frame, comment)
                
        self.show_frame(self.article_detail_frame)

    def show_upload_frame(self):
        self.upload_title_entry.delete(0, "end")
        self.upload_content_textbox.delete("1.0", "end")
        self.selected_category_id = None
        self.load_category_buttons()
        self.load_tag_checkboxes()
        self.show_frame(self.upload_frame)

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
            selected_tag_ids = [tag_id for tag_id, var in self.tag_checkboxes.items() if var.get() != "off"]
            if selected_tag_ids:
                db.associate_article_tags(new_article_id, selected_tag_ids)
                
        messagebox.showinfo("Éxito", "¡Receta publicada con éxito!", parent=self)
        self.load_articles()
        self.load_sidebar_categories()
        self.load_sidebar_tags()

    def show_profile_frame(self, user_id_to_view):
        if user_id_to_view:
            self.profile_frame.load_user_data(user_id_to_view)
            self.show_frame(self.profile_frame)

    def load_sidebar_categories(self):
        for widget in self.categories_sidebar_frame.winfo_children():
            widget.destroy()
        
        all_button = ctk.CTkButton(self.categories_sidebar_frame, text="Mostrar Todas", fg_color="#D32F2F", hover_color="#B71C1C", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", command=self.load_articles)
        all_button.pack(fill="x", padx=0, pady=5)

        categories = db.get_all_categories()
        if not categories:
            ctk.CTkLabel(self.categories_sidebar_frame, text="No hay categorías.", text_color="gray50").pack(anchor="w")
            return

        for cat_id, cat_name in categories:
            btn = ctk.CTkButton(self.categories_sidebar_frame, text=cat_name, fg_color="transparent", text_color="gray30", hover_color="gray90", font=ctk.CTkFont(size=14), anchor="w", command=lambda cid=cat_id: self.filter_by_category(cid))
            btn.pack(fill="x", padx=0, pady=5)

    def load_sidebar_tags(self):
        for widget in self.tags_sidebar_frame.winfo_children():
            widget.destroy()
        
        tags = db.get_all_tags()
        if not tags:
            ctk.CTkLabel(self.tags_sidebar_frame, text="No hay etiquetas.", text_color="gray50").pack(anchor="w")
            return
            
        for tag_id, tag_name in tags:
            btn = ctk.CTkButton(self.tags_sidebar_frame, text=f"# {tag_name}", fg_color="transparent", text_color="gray30", hover_color="gray90", font=ctk.CTkFont(size=14), anchor="w", command=lambda tid=tag_id: self.filter_by_tag(tid))
            btn.pack(fill="x", padx=0, pady=5)

    def filter_by_category(self, category_id):
        articles = db.get_articles_by_category(category_id)
        self.display_articles(articles)
        self.show_frame(self.articles_frame)

    def filter_by_tag(self, tag_id):
        articles = db.get_articles_by_tag(tag_id)
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
            ctk.CTkLabel(self.scrollable_frame, text="No hay recetas para mostrar. 🍜", font=ctk.CTkFont(size=18)).pack(pady=50)
            return

        for i, article_data in enumerate(articles_list):
            self.create_article_card(self.scrollable_frame, article_data, i)

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
        extract = (article['text'][:200] + '...') if len(article['text']) > 200 else article['text']
        extract_label = ctk.CTkLabel(card, text=extract, wraplength=800, text_color="gray40", anchor="w", justify="left")
        extract_label.grid(row=2, column=0, pady=(0, 10), sticky="w", padx=15)
        
        footer_frame = ctk.CTkFrame(card, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        footer_frame.grid_columnconfigure(0, weight=1)
        author_button = ctk.CTkButton(footer_frame, text=f"por {article['username']}", command=lambda uid=article['user_id']: self.show_profile_frame(uid), fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=0)
        author_button.grid(row=0, column=0, sticky="w")
        view_button = ctk.CTkButton(footer_frame, text="Ver Receta →", command=lambda art=article: self.show_article_detail(art), fg_color="#D32F2F", hover_color="#B71C1C", corner_radius=8)
        view_button.grid(row=0, column=1, sticky="e")
        
    def create_comment_card(self, comments_frame, comment):
        comment_card = ctk.CTkFrame(comments_frame, fg_color="gray95", corner_radius=10)
        comment_card.pack(fill="x", pady=5)
        comment_card.grid_columnconfigure(0, weight=1)

        user_date_frame = ctk.CTkFrame(comment_card, fg_color="transparent")
        user_date_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        user_text = f"{comment['username']}"
        author_btn = ctk.CTkButton(user_date_frame, text=user_text, command=lambda uid=comment['user_id']: self.show_profile_frame(uid),
                                 fg_color="transparent", text_color="#1E90FF", hover_color="#E0E0E0", 
                                 font=ctk.CTkFont(size=14, weight="bold"), anchor="w", width=0)
        author_btn.pack(side="left")
        
        date_lbl = ctk.CTkLabel(user_date_frame, text=f" - {comment['created_at']}", font=ctk.CTkFont(size=12), text_color="gray50")
        date_lbl.pack(side="left")
        
        ctk.CTkLabel(comment_card, text=comment['text'], wraplength=700, justify="left", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

    def show_admin_panel_frame(self):
        if not self.is_admin:
            messagebox.showwarning("Acceso Denegado", "Solo los administradores pueden gestionar la aplicación.", parent=self)
            return
        
        self.load_user_list_for_admin() 
        self.load_category_list_for_admin()
        self.show_frame(self.admin_panel_frame)
        
    def _setup_categories_tab(self):
        self.tab_categories.grid_columnconfigure(0, weight=1)
        self.tab_categories.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(self.tab_categories, text="Nueva Categoría:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        self.new_category_entry = ctk.CTkEntry(self.tab_categories, height=40, placeholder_text="Ej. Postres Veganos")
        self.new_category_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkButton(self.tab_categories, text="➕ Agregar Categoría", command=self.add_new_category, fg_color="#388E3C", hover_color="#2E7D32").grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="w")

        ctk.CTkLabel(self.tab_categories, text="Categorías Existentes:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")
        self.category_list_frame = ctk.CTkScrollableFrame(self.tab_categories, fg_color="gray85")
        self.category_list_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.category_list_frame.grid_columnconfigure(0, weight=1)
        
        self.load_category_list_for_admin()

    def load_category_list_for_admin(self):
        for widget in self.category_list_frame.winfo_children():
            widget.destroy()

        categories = db.get_all_categories()
        if not categories:
            ctk.CTkLabel(self.category_list_frame, text="No hay categorías.").pack(pady=10)
            return
            
        for cat_id, cat_name in categories:
            ctk.CTkLabel(self.category_list_frame, text=f"• {cat_name} (ID: {cat_id})", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=10, pady=2)

    def add_new_category(self):
        cat_name = self.new_category_entry.get().strip()
        if not cat_name:
            messagebox.showwarning("Advertencia", "El nombre de la categoría no puede estar vacío.", parent=self)
            return

        db.add_category(cat_name) 
        self.new_category_entry.delete(0, "end")
        
        self.load_sidebar_categories()
        self.load_category_buttons()
        self.load_category_list_for_admin()
        messagebox.showinfo("Éxito", f"Categoría '{cat_name}' agregada.")
        
    def _setup_password_tab(self):
        self.tab_password.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.tab_password, text="Cambiar Contraseña de Administrador", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(self.tab_password, text="Nueva Contraseña:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")
        self.new_pass_entry = ctk.CTkEntry(self.tab_password, placeholder_text="Contraseña", show="•", width=300)
        self.new_pass_entry.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")
        
        ctk.CTkLabel(self.tab_password, text="Confirmar Contraseña:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")
        self.confirm_pass_entry = ctk.CTkEntry(self.tab_password, placeholder_text="Confirmar", show="•", width=300)
        self.confirm_pass_entry.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="w")

        ctk.CTkButton(self.tab_password, text="Guardar Nueva Contraseña", command=self._change_admin_password, fg_color="#D32F2F", hover_color="#B71C1C").grid(row=5, column=0, padx=20, pady=10, sticky="w")

    def _change_admin_password(self):
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        
        if len(new_pass) < 6:
            messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 6 caracteres.", parent=self)
            return
        if new_pass != confirm_pass:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden.", parent=self)
            return
            
        if db.update_admin_password(self.user_id, new_pass):
            messagebox.showinfo("Éxito", "¡Contraseña cambiada con éxito! Deberás iniciar sesión de nuevo.", parent=self)
            self.new_pass_entry.delete(0, "end")
            self.confirm_pass_entry.delete(0, "end")

    def _setup_users_tab(self):
        self.tab_users.grid_columnconfigure(0, weight=1)
        self.tab_users.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_users, text="Asignación y Eliminación de Administrador", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.user_list_scroll_frame = ctk.CTkScrollableFrame(self.tab_users, fg_color="gray85")
        self.user_list_scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.user_list_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_user_list_for_admin()

    def load_user_list_for_admin(self):
        for widget in self.user_list_scroll_frame.winfo_children():
            widget.destroy()
            
        users = db.get_all_users()
        
        if not users:
            ctk.CTkLabel(self.user_list_scroll_frame, text="No hay usuarios registrados.").pack(pady=10)
            return

        header_frame = ctk.CTkFrame(self.user_list_scroll_frame, fg_color="gray75")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=2)
        header_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(header_frame, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(header_frame, text="Usuario / Email", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(header_frame, text="Acciones", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="e", padx=5)
        
        for i, (uid, username, email, is_admin) in enumerate(users):
            user_frame = ctk.CTkFrame(self.user_list_scroll_frame, fg_color="white")
            user_frame.grid(row=i + 1, column=0, sticky="ew", pady=2, padx=5)
            user_frame.grid_columnconfigure(0, weight=1)
            user_frame.grid_columnconfigure(1, weight=2)
            user_frame.grid_columnconfigure(2, weight=1)
            
            role_text = " (ADMIN)" if is_admin else " (Normal)"
            
            ctk.CTkLabel(user_frame, text=f"{uid}", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
            ctk.CTkLabel(user_frame, text=f"{username}{role_text}\n{email}", anchor="w").grid(row=0, column=1, sticky="w", padx=5)
            
            if uid == self.user_id:
                action_button = ctk.CTkLabel(user_frame, text="TÚ (Admin Actual)", text_color="green")
            elif is_admin:
                action_button = ctk.CTkButton(user_frame, text="Quitar Admin", command=lambda id=uid: self._confirm_demote(id), fg_color="#F44336", hover_color="#D32F2F")
            else:
                action_button = ctk.CTkButton(user_frame, text="Hacer Admin", command=lambda id=uid: self._confirm_promote(id), fg_color="#4CAF50", hover_color="#388E3C")

            action_button.grid(row=0, column=2, sticky="e", padx=5, pady=5)

    def _confirm_promote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea asignar el rol de administrador a este usuario?", parent=self):
            db.promote_user(user_id)
            messagebox.showinfo("Éxito", "Usuario promovido a administrador.", parent=self)
            self.load_user_list_for_admin()

    def _confirm_demote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea quitar el rol de administrador a este usuario?", parent=self):
            all_users = db.get_all_users()
            admin_count = sum(1 for _, _, _, is_admin in all_users if is_admin == 1)
            
            if user_id == self.user_id and admin_count <= 1:
                messagebox.showerror("Error", "No puedes degradarte a ti mismo si eres el único administrador en el sistema.", parent=self)
                return
            
            db.demote_user(user_id)
            messagebox.showinfo("Éxito", "Rol de administrador eliminado.", parent=self)
            self.load_user_list_for_admin()