import customtkinter as ctk
from tkinter import messagebox
import ConexionBDD as db
from PIL import Image
from pathlib import Path

class AdminWindow(ctk.CTkToplevel):
    """
    Ventana de administración rediseñada con una barra de navegación lateral vertical,
    inspirada en un diseño moderno con panel izquierdo blanco y tarjetas con sombra.
    Ahora, las tarjetas del dashboard tienen una forma rectangular de lista.
    El título del panel lateral se reemplaza por la imagen "adorno.png".
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

    # 1. --- ESTRUCTURA PRINCIPAL ---

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
            script_path = Path(__file__).parent
            image_path = script_path / "imagenes" / "adorno.png"
            
            # 1. Cargar la imagen original con Pillow
            original_image = Image.open(image_path)
            original_width, original_height = original_image.size

            # 2. Calcular el nuevo alto manteniendo la proporción
            desired_width = 200
            aspect_ratio = original_height / float(original_width)
            desired_height = int(desired_width * aspect_ratio)

            # 3. REDIMENSIONAR la imagen de Pillow ANTES de pasarla a CTkImage
            resized_image = original_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            
            # 4. Crear el CTkImage a partir de la imagen ya redimensionada
            sidebar_image_obj = ctk.CTkImage(
                light_image=resized_image,
                dark_image=resized_image,
                size=(desired_width, desired_height)
            )
            
            image_label = ctk.CTkLabel(sidebar_frame, text="", image=sidebar_image_obj)
            image_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="ew")

        except Exception as e:
            full_path = Path(__file__).parent / "imagenes" / "adorno.png"
            error_msg = f"No se pudo cargar 'adorno.png'.\n\nRuta: {full_path.resolve()}\nError: {e}"
            messagebox.showerror("Error de Imagen", error_msg, parent=self)
            
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
        
        # Frames para funcionalidades futuras
        self.articles_frame = self._create_placeholder_frame("Gestión de Artículos")
        self.comments_frame = self._create_placeholder_frame("Gestión de Comentarios")
        self.tags_frame = self._create_placeholder_frame("Gestión de Etiquetas")

        # Configurar el contenido de cada frame
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

    def _create_placeholder_frame(self, title):
        """Crea un frame genérico para funcionalidades futuras."""
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=24, weight="bold"), text_color=self.PRIMARY_TEXT)
        label.pack(pady=(100,10))
        ctk.CTkLabel(frame, text="(Funcionalidad no implementada en este panel)", font=ctk.CTkFont(size=16), text_color=self.SECONDARY_TEXT).pack()
        return frame
        
    # 3. --- LÓGICA Y HANDLERS ---
    
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