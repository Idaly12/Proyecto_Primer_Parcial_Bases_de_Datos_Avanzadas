import customtkinter as ctk
from tkinter import messagebox
import ConexionBDD as db
from PIL import Image
from pathlib import Path

class AdminWindow(ctk.CTkToplevel):
    """
    Ventana de administración rediseñada con una barra de navegación lateral vertical,
    inspirada en un diseño moderno con panel izquierdo blanco y tarjetas con sombra.
    """
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.master_app = master
        self.user_id = user_id
        # Variable para saber qué artículo se está editando
        self.editing_article_id = None 
        
        self.title("Panel de Administración del Blog")
        self.geometry("1200x750") 
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # --- Paleta de Colores y Fuentes ---
        self.SIDEBAR_BG = "#FFFFFF"
        self.CONTENT_BG = "#F5F5F5"
        self.CARD_BG = "#FFFFFF"
        self.PRIMARY_TEXT = "#212121"
        self.SECONDARY_TEXT = "#757575"
        self.ACCENT_COLOR = "#7E57C2" 

        # --- Configuración de la cuadrícula principal ---
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # --- Creación de la UI ---
        self._create_sidebar()
        self._create_content_area()
        self._setup_content_frames()

        # Mostrar el frame inicial
        self.show_frame(self.dashboard_frame)

    # 1. --- ESTRUCTURA PRINCIPAL ---

    def _create_sidebar(self):
        """Crea la barra de navegación lateral izquierda con efecto de sombra."""
        shadow_container = ctk.CTkFrame(self, fg_color="#E0E0E0", width=242, corner_radius=0)
        shadow_container.grid(row=0, column=0, sticky="nsw")
        
        sidebar_frame = ctk.CTkFrame(shadow_container, width=240, corner_radius=0, fg_color=self.SIDEBAR_BG)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.grid_propagate(False) 
        sidebar_frame.grid_rowconfigure(7, weight=1) 

        # --- Título con imagen ---
        try:
            script_path = Path(__file__).parent
            image_path = script_path / "imagenes" / "adorno.png"
            original_image = Image.open(image_path)
            original_width, original_height = original_image.size
            desired_width = 200
            aspect_ratio = original_height / float(original_width)
            desired_height = int(desired_width * aspect_ratio)
            resized_image = original_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            sidebar_image_obj = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(desired_width, desired_height))
            image_label = ctk.CTkLabel(sidebar_frame, text="", image=sidebar_image_obj)
            image_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
        except Exception as e:
            full_path = Path(__file__).parent / "imagenes" / "adorno.png"
            error_msg = f"No se pudo cargar 'adorno.png'.\n\nRuta: {full_path.resolve()}\nError: {e}"
            messagebox.showerror("Error de Imagen", error_msg, parent=self)
            ctk.CTkLabel(sidebar_frame, text="Admin Panel ⚙️", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.PRIMARY_TEXT).grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
        
        # --- Botones de navegación ---
        self._create_nav_button(sidebar_frame, "Inicio", lambda: self.show_frame(self.dashboard_frame), row=1)
        self._create_nav_button(sidebar_frame, "Artículos", lambda: self.show_frame(self.articles_frame), row=2)
        self._create_nav_button(sidebar_frame, "Categorías", lambda: self.show_frame(self.categories_frame), row=3)
        self._create_nav_button(sidebar_frame, "Comentarios", lambda: self.show_frame(self.comments_frame), row=4)
        self._create_nav_button(sidebar_frame, "Tags", lambda: self.show_frame(self.tags_frame), row=5)
        self._create_nav_button(sidebar_frame, "Usuarios", lambda: self.show_frame(self.users_frame), row=6)
        
        # --- Botón para volver ---
        ctk.CTkButton(sidebar_frame, text="Volver al Blog ↩️", command=self.destroy, fg_color="#F44336", hover_color="#D32F2F").grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
    def _create_content_area(self):
        """Crea el contenedor principal donde se mostrarán los diferentes frames."""
        self.content_container = ctk.CTkFrame(self, fg_color=self.CONTENT_BG, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _setup_content_frames(self):
        """Inicializa todos los frames de contenido que se usarán."""
        self.dashboard_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.categories_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.users_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.profile_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.comments_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tags_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")

        self.articles_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self._setup_articles_content(self.articles_frame)

        self._setup_dashboard_content(self.dashboard_frame)
        self._setup_categories_content(self.categories_frame)
        self._setup_users_content(self.users_frame)
        self._setup_profile_content(self.profile_frame)
        
    def show_frame(self, frame_to_show):
        """Oculta todos los frames y muestra solo el seleccionado."""
        for frame in [self.dashboard_frame, self.categories_frame, self.users_frame, self.profile_frame, self.articles_frame, self.comments_frame, self.tags_frame]:
            frame.grid_forget()
        frame_to_show.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

    # 2. --- CONTENIDO DE CADA FRAME ---
    
    def _setup_dashboard_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1) 
        ctk.CTkLabel(parent_frame, text="Bienvenido al Panel de Administración", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.PRIMARY_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(parent_frame, text="Desde aquí puedes gestionar todos los aspectos de tu blog.", font=ctk.CTkFont(size=16), text_color=self.SECONDARY_TEXT, anchor="w").pack(fill="x", pady=(0, 25))
        cards_container = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=0, pady=0) 
        cards_container.grid_columnconfigure(0, weight=1) 
        self._create_dashboard_card(cards_container, "Artículos", "Visualiza, edita y elimina los artículos del blog.", lambda: self.show_frame(self.articles_frame))
        self._create_dashboard_card(cards_container, "Categorías", "Organiza tus artículos por categorías.", lambda: self.show_frame(self.categories_frame))
        self._create_dashboard_card(cards_container, "Comentarios", "Modera los comentarios de los lectores.", lambda: self.show_frame(self.comments_frame))
        self._create_dashboard_card(cards_container, "Tags", "Gestiona las etiquetas para tus artículos.", lambda: self.show_frame(self.tags_frame))
        self._create_dashboard_card(cards_container, "Usuarios", "Administra los usuarios del sistema.", lambda: self.show_frame(self.users_frame))

    def _setup_articles_content(self, parent_frame):
        """Crea el contenido del panel de gestión de artículos."""
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1) # Fila para la lista de articulos

        ctk.CTkLabel(parent_frame, text="Gestión de Artículos 📝", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 20))

        # --- Card para EDITAR Artículo (inicialmente oculta) ---
        self.edit_article_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        # No se usa .grid() aquí para que esté oculta por defecto
        
        self.edit_article_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.edit_article_card, text="Editar Artículo", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")
        
        ctk.CTkLabel(self.edit_article_card, text="Título:", anchor="w").grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.article_title_entry = ctk.CTkEntry(self.edit_article_card, height=40)
        self.article_title_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self.edit_article_card, text="Contenido:", anchor="w").grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.article_content_textbox = ctk.CTkTextbox(self.edit_article_card, height=120)
        self.article_content_textbox.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self.edit_article_card, text="Categoría:", anchor="w").grid(row=5, column=0, padx=20, pady=(5, 2), sticky="w")
        categories = db.get_all_categories()
        category_names = [name for id, name in categories] if categories else ["Sin categorías"]
        self.article_category_combo = ctk.CTkComboBox(self.edit_article_card, values=category_names, height=40)
        self.article_category_combo.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")

        btn_frame = ctk.CTkFrame(self.edit_article_card, fg_color="transparent")
        btn_frame.grid(row=6, column=1, padx=20, pady=(0, 20), sticky="e")
        ctk.CTkButton(btn_frame, text="Guardar Cambios", command=self.handle_update_article, height=40, fg_color=self.ACCENT_COLOR, hover_color="#673AB7").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.hide_edit_form, height=40, fg_color="#757575", hover_color="#616161").pack(side="left")

        # --- Card para Listar Artículos ---
        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=2, column=0, sticky="nsew", padx=10, pady=0) # Siempre visible
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_card, text="Lista de Artículos Publicados", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self.articles_list_scrollframe = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.articles_list_scrollframe.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.articles_list_scrollframe.grid_columnconfigure(0, weight=1)

        self.load_articles_list()

    def _setup_categories_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(parent_frame, text="Gestión de Categorías 📚", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        entry_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        self.new_category_entry = ctk.CTkEntry(entry_frame, placeholder_text="Nombre de la nueva categoría", height=40)
        self.new_category_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(entry_frame, text="Agregar", command=self.handle_add_category, fg_color=self.ACCENT_COLOR, hover_color="#673AB7", height=40).grid(row=0, column=1)
        ctk.CTkLabel(parent_frame, text="Categorías Existentes:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        self.categories_list_scrollframe = ctk.CTkScrollableFrame(parent_frame, label_text="ID | Nombre de Categoría")
        self.categories_list_scrollframe.grid(row=3, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.categories_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_admin_categories_list()

    def _setup_profile_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(parent_frame, text="Configuración de Administrador ⚙️", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        ctk.CTkLabel(parent_frame, text="Nueva Contraseña:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")
        self.admin_new_password_entry = ctk.CTkEntry(parent_frame, show="•", placeholder_text="Escribe la nueva contraseña", width=300)
        self.admin_new_password_entry.grid(row=4, column=0, padx=10, sticky="w")
        ctk.CTkLabel(parent_frame, text="Confirmar Nueva Contraseña:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")
        self.admin_confirm_password_entry = ctk.CTkEntry(parent_frame, show="•", placeholder_text="Confirma la nueva contraseña", width=300)
        self.admin_confirm_password_entry.grid(row=6, column=0, padx=10, sticky="w")
        ctk.CTkButton(parent_frame, text="Actualizar Contraseña", command=self.handle_admin_password_change, fg_color="#D32F2F", hover_color="#B71C1C").grid(row=7, column=0, padx=10, pady=30, sticky="w")

    def _setup_users_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(parent_frame, text="Gestión de Usuarios y Roles 👥", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        self.user_list_scroll_frame = ctk.CTkScrollableFrame(parent_frame, label_text="Usuarios Registrados")
        self.user_list_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.user_list_scroll_frame.grid_columnconfigure(0, weight=1)
        self.load_user_list_for_admin()
        
    # 3. --- LÓGICA Y HANDLERS ---
    
    def load_articles_list(self):
        """Carga la lista de artículos llamando al procedimiento de la BDD."""
        for widget in self.articles_list_scrollframe.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.articles_list_scrollframe, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=2); header.grid_columnconfigure(1, weight=1); header.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(header, text="Título", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Categoría", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=2, padx=10)

        try:
            articles = db.get_all_articles_admin() 
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudieron cargar los artículos: {e}", parent=self)
            articles = []

        if not articles:
            ctk.CTkLabel(self.articles_list_scrollframe, text="No hay artículos para mostrar.").pack(pady=30)
            return

        for i, (art_id, title, category) in enumerate(articles):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row = ctk.CTkFrame(self.articles_list_scrollframe, fg_color=bg_color, corner_radius=4)
            row.pack(fill="x", pady=2, padx=5)
            row.grid_columnconfigure(0, weight=2); row.grid_columnconfigure(1, weight=1); row.grid_columnconfigure(2, weight=1)

            ctk.CTkLabel(row, text=title, anchor="w", wraplength=300).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=category, anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
            
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=2, padx=10)
            
            ctk.CTkButton(actions_frame, text="Editar", width=70, fg_color="#1E88E5", hover_color="#1565C0", command=lambda id=art_id: self.show_edit_form(id)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(actions_frame, text="Eliminar", width=70, fg_color="#F44336", hover_color="#D32F2F", command=lambda id=art_id: self.handle_delete_article(id)).pack(side="left")

    def show_edit_form(self, article_id):
        """Muestra el formulario de edición y lo puebla con datos del artículo."""
        try:
            # Obtiene los datos del artículo de la BDD
            article_data = db.get_article_details(article_id) # (title, content, category_id)
            if not article_data:
                messagebox.showerror("Error", "No se encontraron los datos del artículo.", parent=self)
                return
            
            title, content, category_id = article_data
            
            # Limpia y puebla el formulario
            self.article_title_entry.delete(0, "end"); self.article_title_entry.insert(0, title)
            self.article_content_textbox.delete("1.0", "end"); self.article_content_textbox.insert("1.0", content)
            
            # Busca el nombre de la categoría correspondiente al ID
            categories = db.get_all_categories() # Asumiendo que devuelve (id, name)
            category_name = "Sin categorías"
            if categories:
                for cat_id, name in categories:
                    if cat_id == category_id:
                        category_name = name
                        break
            self.article_category_combo.set(category_name)
            
            # Guarda el ID del artículo que se está editando
            self.editing_article_id = article_id
            
            # Muestra el formulario
            self.edit_article_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))

        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudieron cargar los detalles del artículo: {e}", parent=self)

    def hide_edit_form(self):
        """Oculta el formulario de edición y limpia los campos."""
        self.editing_article_id = None
        self.article_title_entry.delete(0, "end")
        self.article_content_textbox.delete("1.0", "end")
        self.edit_article_card.grid_forget()

    def handle_update_article(self):
        """Guarda los cambios del artículo editado en la BDD."""
        if self.editing_article_id is None:
            return

        new_title = self.article_title_entry.get()
        new_content = self.article_content_textbox.get("1.0", "end-1c")
        new_category_name = self.article_category_combo.get()

        if not all([new_title, new_content, new_category_name]):
            messagebox.showwarning("Campos incompletos", "Todos los campos son obligatorios.", parent=self)
            return

        # Obtener el ID de la categoría a partir del nombre
        categories = db.get_all_categories()
        new_category_id = None
        if categories:
            for cat_id, name in categories:
                if name == new_category_name:
                    new_category_id = cat_id
                    break
        
        if new_category_id is None:
            messagebox.showerror("Error", "La categoría seleccionada no es válida.", parent=self)
            return

        try:
            # Llama a la función de BDD para actualizar
            success = db.update_article(self.editing_article_id, new_title, new_content, new_category_id)
            if success:
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente.", parent=self)
                self.hide_edit_form()
                self.load_articles_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el artículo.", parent=self)
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al actualizar: {e}", parent=self)

    def handle_delete_article(self, article_id):
        """Confirma y elimina un artículo llamando al procedimiento de la BDD."""
        if messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que quieres eliminar el artículo con ID {article_id}?", parent=self):
            try:
                success = db.delete_article_by_id(article_id) 
                if success:
                    messagebox.showinfo("Éxito", f"Artículo {article_id} eliminado correctamente.", parent=self)
                    self.hide_edit_form() # Oculta el form si se estaba editando el artículo borrado
                    self.load_articles_list() 
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar el artículo {article_id}.", parent=self)
            except Exception as e:
                messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al eliminar: {e}", parent=self)
    
    def load_admin_categories_list(self):
        for widget in self.categories_list_scrollframe.winfo_children():
            widget.destroy()
        categories = db.get_all_categories()
        if not categories:
            ctk.CTkLabel(self.categories_list_scrollframe, text="No hay categorías creadas.").pack(pady=20)
            return
        for i, (cat_id, cat_name) in enumerate(categories):
            ctk.CTkLabel(self.categories_list_scrollframe, text=f"{cat_id} | {cat_name}", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=10, pady=5)
            
    def handle_add_category(self):
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la categoría.", parent=self)
            return
        if db.admin_add_category(category_name):
            messagebox.showinfo("Éxito", f"Categoría '{category_name}' creada.", parent=self)
            self.new_category_entry.delete(0, "end")
            self.load_admin_categories_list()

    def handle_admin_password_change(self):
        new_pass = self.admin_new_password_entry.get()
        confirm_pass = self.admin_confirm_password_entry.get()
        if not new_pass or not confirm_pass:
            messagebox.showwarning("Advertencia", "Ambos campos de contraseña son obligatorios.", parent=self)
            return
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden.", parent=self)
            return
        if db.update_admin_password(self.user_id, new_pass):
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.", parent=self)
            self.admin_new_password_entry.delete(0, "end")
            self.admin_confirm_password_entry.delete(0, "end")

    def load_user_list_for_admin(self):
        for widget in self.user_list_scroll_frame.winfo_children():
            widget.destroy()
        users = db.get_all_users()
        if not users:
            ctk.CTkLabel(self.user_list_scroll_frame, text="No hay usuarios registrados.").pack(pady=10)
            return
        for i, (uid, username, email, is_admin) in enumerate(users):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            user_frame = ctk.CTkFrame(self.user_list_scroll_frame, fg_color=bg_color, corner_radius=5)
            user_frame.pack(fill="x", pady=2, padx=5)
            user_frame.grid_columnconfigure(1, weight=1)
            
            role_text = " (ADMIN)" if is_admin else ""
            info_label = ctk.CTkLabel(user_frame, text=f"{username}{role_text} - {email}", anchor="w")
            info_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
            
            actions_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=2, sticky="e", padx=10)
            
            if uid == self.user_id:
                ctk.CTkLabel(actions_frame, text="TÚ", text_color="green", font=ctk.CTkFont(weight="bold")).pack()
            elif is_admin:
                ctk.CTkButton(actions_frame, text="Quitar Admin", command=lambda id=uid: self._confirm_demote(id), fg_color="#F44336", hover_color="#D32F2F").pack()
            else:
                ctk.CTkButton(actions_frame, text="Hacer Admin", command=lambda id=uid: self._confirm_promote(id), fg_color="#4CAF50", hover_color="#388E3C").pack()
    
    def _confirm_promote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Asignar rol de administrador a este usuario?", parent=self):
            db.promote_user(user_id)
            self.load_user_list_for_admin()

    def _confirm_demote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Quitar rol de administrador a este usuario?", parent=self):
            db.demote_user(user_id)
            self.load_user_list_for_admin()

    # 4. --- HELPERS DE UI ---
    
    def _create_nav_button(self, parent, text, command, row):
        button = ctk.CTkButton(parent, text=text, command=command, fg_color="transparent", hover_color="#F0F0F0", text_color=self.PRIMARY_TEXT, anchor="w", font=ctk.CTkFont(size=16), height=45)
        button.grid(row=row, column=0, padx=20, pady=4, sticky="ew")
        return button

    def _create_dashboard_card(self, parent, title, description, command):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        card.pack(fill="x", padx=15, pady=8) 
        card.bind("<Enter>", lambda e: card.configure(fg_color="#F9F9F9"))
        card.bind("<Leave>", lambda e: card.configure(fg_color=self.CARD_BG))
        card.bind("<Button-1>", lambda e: command())
        card.grid_columnconfigure(1, weight=1) 
        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)
        text_container.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(text_container, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.PRIMARY_TEXT, anchor="w")
        title_label.grid(row=0, column=0, sticky="ew")
        desc_label = ctk.CTkLabel(text_container, text=description, text_color=self.SECONDARY_TEXT, wraplength=500, anchor="w", justify="left")
        desc_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        title_label.bind("<Button-1>", lambda e: command())
        desc_label.bind("<Button-1>", lambda e: command())
        text_container.bind("<Button-1>", lambda e: command())
        arrow_label = ctk.CTkLabel(card, text="→", font=ctk.CTkFont(size=24))
        arrow_label.grid(row=0, column=2, padx=20)
        arrow_label.bind("<Button-1>", lambda e: command())