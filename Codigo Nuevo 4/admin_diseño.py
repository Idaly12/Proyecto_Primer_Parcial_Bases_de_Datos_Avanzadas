import customtkinter as ctk
from tkinter import messagebox
# Asegúrate de que tu archivo de conexión se llama así
import ConexionBDD as db 
from PIL import Image
from pathlib import Path
from datetime import datetime

class AdminWindow(ctk.CTkToplevel):
    """
    Ventana de administración fusionada.
    """
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.master_app = master
        self.user_id = user_id
        self.username = db.get_user_info(user_id)
        
        self.title("Panel de Administración del Blog")
        self.geometry("1200x750") 
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.editing_article_id = None
        
        # --- Paleta de Colores y Fuentes ---
        self.SIDEBAR_BG = "#FFFFFF"
        self.CONTENT_BG = "#FFFFFF"
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

        try:
            script_path = Path(__file__).parent
            image_path = script_path / "imagenes" / "adorno.png"
            original_image = Image.open(image_path)
            desired_width = 200
            aspect_ratio = original_image.height / float(original_image.width)
            desired_height = int(desired_width * aspect_ratio)
            resized_image = original_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            sidebar_image_obj = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(desired_width, desired_height))
            image_label = ctk.CTkLabel(sidebar_frame, text="", image=sidebar_image_obj)
            image_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
        except Exception as e:
            ctk.CTkLabel(sidebar_frame, text="Admin Panel ⚙️", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.PRIMARY_TEXT).grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")
        
        self._create_nav_button(sidebar_frame, "Inicio", lambda: self.show_frame(self.dashboard_frame), row=1)
        self._create_nav_button(sidebar_frame, "Artículos", lambda: self.show_frame(self.articles_frame), row=2)
        self._create_nav_button(sidebar_frame, "Categorías", lambda: self.show_frame(self.categories_frame), row=3)
        self._create_nav_button(sidebar_frame, "Comentarios", lambda: self.show_frame(self.comments_frame), row=4)
        self._create_nav_button(sidebar_frame, "Tags", lambda: self.show_frame(self.tags_frame), row=5)
        self._create_nav_button(sidebar_frame, "Usuarios", lambda: self.show_frame(self.users_frame), row=6)
        
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
        self._setup_comments_content(self.comments_frame)
        self._setup_tags_content(self.tags_frame)
        
    def show_frame(self, frame_to_show):
        for frame in [self.dashboard_frame, self.categories_frame, self.users_frame, self.profile_frame, self.articles_frame, self.comments_frame, self.tags_frame]:
            frame.grid_forget()
        frame_to_show.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

    # --- SECCIÓN DE ARTÍCULOS ---
    def _setup_articles_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1)
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Gestión de Artículos 📝", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w")
        self.edit_article_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        self.edit_article_card.grid_columnconfigure(0, weight=1)
        self.edit_article_label = ctk.CTkLabel(self.edit_article_card, text="Editando Artículo", font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
        self.edit_article_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")
        ctk.CTkLabel(self.edit_article_card, text="Título:", anchor="w").grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.article_title_entry = ctk.CTkEntry(self.edit_article_card, placeholder_text="El título de tu increíble artículo", height=40)
        self.article_title_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(self.edit_article_card, text="Contenido:", anchor="w").grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.article_content_textbox = ctk.CTkTextbox(self.edit_article_card, height=120)
        self.article_content_textbox.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.category_map = {}
        categories = db.get_all_categories()
        category_names = [name for cat_id, name in categories] if categories else ["Sin categorías"]
        if categories: self.category_map = {name: cat_id for cat_id, name in categories}
        ctk.CTkLabel(self.edit_article_card, text="Categoría:", anchor="w").grid(row=5, column=0, padx=20, pady=(5, 2), sticky="w")
        self.article_category_combo = ctk.CTkComboBox(self.edit_article_card, values=category_names, height=40)
        self.article_category_combo.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        btn_frame = ctk.CTkFrame(self.edit_article_card, fg_color="transparent")
        btn_frame.grid(row=6, column=1, padx=20, pady=(0, 20), sticky="e")
        ctk.CTkButton(btn_frame, text="Actualizar", command=self.handle_save_article, height=40, fg_color=self.ACCENT_COLOR, hover_color="#673AB7").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.hide_edit_article_form, height=40, fg_color="#757575", hover_color="#616161").pack(side="left")
        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_card, text="Lista de Artículos", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        self.articles_list_scrollframe = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.articles_list_scrollframe.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.articles_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_articles_list()

    def load_articles_list(self):
        for widget in self.articles_list_scrollframe.winfo_children():
            widget.destroy()
        header = ctk.CTkFrame(self.articles_list_scrollframe, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=2); header.grid_columnconfigure(1, weight=1); header.grid_columnconfigure(2, weight=1); header.grid_columnconfigure(3, minsize=180)
        ctk.CTkLabel(header, text="Título", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Autor", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Fecha", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=3)
        articles = db.get_all_articles_for_admin()
        if not articles:
            ctk.CTkLabel(self.articles_list_scrollframe, text="No hay artículos para mostrar.").pack(pady=30)
            return
        for i, (art_id, title, date, username) in enumerate(articles):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row = ctk.CTkFrame(self.articles_list_scrollframe, fg_color=bg_color, corner_radius=4)
            row.pack(fill="x", pady=2, padx=5)
            row.grid_columnconfigure(0, weight=2); row.grid_columnconfigure(1, weight=1); row.grid_columnconfigure(2, weight=1); row.grid_columnconfigure(3, minsize=180)
            ctk.CTkLabel(row, text=title, anchor="w", wraplength=300).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=username, anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=date, anchor="w").grid(row=0, column=2, padx=10, pady=8, sticky="w")
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=3, padx=10)
            ctk.CTkButton(actions_frame, text="Editar", width=70, fg_color="#1E88E5", hover_color="#1565C0", command=lambda id=art_id: self.show_edit_article_form(id)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(actions_frame, text="Eliminar", width=70, fg_color="#F44336", hover_color="#D32F2F", command=lambda id=art_id: self.handle_delete_article(id)).pack(side="left")

    def show_edit_article_form(self, article_id):
        details = db.get_article_details(article_id)
        if not details:
            messagebox.showerror("Error", "No se pudieron obtener los detalles del artículo.", parent=self)
            return
        _id, title, content, _user_id, _date, category_id = details[0]
        self.clear_article_form()
        self.editing_article_id = article_id
        self.article_title_entry.insert(0, title)
        self.article_content_textbox.insert("1.0", content)
        current_category_name = "Sin categorías"
        if category_id:
            id_to_name_map = {v: k for k, v in self.category_map.items()}
            current_category_name = id_to_name_map.get(category_id, "Sin categorías")
        self.article_category_combo.set(current_category_name)
        self.edit_article_label.configure(text=f"Editando Artículo: {title}")
        self.edit_article_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))

    def hide_edit_article_form(self):
        self.edit_article_card.grid_forget()
        self.clear_article_form()

    def clear_article_form(self):
        self.editing_article_id = None
        self.article_title_entry.delete(0, "end")
        self.article_content_textbox.delete("1.0", "end")
        if self.article_category_combo.cget("values"):
            self.article_category_combo.set(self.article_category_combo.cget("values")[0])

    def handle_save_article(self):
        if self.editing_article_id is None: return
        title = self.article_title_entry.get().strip()
        content = self.article_content_textbox.get("1.0", "end-1c").strip()
        selected_category_name = self.article_category_combo.get()
        category_id = self.category_map.get(selected_category_name)
        if not title or not content:
            messagebox.showwarning("Campos incompletos", "El título y el contenido son obligatorios.", parent=self)
            return
        if db.update_article(self.editing_article_id, title, content):
            db.update_article_category(self.editing_article_id, category_id)
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente.", parent=self)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el artículo.", parent=self)
        self.hide_edit_article_form()
        self.load_articles_list()
    
    def handle_delete_article(self, article_id):
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de ELIMINAR el artículo ID {article_id}?\nEsto es permanente y borrará su contenido asociado.", parent=self):
            if db.delete_article(article_id):
                messagebox.showinfo("Éxito", f"Artículo {article_id} eliminado.", parent=self)
                self.load_articles_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo.", parent=self)
    
    # 3. --- RESTO DE SECCIONES ---
    
    def _setup_dashboard_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1) 
        ctk.CTkLabel(parent_frame, text="Bienvenido al Panel de Administración", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.PRIMARY_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(parent_frame, text="Gestiona todos los aspectos de tu blog:", font=ctk.CTkFont(size=16), text_color=self.SECONDARY_TEXT, anchor="w").pack(fill="x", pady=(0, 25))
        cards_container = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=0, pady=0) 
        cards_container.grid_columnconfigure(0, weight=1) 
        self._create_dashboard_card(cards_container, "Artículos", "Edita y elimina los artículos del blog.", lambda: self.show_frame(self.articles_frame))
        self._create_dashboard_card(cards_container, "Categorías", "Organiza tus artículos por categorías.", lambda: self.show_frame(self.categories_frame))
        self._create_dashboard_card(cards_container, "Comentarios", "Modera los comentarios de los lectores.", lambda: self.show_frame(self.comments_frame))
        self._create_dashboard_card(cards_container, "Tags", "Gestiona las etiquetas para tus artículos.", lambda: self.show_frame(self.tags_frame))
        self._create_dashboard_card(cards_container, "Usuarios", "Administra los usuarios del sistema.", lambda: self.show_frame(self.users_frame))

    # --- SECCIÓN DE CATEGORÍAS ---
    def _setup_categories_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1) 
        ctk.CTkLabel(parent_frame, text="Gestión de Categorías 📚", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(0,20))
        add_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        add_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))
        add_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(add_card, text="Agregar Nueva Categoría", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")
        ctk.CTkLabel(add_card, text="Nombre:", anchor="w").grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.new_category_entry = ctk.CTkEntry(add_card, placeholder_text="Nombre de la nueva categoría", height=40)
        self.new_category_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        buttons_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))
        ctk.CTkButton(buttons_frame, text="Guardar", command=self.handle_add_category, height=40, fg_color=self.ACCENT_COLOR, hover_color="#673AB7").pack(side="left", padx=(0, 10))
        ctk.CTkButton(buttons_frame, text="Cancelar", command=lambda: self.new_category_entry.delete(0, 'end'), height=40, fg_color="#757575", hover_color="#616161").pack(side="left")
        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_card, text="Lista de Categorías", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        self.categories_list_scrollframe = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.categories_list_scrollframe.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.categories_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_admin_categories_list()

    def load_admin_categories_list(self):
        for widget in self.categories_list_scrollframe.winfo_children():
            widget.destroy()
        header = ctk.CTkFrame(self.categories_list_scrollframe, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=1); header.grid_columnconfigure(1, minsize=180) 
        ctk.CTkLabel(header, text="Nombre", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=1)
        categories = db.get_all_categories()
        if not categories:
            ctk.CTkLabel(self.categories_list_scrollframe, text="No hay categorías creadas.").pack(pady=20)
            return
        for i, (cat_id, cat_name) in enumerate(categories):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row_frame = ctk.CTkFrame(self.categories_list_scrollframe, fg_color=bg_color, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=5)
            row_frame.grid_columnconfigure(0, weight=1); row_frame.grid_columnconfigure(1, minsize=180)
            ctk.CTkLabel(row_frame, text=cat_name, anchor="w", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, sticky="e", padx=10)
            ctk.CTkButton(action_frame, text="Editar", width=70, fg_color="#1E88E5", hover_color="#1565C0", command=lambda id=cat_id, name=cat_name: self.handle_edit_category(id, name)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(action_frame, text="Eliminar", width=70, fg_color="#F44336", hover_color="#D32F2F", command=lambda id=cat_id: self.handle_delete_category(id)).pack(side="left")

    def handle_add_category(self):
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la categoría.", parent=self)
            return
        if db.admin_add_category(category_name):
            messagebox.showinfo("Éxito", f"Categoría '{category_name}' creada.", parent=self)
            self.new_category_entry.delete(0, "end")
            self.load_admin_categories_list()

    def handle_edit_category(self, cat_id, current_name):
        dialog = ctk.CTkInputDialog(text=f"Editando Categoría. Nuevo nombre:", title="Editar Categoría")
        dialog.entry.insert(0, current_name)
        new_name = dialog.get_input()
        if new_name and new_name.strip() and new_name.strip() != current_name:
            if db.update_category(cat_id, new_name.strip()):
                messagebox.showinfo("Éxito", f"Categoría actualizada a '{new_name}'.", parent=self)
                self.load_admin_categories_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la categoría.", parent=self)

    def handle_delete_category(self, cat_id):
        if messagebox.askyesno("Confirmar", f"¿Eliminar la categoría con ID {cat_id}?", parent=self):
            if db.delete_category(cat_id):
                messagebox.showinfo("Éxito", f"Categoría {cat_id} eliminada.", parent=self)
                self.load_admin_categories_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la categoría.", parent=self)

    # --- SECCIÓN DE COMENTARIOS MODIFICADA ---
    def _setup_comments_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1) 

        ctk.CTkLabel(parent_frame, text="Gestión de Comentarios 💬", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(0,20))

        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_card, text="Lista de Comentarios", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self.comments_list_scrollframe = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.comments_list_scrollframe.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.comments_list_scrollframe.grid_columnconfigure(0, weight=1)
        
        self.load_admin_comments_list()

    def load_admin_comments_list(self):
        for widget in self.comments_list_scrollframe.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.comments_list_scrollframe, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=0, minsize=60) # ID
        header.grid_columnconfigure(1, weight=1)             # Autor
        header.grid_columnconfigure(2, weight=2)             # Comentario
        header.grid_columnconfigure(3, weight=1)             # Artículo
        header.grid_columnconfigure(4, weight=0, minsize=100) # Fecha
        header.grid_columnconfigure(5, weight=0, minsize=80) # Acciones
        
        ctk.CTkLabel(header, text="ID", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Autor", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Comentario", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Artículo", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Fecha", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=4, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=5, padx=10)

        comments = db.get_all_comments_for_admin()
        if not comments:
            ctk.CTkLabel(self.comments_list_scrollframe, text="No hay comentarios que moderar.").pack(pady=30)
            return

        for i, (comment_id, name, text, article_title, created_at) in enumerate(comments):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row_frame = ctk.CTkFrame(self.comments_list_scrollframe, fg_color=bg_color, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=5)
            row_frame.grid_columnconfigure(0, weight=0, minsize=60)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=1)
            row_frame.grid_columnconfigure(4, weight=0, minsize=100)
            row_frame.grid_columnconfigure(5, weight=0, minsize=80)

            ctk.CTkLabel(row_frame, text=str(comment_id), anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=name, anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=text, anchor="w", wraplength=250).grid(row=0, column=2, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=article_title, anchor="w", wraplength=150).grid(row=0, column=3, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=created_at.strftime('%Y-%m-%d'), anchor="w").grid(row=0, column=4, padx=10, pady=8, sticky="w")
            
            ctk.CTkButton(row_frame, text="Eliminar", command=lambda id=comment_id: self.handle_delete_comment(id), width=70, fg_color="#F44336", hover_color="#D32F2F", height=30).grid(row=0, column=5, padx=10, sticky="e")


    def handle_delete_comment(self, comment_id):
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de ELIMINAR el comentario ID {comment_id}?", parent=self):
            if db.delete_comment(comment_id):
                messagebox.showinfo("Éxito", f"Comentario {comment_id} eliminado.", parent=self)
                self.load_admin_comments_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el comentario.", parent=self)
    
    # --- SECCIÓN DE TAGS ---
    def _setup_tags_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(parent_frame, text="Gestión de Etiquetas (Tags) 🏷️", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(0,20))
        add_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        add_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))
        add_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(add_card, text="Agregar Nueva Etiqueta", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")
        ctk.CTkLabel(add_card, text="Nombre:", anchor="w").grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.new_tag_entry = ctk.CTkEntry(add_card, placeholder_text="Nombre de la nueva etiqueta", height=40)
        self.new_tag_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        buttons_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))
        ctk.CTkButton(buttons_frame, text="Guardar", command=self.handle_add_tag, height=40, fg_color=self.ACCENT_COLOR, hover_color="#673AB7").pack(side="left", padx=(0, 10))
        ctk.CTkButton(buttons_frame, text="Cancelar", command=lambda: self.new_tag_entry.delete(0, 'end'), height=40, fg_color="#757575", hover_color="#616161").pack(side="left")
        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_card, text="Lista de Etiquetas", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        self.tags_list_scrollframe = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.tags_list_scrollframe.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.tags_list_scrollframe.grid_columnconfigure(0, weight=1)
        self.load_admin_tags_list()

    def load_admin_tags_list(self):
        for widget in self.tags_list_scrollframe.winfo_children():
            widget.destroy()
        header = ctk.CTkFrame(self.tags_list_scrollframe, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=1); header.grid_columnconfigure(1, minsize=180) 
        ctk.CTkLabel(header, text="Nombre", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=1)
        tags = db.get_all_tags()
        if not tags:
            ctk.CTkLabel(self.tags_list_scrollframe, text="No hay etiquetas creadas.").pack(pady=20)
            return
        for i, (tag_id, tag_name) in enumerate(tags):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row_frame = ctk.CTkFrame(self.tags_list_scrollframe, fg_color=bg_color, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=5)
            row_frame.grid_columnconfigure(0, weight=1); row_frame.grid_columnconfigure(1, minsize=180)
            ctk.CTkLabel(row_frame, text=tag_name, anchor="w", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=1, sticky="e", padx=10)
            ctk.CTkButton(action_frame, text="Editar", width=70, fg_color="#1E88E5", hover_color="#1565C0", command=lambda id=tag_id, name=tag_name: self.handle_edit_tag(id, name)).pack(side="left", padx=(0, 5))
            ctk.CTkButton(action_frame, text="Eliminar", width=70, fg_color="#F44336", hover_color="#D32F2F", command=lambda id=tag_id: self.handle_delete_tag(id)).pack(side="left")

    def handle_add_tag(self):
        tag_name = self.new_tag_entry.get().strip()
        if not tag_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la etiqueta.", parent=self)
            return
        if db.add_tag(tag_name):
            messagebox.showinfo("Éxito", f"Etiqueta '{tag_name}' creada.", parent=self)
            self.new_tag_entry.delete(0, "end")
            self.load_admin_tags_list()

    def handle_edit_tag(self, tag_id, current_name):
        dialog = ctk.CTkInputDialog(text=f"Editando Etiqueta {tag_id}. Nuevo nombre:", title="Editar Etiqueta")
        dialog.entry.insert(0, current_name)
        new_name = dialog.get_input()
        if new_name and new_name.strip() and new_name.strip() != current_name:
            if db.update_tag(tag_id, new_name.strip()):
                messagebox.showinfo("Éxito", f"Etiqueta {tag_id} actualizada a '{new_name}'.", parent=self)
                self.load_admin_tags_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la etiqueta.", parent=self)

    def handle_delete_tag(self, tag_id):
        if messagebox.askyesno("Confirmar", f"¿Eliminar la etiqueta con ID {tag_id}?", parent=self):
            if db.delete_tag(tag_id):
                messagebox.showinfo("Éxito", f"Etiqueta {tag_id} eliminada.", parent=self)
                self.load_admin_tags_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la etiqueta.", parent=self)
    
    # --- SECCIÓN DE USUARIOS ---
    def _setup_users_content(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(parent_frame, text="Gestión de Usuarios y Roles 👥", font=ctk.CTkFont(size=24, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=(0,20))

        list_card = ctk.CTkFrame(parent_frame, fg_color=self.CARD_BG, border_width=1, border_color="#E0E0E0", corner_radius=12)
        list_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_card, text="Lista de Usuarios", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self.user_list_scroll_frame = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.user_list_scroll_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.user_list_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_user_list_for_admin()

    def load_user_list_for_admin(self):
        for widget in self.user_list_scroll_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.user_list_scroll_frame, fg_color="#F5F5F5", height=40)
        header.pack(fill="x", pady=(0, 5), padx=5)
        header.grid_columnconfigure(0, weight=0, minsize=60)  # ID
        header.grid_columnconfigure(1, weight=2)              # Nombre
        header.grid_columnconfigure(2, weight=3)              # Email
        header.grid_columnconfigure(3, weight=0, minsize=220) # Acciones
        
        ctk.CTkLabel(header, text="ID", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Nombre", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Email", font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Acciones", font=ctk.CTkFont(weight="bold"), anchor="center").grid(row=0, column=3, padx=10)

        users = db.get_all_users()
        if not users:
            ctk.CTkLabel(self.user_list_scroll_frame, text="No hay usuarios registrados.").pack(pady=20)
            return

        for i, (uid, username, email, is_admin) in enumerate(users):
            bg_color = "#FFFFFF" if i % 2 == 0 else "#FAFAFA"
            row_frame = ctk.CTkFrame(self.user_list_scroll_frame, fg_color=bg_color, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=5)
            row_frame.grid_columnconfigure(0, weight=0, minsize=60)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=0, minsize=220)

            role_text = " (Admin)" if is_admin else ""
            
            ctk.CTkLabel(row_frame, text=str(uid), anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=username + role_text, anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row_frame, text=email, anchor="w").grid(row=0, column=2, padx=10, pady=8, sticky="w")
            
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=3, padx=10)

            if uid == self.user_id:
                ctk.CTkLabel(actions_frame, text="TÚ", text_color="green", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            elif is_admin:
                ctk.CTkButton(actions_frame, text="Quitar Admin", command=lambda id=uid: self._confirm_demote(id), fg_color="#FF9800", hover_color="#F57C00", width=100, height=30).pack(side="left", padx=5)
            else:
                ctk.CTkButton(actions_frame, text="Hacer Admin", command=lambda id=uid: self._confirm_promote(id), fg_color="#4CAF50", hover_color="#388E3C", width=100, height=30).pack(side="left", padx=5)
            
            if uid != self.user_id:
                ctk.CTkButton(actions_frame, text="Eliminar", command=lambda id=uid: self.handle_delete_user(id), fg_color="#F44336", hover_color="#D32F2F", width=70, height=30).pack(side="left", padx=5)

    def handle_delete_user(self, user_id):
        if messagebox.askyesno("PELIGRO", f"¿Eliminar al usuario ID {user_id}?\nSe borrarán TODOS sus artículos y comentarios.", parent=self):
            if db.delete_user(user_id):
                messagebox.showinfo("Éxito", f"Usuario {user_id} eliminado.", parent=self)
                self.load_user_list_for_admin()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.", parent=self)
                
    def _confirm_promote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Asignar rol de administrador?", parent=self):
            db.promote_user(user_id)
            self.load_user_list_for_admin()

    def _confirm_demote(self, user_id):
        if messagebox.askyesno("Confirmar", "¿Quitar rol de administrador?", parent=self):
            db.demote_user(user_id)
            self.load_user_list_for_admin()
            
    # --- SECCIÓN DE PERFIL ---
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
            messagebox.showwarning("Advertencia", "Ambos campos son obligatorios.", parent=self)
            return
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=self)
            return
        if db.update_admin_password(self.user_id, new_pass): 
            messagebox.showinfo("Éxito", "Contraseña actualizada.", parent=self)
            self.admin_new_password_entry.delete(0, "end")
            self.admin_confirm_password_entry.delete(0, "end")

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