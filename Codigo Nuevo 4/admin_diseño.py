import customtkinter as ctk
from tkinter import messagebox
# Asumimos que 'db' contiene las funciones de conexión a Oracle que llaman a los procedimientos
import ConexionBDD as db
from PIL import Image
from pathlib import Path
from datetime import datetime

class AdminWindow(ctk.CTkToplevel):
    """
    Ventana de administración rediseñada con barra de navegación lateral.
    Implementación de CRUD (Crear, Leer, Actualizar, Eliminar) completa.
    """
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.master_app = master
        self.user_id = user_id
        # La función get_user_info ya debe existir en ConexionBDD
        self.username = db.get_user_info(user_id) 
        
        self.title("Panel de Administración del Blog")
        self.geometry("1200x750") 
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # --- Paleta de Colores y Fuentes para fácil modificación ---
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

        # Mostrar el frame inicial (el dashboard)
        self.show_frame(self.dashboard_frame)

    # 1. --- ESTRUCTURA PRINCIPAL (SIN MODIFICACIONES) ---

    def _create_sidebar(self):
        """Crea la barra de navegación lateral izquierda con efecto de sombra."""
        shadow_container = ctk.CTkFrame(self, fg_color="#E0E0E0", width=242, corner_radius=0)
        shadow_container.grid(row=0, column=0, sticky="nsw")
        
        sidebar_frame = ctk.CTkFrame(shadow_container, width=240, corner_radius=0, fg_color=self.SIDEBAR_BG)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.grid_propagate(False) 
        sidebar_frame.grid_rowconfigure(7, weight=1) 

        # --- Título con imagen (MÉTODO CORREGIDO Y MÁS SEGURO) ---
        try:
            # Uso de Path para resolver la ruta de manera robusta
            script_path = Path(__file__).parent
            image_path = script_path / "imagenes" / "adorno.png"
            
            original_image = Image.open(image_path)
            
            desired_width = 200
            aspect_ratio = original_image.height / float(original_image.width)
            desired_height = int(desired_width * aspect_ratio)

            resized_image = original_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            
            sidebar_image_obj = ctk.CTkImage(
                light_image=resized_image,
                dark_image=resized_image,
                size=(desired_width, desired_height)
            )
            
            image_label = ctk.CTkLabel(sidebar_frame, text="", image=sidebar_image_obj)
            image_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")

        except Exception as e:
            # Fallback en caso de que la imagen no cargue
            ctk.CTkLabel(sidebar_frame, text="Admin Panel ⚙️", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.PRIMARY_TEXT).grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
        
        # Botones de navegación
        self._create_nav_button(sidebar_frame, "Inicio", lambda: self.show_frame(self.dashboard_frame), row=1)
        self._create_nav_button(sidebar_frame, "Artículos", lambda: self.show_frame(self.articles_frame), row=2)
        self._create_nav_button(sidebar_frame, "Categorías", lambda: self.show_frame(self.categories_frame), row=3)
        self._create_nav_button(sidebar_frame, "Comentarios", lambda: self.show_frame(self.comments_frame), row=4)
        self._create_nav_button(sidebar_frame, "Tags", lambda: self.show_frame(self.tags_frame), row=5)
        self._create_nav_button(sidebar_frame, "Usuarios", lambda: self.show_frame(self.users_frame), row=6)
        
        # Botón para volver, al final
        ctk.CTkButton(
            sidebar_frame, 
            text="Volver al Blog ↩️", 
            command=self.destroy, 
            fg_color="#F44336", 
            hover_color="#D32F2F"
        ).grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
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
        
        # --- FRAMES REALES DE CONTENIDO (NO PLACEHOLDERS) ---
        self.articles_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        # Frame adicional para el formulario de edición/creación de artículos
        self.article_editor_frame = ctk.CTkFrame(self.content_container, fg_color="transparent") 
        self.comments_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tags_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        # --- FIN DE FRAMES REALES ---

        # Configurar el contenido de cada frame
        self._setup_dashboard_content(self.dashboard_frame)
        self._setup_categories_content(self.categories_frame)
        self._setup_users_content(self.users_frame)
        self._setup_profile_content(self.profile_frame)
        self._setup_articles_content(self.articles_frame) # NUEVO: Contenido de Artículos
        self._setup_comments_content(self.comments_frame) # NUEVO: Contenido de Comentarios
        self._setup_tags_content(self.tags_frame)         # NUEVO: Contenido de Tags
        
    def show_frame(self, frame_to_show):
        """Oculta todos los frames y muestra solo el seleccionado."""
        # Asegúrate de incluir el frame de edición de artículos aquí
        all_frames = [
            self.dashboard_frame, self.categories_frame, self.users_frame, 
            self.profile_frame, self.articles_frame, self.article_editor_frame, 
            self.comments_frame, self.tags_frame
        ]
        for frame in all_frames:
            frame.grid_forget()
        frame_to_show.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

    # 2. --- CONTENIDO DE CADA FRAME --- (Artículos, Comentarios, Tags, Categorías CRUD)

    # --- INICIO: LÓGICA DE ARTÍCULOS (CRUD) ---
    def _setup_articles_content(self, parent_frame):
        """Crea la vista de listado de artículos (Read/Delete)."""
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(parent_frame, text="Gestión de Artículos 📝", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        
        # Botón para Crear nuevo artículo
        ctk.CTkButton(
            parent_frame, 
            text="➕ Nuevo Artículo", 
            command=lambda: self.show_article_editor_frame(), # Pasa None para crear
            fg_color="#4CAF50", 
            hover_color="#388E3C"
        ).grid(row=1, column=0, padx=10, pady=(0, 20), sticky="w")
        
        self.articles_list_scrollframe = ctk.CTkScrollableFrame(parent_frame, label_text="Artículos Publicados | ID | Título | Autor | Fecha")
        self.articles_list_scrollframe.grid(row=2, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.articles_list_scrollframe.grid_columnconfigure(0, weight=1)
        
        self.load_admin_articles_list() 

    def load_admin_articles_list(self):
        """Carga la lista de artículos con opciones de editar y eliminar."""
        for widget in self.articles_list_scrollframe.winfo_children():
            widget.destroy()
            
        # db.get_all_articles_for_admin debe retornar (article_id, title, article_date, username)
        articles = db.get_all_articles_for_admin() 

        if not articles:
            ctk.CTkLabel(self.articles_list_scrollframe, text="No hay artículos publicados.").pack(pady=20)
            return

        for i, (article_id, title, date, username) in enumerate(articles):
            row_frame = ctk.CTkFrame(self.articles_list_scrollframe, fg_color="#F9F9F9", corner_radius=5)
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.grid_columnconfigure(0, weight=1)
            
            info_text = f"[{article_id}] {title} - por {username} ({date})"
            ctk.CTkLabel(row_frame, text=info_text, anchor="w", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, sticky="e", padx=5)
            
            ctk.CTkButton(
                action_frame, 
                text="Editar", 
                command=lambda id=article_id: self.show_article_editor_frame(id), 
                width=70, height=28, fg_color="#FFB300", hover_color="#FF8F00"
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                action_frame, 
                text="Eliminar", 
                command=lambda id=article_id: self.handle_delete_article(id), 
                width=70, height=28, fg_color="#E53935", hover_color="#C62828"
            ).pack(side="left", padx=5)

    def show_article_editor_frame(self, article_id=None):
        """Muestra el formulario para crear un artículo nuevo (None) o editar uno existente (ID)."""
        self.show_frame(self.article_editor_frame)
        
        for widget in self.article_editor_frame.winfo_children():
            widget.destroy()
            
        is_editing = article_id is not None
        
        # El frame de edición se adapta mejor al layout de cuadrícula
        self.article_editor_frame.grid_columnconfigure(0, weight=1)
        self.article_editor_frame.grid_rowconfigure(5, weight=1) # El textbox del contenido usa el espacio restante
        
        title_text = "Editar Artículo Existente" if is_editing else "Crear Nuevo Artículo"
        ctk.CTkLabel(self.article_editor_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        # Campos del formulario
        ctk.CTkLabel(self.article_editor_frame, text="Título:", anchor="w").grid(row=1, column=0, padx=10, sticky="w")
        self.article_title_entry = ctk.CTkEntry(self.article_editor_frame, placeholder_text="Título del Artículo")
        self.article_title_entry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Asumimos que hay una variable de instancia para almacenar el ID de la categoría seleccionada
        self.article_category_var = ctk.StringVar(value="")
        categories = db.get_all_categories() # Asume que retorna [(id, nombre)]
        category_map = {name: id for id, name in categories}
        category_names = [name for id, name in categories]
        
        ctk.CTkLabel(self.article_editor_frame, text="Categoría:", anchor="w").grid(row=1, column=1, padx=10, sticky="w")
        self.article_category_combobox = ctk.CTkComboBox(
            self.article_editor_frame, 
            values=category_names, 
            variable=self.article_category_var, 
            width=200
        )
        self.article_category_combobox.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.article_category_combobox.set(category_names[0] if category_names else "Sin Categorías")
        
        ctk.CTkLabel(self.article_editor_frame, text="Contenido:", anchor="w").grid(row=3, column=0, columnspan=2, padx=10, sticky="w")
        self.article_content_textbox = ctk.CTkTextbox(self.article_editor_frame, height=300)
        self.article_content_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        
        # Botones de acción
        action_button_text = "Actualizar Artículo" if is_editing else "Publicar Artículo"
        action_command = lambda: self.handle_save_article(article_id, category_map)
        
        btn_save = ctk.CTkButton(self.article_editor_frame, text=action_button_text, command=action_command, fg_color="#1E88E5", hover_color="#1565C0")
        btn_save.grid(row=5, column=0, padx=10, pady=20, sticky="sw")
        
        btn_cancel = ctk.CTkButton(self.article_editor_frame, text="Cancelar y Volver", command=lambda: self.show_frame(self.articles_frame), fg_color="#757575", hover_color="#616161")
        btn_cancel.grid(row=5, column=0, padx=(200, 10), pady=20, sticky="sw")

        # Cargar datos si se está editando
        if is_editing:
            # db.get_article_details debe retornar (article_id, title, article_text, user_id, article_date, category_id)
            details = db.get_article_details(article_id) 
            if details:
                # La consulta trae 6 campos. Asumimos el orden
                article_id, title, content, user_id, date, category_id = details[0]
                self.article_title_entry.insert(0, title)
                self.article_content_textbox.insert("0.0", content)
                
                # Seleccionar la categoría
                if category_id:
                    # Busca el nombre de la categoría para asignarlo al ComboBox
                    current_category_name = next((name for id, name in categories if id == category_id), None)
                    if current_category_name:
                        self.article_category_combobox.set(current_category_name)
            else:
                messagebox.showerror("Error", "No se encontraron los detalles del artículo.", parent=self)
                self.show_frame(self.articles_frame)

    def handle_save_article(self, article_id, category_map):
        """Maneja la lógica de guardar o actualizar el artículo."""
        title = self.article_title_entry.get().strip()
        # Se obtiene el contenido del CTkTextbox, del inicio ("1.0") al final menos un caracter ("end-1c")
        content = self.article_content_textbox.get("1.0", "end-1c").strip() 
        
        selected_category_name = self.article_category_var.get()
        category_id = category_map.get(selected_category_name)

        if not title or not content:
            messagebox.showwarning("Advertencia", "El título y el contenido son obligatorios.", parent=self)
            return
            
        if article_id:
            # Lógica de Edición
            if db.update_article(article_id, title, content):
                db.update_article_category(article_id, category_id) # Se asume una función para actualizar la relación
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente.", parent=self)
            else:
                messagebox.showerror("Error", "Error al actualizar el artículo.", parent=self)
        else:
            # Lógica de Creación (Se asume que add_article retorna el nuevo ID)
            new_id = db.add_article(title, content, self.user_id) 
            if new_id:
                db.add_article_category(new_id, category_id) # Se asume una función para añadir la relación
                messagebox.showinfo("Éxito", "Artículo publicado correctamente.", parent=self)
            else:
                messagebox.showerror("Error", "Error al crear el artículo.", parent=self)

        self.load_admin_articles_list()
        self.show_frame(self.articles_frame)

    def handle_delete_article(self, article_id):
        """Maneja la eliminación de un artículo."""
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de ELIMINAR el artículo con ID {article_id}? Esto eliminará todo su contenido asociado (comentarios, tags, categorías).", parent=self):
            if db.delete_article(article_id): 
                messagebox.showinfo("Éxito", f"Artículo {article_id} eliminado correctamente.", parent=self)
                self.load_admin_articles_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo. Revise la base de datos.", parent=self)
    # --- FIN: LÓGICA DE ARTÍCULOS (CRUD) ---

    # --- INICIO: LÓGICA DE CATEGORÍAS (CRUD COMPLETO) ---
    def _setup_categories_content(self, parent_frame):
        """ Configuración del contenido de la gestión de categorías (con botones CRUD). """
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(parent_frame, text="Gestión de Categorías 📚", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        
        # Sección de "Agregar" (C)
        entry_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        self.new_category_entry = ctk.CTkEntry(entry_frame, placeholder_text="Nombre de la nueva categoría", height=40)
        self.new_category_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(entry_frame, text="Agregar", command=self.handle_add_category, fg_color=self.ACCENT_COLOR, hover_color="#673AB7", height=40).grid(row=0, column=1)
        
        # Sección de "Listado" (R, U, D)
        ctk.CTkLabel(parent_frame, text="Categorías Existentes (Editar/Eliminar):", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        self.categories_list_scrollframe = ctk.CTkScrollableFrame(parent_frame, label_text="ID | Nombre de Categoría")
        self.categories_list_scrollframe.grid(row=3, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.categories_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_admin_categories_list()

    def load_admin_categories_list(self):
        """Carga la lista de categorías con opciones de edición y eliminación."""
        for widget in self.categories_list_scrollframe.winfo_children():
            widget.destroy()
        
        categories = db.get_all_categories() # Asume que retorna [(id, nombre)]
        
        if not categories:
            ctk.CTkLabel(self.categories_list_scrollframe, text="No hay categorías creadas.").pack(pady=20)
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            row_frame = ctk.CTkFrame(self.categories_list_scrollframe, fg_color="#F9F9F9", corner_radius=5)
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(row_frame, text=f"[{cat_id}] {cat_name}", anchor="w", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, sticky="e", padx=5)
            
            # Botón de Editar (U)
            ctk.CTkButton(
                action_frame, 
                text="Editar", 
                command=lambda id=cat_id, name=cat_name: self.handle_edit_category(id, name), 
                width=70, height=28, fg_color="#FFB300", hover_color="#FF8F00"
            ).pack(side="left", padx=5)
            
            # Botón de Eliminar (D)
            ctk.CTkButton(
                action_frame, 
                text="Eliminar", 
                command=lambda id=cat_id: self.handle_delete_category(id), 
                width=70, height=28, fg_color="#E53935", hover_color="#C62828"
            ).pack(side="left", padx=5)

    def handle_add_category(self):
        """ Maneja la creación de categorías (C). """
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la categoría.", parent=self)
            return
        # admin_add_category debe llamar al procedimiento add_category
        if db.admin_add_category(category_name): 
            messagebox.showinfo("Éxito", f"Categoría '{category_name}' creada.", parent=self)
            self.new_category_entry.delete(0, "end")
            self.load_admin_categories_list()

    def handle_edit_category(self, cat_id, current_name):
        """ Maneja la edición de categorías (U). """
        new_name = ctk.CTkInputDialog(
            text=f"Editando Categoría {cat_id}. Nuevo nombre:", 
            title="Editar Categoría",
            initial_value=current_name
        ).get_input()
        
        if new_name is not None and new_name.strip() and new_name != current_name:
            if db.update_category(cat_id, new_name.strip()): # Llama al procedimiento update_category
                messagebox.showinfo("Éxito", f"Categoría {cat_id} actualizada a '{new_name}'.", parent=self)
                self.load_admin_categories_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la categoría.", parent=self)

    def handle_delete_category(self, cat_id):
        """ Maneja la eliminación de categorías (D). """
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de ELIMINAR la categoría con ID {cat_id}? Esto eliminará las relaciones con artículos.", parent=self):
            if db.delete_category(cat_id): # Llama al procedimiento delete_category
                messagebox.showinfo("Éxito", f"Categoría {cat_id} eliminada correctamente.", parent=self)
                self.load_admin_categories_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la categoría. Revise la base de datos.", parent=self)
    # --- FIN: LÓGICA DE CATEGORÍAS (CRUD COMPLETO) ---

    # --- INICIO: LÓGICA DE COMENTARIOS (READ, DELETE) ---
    def _setup_comments_content(self, parent_frame):
        """ Crea la vista de moderación de comentarios. """
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(parent_frame, text="Gestión de Comentarios 💬", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        
        self.comments_list_scroll_frame = ctk.CTkScrollableFrame(parent_frame, label_text="Comentarios Recientes (Moderación)")
        self.comments_list_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.comments_list_scroll_frame.grid_columnconfigure(0, weight=1)
        self.load_admin_comments_list()

    def load_admin_comments_list(self):
        """ Carga la lista de comentarios para moderación. """
        for widget in self.comments_list_scroll_frame.winfo_children():
            widget.destroy()
            
        # db.get_all_comments_for_admin debe retornar (comment_id, commenter_name, comment_text, article_title, created_at)
        comments = db.get_all_comments_for_admin()
        
        if not comments:
            ctk.CTkLabel(self.comments_list_scroll_frame, text="No hay comentarios que moderar.").pack(pady=20)
            return

        for i, (comment_id, name, text, article_title, created_at) in enumerate(comments):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            
            comment_frame = ctk.CTkFrame(self.comments_list_scroll_frame, fg_color=bg_color, corner_radius=5)
            comment_frame.pack(fill="x", pady=5, padx=5)
            comment_frame.grid_columnconfigure(0, weight=1)
            
            # Título: Comentarista y Artículo
            title_label = ctk.CTkLabel(
                comment_frame, 
                text=f"[{comment_id}] {name} - en artículo: '{article_title}'", 
                anchor="w", 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
            
            # Contenido del comentario
            text_label = ctk.CTkLabel(
                comment_frame, 
                text=text, 
                anchor="w", 
                justify="left", 
                wraplength=650, 
                font=ctk.CTkFont(size=13)
            )
            text_label.grid(row=1, column=0, sticky="w", padx=10, pady=(2, 5))
            
            # Botón de Eliminar
            ctk.CTkButton(
                comment_frame, 
                text="Eliminar 🗑️", 
                command=lambda id=comment_id: self.handle_delete_comment(id), 
                width=80, height=30, 
                fg_color="#D32F2F", hover_color="#B71C1C"
            ).grid(row=0, column=1, rowspan=2, sticky="e", padx=10)

    def handle_delete_comment(self, comment_id):
        """ Maneja la eliminación de un comentario. """
        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar el comentario con ID {comment_id}?", parent=self):
            if db.delete_comment(comment_id): # Llama al procedimiento delete_comment
                messagebox.showinfo("Éxito", f"Comentario {comment_id} eliminado.", parent=self)
                self.load_admin_comments_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el comentario.", parent=self)
    # --- FIN: LÓGICA DE COMENTARIOS (READ, DELETE) ---

    # --- INICIO: LÓGICA DE TAGS (CRUD COMPLETO) ---
    def _setup_tags_content(self, parent_frame):
        """ Configuración del contenido de la gestión de tags. """
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(parent_frame, text="Gestión de Etiquetas (Tags) 🏷️", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        
        # Sección de "Agregar" (C)
        entry_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        self.new_tag_entry = ctk.CTkEntry(entry_frame, placeholder_text="Nombre de la nueva etiqueta", height=40)
        self.new_tag_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(entry_frame, text="Agregar", command=self.handle_add_tag, fg_color=self.ACCENT_COLOR, hover_color="#673AB7", height=40).grid(row=0, column=1)
        
        # Sección de "Listado" (R, U, D)
        ctk.CTkLabel(parent_frame, text="Tags Existentes (Editar/Eliminar):", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        self.tags_list_scrollframe = ctk.CTkScrollableFrame(parent_frame, label_text="ID | Nombre de Etiqueta")
        self.tags_list_scrollframe.grid(row=3, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.tags_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_admin_tags_list()

    def load_admin_tags_list(self):
        """ Carga la lista de tags con opciones de edición y eliminación. """
        for widget in self.tags_list_scrollframe.winfo_children():
            widget.destroy()
        
        tags = db.get_all_tags() # Asume que retorna [(id, nombre)]
        
        if not tags:
            ctk.CTkLabel(self.tags_list_scrollframe, text="No hay etiquetas creadas.").pack(pady=20)
            return

        for i, (tag_id, tag_name) in enumerate(tags):
            row_frame = ctk.CTkFrame(self.tags_list_scrollframe, fg_color="#F9F9F9", corner_radius=5)
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(row_frame, text=f"[{tag_id}] {tag_name}", anchor="w", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, sticky="e", padx=5)
            
            # Botón de Editar (U)
            ctk.CTkButton(
                action_frame, 
                text="Editar", 
                command=lambda id=tag_id, name=tag_name: self.handle_edit_tag(id, name), 
                width=70, height=28, fg_color="#FFB300", hover_color="#FF8F00"
            ).pack(side="left", padx=5)
            
            # Botón de Eliminar (D)
            ctk.CTkButton(
                action_frame, 
                text="Eliminar", 
                command=lambda id=tag_id: self.handle_delete_tag(id), 
                width=70, height=28, fg_color="#E53935", hover_color="#C62828"
            ).pack(side="left", padx=5)

    def handle_add_tag(self):
        """ Maneja la creación de tags (C). """
        tag_name = self.new_tag_entry.get().strip()
        if not tag_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la etiqueta.", parent=self)
            return
        if db.add_tag(tag_name): # Llama al procedimiento add_tag
            messagebox.showinfo("Éxito", f"Etiqueta '{tag_name}' creada.", parent=self)
            self.new_tag_entry.delete(0, "end")
            self.load_admin_tags_list()

    def handle_edit_tag(self, tag_id, current_name):
        """ Maneja la edición de tags (U). """
        new_name = ctk.CTkInputDialog(
            text=f"Editando Etiqueta {tag_id}. Nuevo nombre:", 
            title="Editar Etiqueta",
            initial_value=current_name
        ).get_input()
        
        if new_name is not None and new_name.strip() and new_name != current_name:
            if db.update_tag(tag_id, new_name.strip()): # Llama al procedimiento update_tag
                messagebox.showinfo("Éxito", f"Etiqueta {tag_id} actualizada a '{new_name}'.", parent=self)
                self.load_admin_tags_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la etiqueta.", parent=self)

    def handle_delete_tag(self, tag_id):
        """ Maneja la eliminación de tags (D). """
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de ELIMINAR la etiqueta con ID {tag_id}? Esto eliminará las relaciones con artículos.", parent=self):
            if db.delete_tag(tag_id): # Llama al procedimiento delete_tag
                messagebox.showinfo("Éxito", f"Etiqueta {tag_id} eliminada correctamente.", parent=self)
                self.load_admin_tags_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la etiqueta. Revise la base de datos.", parent=self)
    # --- FIN: LÓGICA DE TAGS (CRUD COMPLETO) ---
    
    # --- LÓGICA DE DASHBOARD, PERFIL Y USUARIOS (Mantenida, con adición de DELETE USER) ---

    def _setup_dashboard_content(self, parent_frame):
        """Crea el contenido del dashboard principal con las tarjetas en formato de lista."""
        parent_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkLabel(parent_frame, text="Bienvenido al Panel de Administración del Blog", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.PRIMARY_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(parent_frame, text="Desde aquí puedes gestionar todos los aspectos de tu blog:", font=ctk.CTkFont(size=16), text_color=self.SECONDARY_TEXT, anchor="w").pack(fill="x", pady=(0, 25))

        cards_container = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=0, pady=0) 
        cards_container.grid_columnconfigure(0, weight=1) 

        self._create_dashboard_card(cards_container, "Artículos", "Gestiona los artículos del blog: crear, editar y eliminar.", lambda: self.show_frame(self.articles_frame))
        self._create_dashboard_card(cards_container, "Categorías", "Organiza tus artículos por categorías.", lambda: self.show_frame(self.categories_frame))
        self._create_dashboard_card(cards_container, "Comentarios", "Modera los comentarios de los lectores.", lambda: self.show_frame(self.comments_frame))
        self._create_dashboard_card(cards_container, "Tags", "Gestiona las etiquetas para tus artículos.", lambda: self.show_frame(self.tags_frame))
        self._create_dashboard_card(cards_container, "Usuarios", "Administra los usuarios del sistema.", lambda: self.show_frame(self.users_frame))

    # --- LÓGICA DE USUARIOS (Mantenida + Botón Eliminar) ---

    def _setup_users_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(parent_frame, text="Gestión de Usuarios y Roles 👥", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        self.user_list_scroll_frame = ctk.CTkScrollableFrame(parent_frame, label_text="Usuarios Registrados")
        self.user_list_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.user_list_scroll_frame.grid_columnconfigure(0, weight=1)
        self.load_user_list_for_admin()

    def load_user_list_for_admin(self):
        for widget in self.user_list_scroll_frame.winfo_children():
            widget.destroy()
        users = db.get_all_users() # Asume que retorna (uid, username, email, is_admin)
        if not users:
            ctk.CTkLabel(self.user_list_scroll_frame, text="No hay usuarios registrados.").pack(pady=10)
            return
        
        for i, (uid, username, email, is_admin) in enumerate(users):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            user_frame = ctk.CTkFrame(self.user_list_scroll_frame, fg_color=bg_color, corner_radius=5)
            user_frame.pack(fill="x", pady=2, padx=5)
            user_frame.grid_columnconfigure(0, weight=1)
            
            role_text = " (ADMIN)" if is_admin else ""
            info_label = ctk.CTkLabel(user_frame, text=f"[{uid}] {username}{role_text} - {email}", anchor="w")
            info_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            actions_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=1, sticky="e", padx=10)
            
            if uid == self.user_id:
                ctk.CTkLabel(actions_frame, text="TÚ", text_color="green", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            elif is_admin:
                ctk.CTkButton(actions_frame, text="Quitar Admin", command=lambda id=uid: self._confirm_demote(id), fg_color="#F44336", hover_color="#D32F2F", width=100, height=30).pack(side="left", padx=5)
            else:
                ctk.CTkButton(actions_frame, text="Hacer Admin", command=lambda id=uid: self._confirm_promote(id), fg_color="#4CAF50", hover_color="#388E3C", width=100, height=30).pack(side="left", padx=5)

            # Botón de eliminar para cualquier usuario excepto uno mismo
            if uid != self.user_id:
                 ctk.CTkButton(actions_frame, text="Eliminar", command=lambda id=uid: self.handle_delete_user(id), fg_color="#616161", hover_color="#424242", width=70, height=30).pack(side="left", padx=5)

    def handle_delete_user(self, user_id):
        """ Maneja la eliminación de un usuario. """
        if messagebox.askyesno("PELIGRO: Eliminar Usuario", f"¿Estás seguro de ELIMINAR al usuario con ID {user_id}? Esto borrará TODOS sus artículos y comentarios.", parent=self):
            if db.delete_user(user_id): # Llama al procedimiento delete_user
                messagebox.showinfo("Éxito", f"Usuario {user_id} y su contenido han sido eliminados.", parent=self)
                self.load_user_list_for_admin()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.", parent=self)
                
    def _confirm_promote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Asignar rol de administrador a este usuario?", parent=self):
            db.promote_user(user_id)
            self.load_user_list_for_admin()

    def _confirm_demote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Quitar rol de administrador a este usuario?", parent=self):
            db.demote_user(user_id)
            self.load_user_list_for_admin()
            
    # --- FIN: LÓGICA DE USUARIOS ---
            
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

    def handle_admin_password_change(self):
        new_pass = self.admin_new_password_entry.get()
        confirm_pass = self.admin_confirm_password_entry.get()
        if not new_pass or not confirm_pass:
            messagebox.showwarning("Advertencia", "Ambos campos de contraseña son obligatorios.", parent=self)
            return
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden.", parent=self)
            return
        # update_admin_password debe llamar al procedimiento update_user_password(self.user_id, new_pass)
        if db.update_admin_password(self.user_id, new_pass): 
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.", parent=self)
            self.admin_new_password_entry.delete(0, "end")
            self.admin_confirm_password_entry.delete(0, "end")

    # --- HELPERS DE UI (SIN MODIFICACIONES) ---

    def _create_nav_button(self, parent, text, command, row):
        """Crea un botón estandarizado para la barra de navegación lateral."""
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color="#F0F0F0",
            text_color=self.PRIMARY_TEXT,
            anchor="w",
            font=ctk.CTkFont(size=16),
            height=45
        )
        button.grid(row=row, column=0, padx=20, pady=4, sticky="ew")
        return button

    def _create_dashboard_card(self, parent, title, description, command):
        """Crea una tarjeta de información moderna para el dashboard en formato de lista."""
        card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        card.pack(fill="x", padx=15, pady=8) 
        
        # --- Habilitar el hover y el click en toda la tarjeta ---
        card.bind("<Enter>", lambda e: card.configure(fg_color="#F9F9F9"))
        card.bind("<Leave>", lambda e: card.configure(fg_color=self.CARD_BG))
        card.bind("<Button-1>", lambda e: command())

        card.grid_columnconfigure(1, weight=1) 
        
        # Contenedor para el texto para que todo sea clickeable
        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)
        text_container.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(text_container, text=title, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.PRIMARY_TEXT, anchor="w")
        title_label.grid(row=0, column=0, sticky="ew")
        
        desc_label = ctk.CTkLabel(text_container, text=description, text_color=self.SECONDARY_TEXT, wraplength=500, anchor="w", justify="left")
        desc_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # --- Hacer que las etiquetas también sean clickeables ---
        title_label.bind("<Button-1>", lambda e: command())
        desc_label.bind("<Button-1>", lambda e: command())
        text_container.bind("<Button-1>", lambda e: command())

        # Flecha para indicar que es un botón
        arrow_label = ctk.CTkLabel(card, text="→", font=ctk.CTkFont(size=24))
        arrow_label.grid(row=0, column=2, padx=20)
        arrow_label.bind("<Button-1>", lambda e: command())