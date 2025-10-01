import customtkinter as ctk
from tkinter import messagebox
import ConexionBDD as db
from artCategorias_diseño import BlogApp 

class AdminWindow(ctk.CTkToplevel):
    """Ventana dedicada para la administración de categorías y perfil de administrador."""
    def __init__(self, master, user_id):
        super().__init__(master=master)
        self.master_app = master
        self.user_id = user_id
        self.username = db.get_user_info(user_id)
        
        self.title("Panel de Administración")
        self.geometry("900x700")
        self.resizable(False, False)
        
        # Si el administrador cierra esta ventana, se destruye solo esta, pero el app principal sigue vivo
        self.protocol("WM_DELETE_WINDOW", self.destroy) 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_main_panel()

    def _create_header(self):
        header_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#5D0C0C")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text=f"Panel Admin | {self.username}", 
                     font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color="white").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        ctk.CTkButton(header_frame, text="Volver al Blog ↩️", 
                      command=self.open_blog_view, fg_color="#D32F2F", 
                      hover_color="#B71C1C").grid(row=0, column=1, padx=20, sticky="e")
        
    def _create_main_panel(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.admin_tabview = ctk.CTkTabview(self.main_frame)
        self.admin_tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_categories = self.admin_tabview.add("Gestión de Categorías 📚")
        self.tab_profile = self.admin_tabview.add("Configuración Admin ⚙️")
        
        self._setup_category_tab(self.tab_categories)
        self._setup_admin_profile_tab(self.tab_profile)

    # --- TABS SETUP ---
    
    def _setup_category_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

        # 1. Sección para AGREGAR CATEGORÍA
        ctk.CTkLabel(tab, text="Agregar Nueva Categoría:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        entry_frame = ctk.CTkFrame(tab, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)
        
        self.new_category_entry = ctk.CTkEntry(entry_frame, placeholder_text="Nombre de la Categoría (Ej: Platos Principales)", height=40)
        self.new_category_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkButton(entry_frame, text="Agregar", command=self.handle_add_category, fg_color="#0066CC", hover_color="#0052A3", height=40).grid(row=0, column=1)

        # 2. Sección para LISTAR CATEGORÍAS
        ctk.CTkLabel(tab, text="Categorías Existentes:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.categories_list_scrollframe = ctk.CTkScrollableFrame(tab, label_text="ID | Nombre de Categoría")
        self.categories_list_scrollframe.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.categories_list_scrollframe.grid_columnconfigure(0, weight=1)
        
        self.load_admin_categories_list()

    def _setup_admin_profile_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        
        # Configuración de Contraseña
        ctk.CTkLabel(tab, text="Cambio de Contraseña de Administrador", 
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        ctk.CTkLabel(tab, text="Contraseña Actual (Para Confirmar):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        self.admin_current_password_entry = ctk.CTkEntry(tab, show="•", placeholder_text="Contraseña actual", width=300)
        self.admin_current_password_entry.grid(row=2, column=0, padx=20, sticky="w")
        
        ctk.CTkLabel(tab, text="Nueva Contraseña:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        self.admin_new_password_entry = ctk.CTkEntry(tab, show="•", placeholder_text="Escribe la nueva contraseña", width=300)
        self.admin_new_password_entry.grid(row=4, column=0, padx=20, sticky="w")

        ctk.CTkLabel(tab, text="Confirmar Nueva Contraseña:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        self.admin_confirm_password_entry = ctk.CTkEntry(tab, show="•", placeholder_text="Confirma la nueva contraseña", width=300)
        self.admin_confirm_password_entry.grid(row=6, column=0, padx=20, sticky="w")
        
        ctk.CTkButton(tab, text="Actualizar Contraseña", 
                      command=self.handle_admin_password_change, # Función a implementar en DB
                      fg_color="#D32F2F", hover_color="#B71C1C").grid(row=7, column=0, padx=20, pady=30, sticky="w")

    # --- LOGIC HANDLERS ---
    
    def load_admin_categories_list(self):
        """Carga la lista de categorías en la pestaña de administración."""
        for widget in self.categories_list_scrollframe.winfo_children():
            widget.destroy()
            
        categories = db.get_all_categories()
        
        if not categories:
            ctk.CTkLabel(self.categories_list_scrollframe, text="No hay categorías creadas.").pack(pady=20)
            return

        for i, (cat_id, cat_name) in enumerate(categories):
            cat_label = ctk.CTkLabel(self.categories_list_scrollframe, 
                                     text=f"{cat_id} | {cat_name}", 
                                     anchor="w", font=ctk.CTkFont(size=14),
                                     fg_color="gray90" if i % 2 == 0 else "white")
            cat_label.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            
    def handle_add_category(self):
        """Maneja la adición de una categoría llamando a la función de DB."""
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para la categoría.", parent=self)
            return
            
        if db.admin_add_category(category_name):
            self.new_category_entry.delete(0, "end")
            self.load_admin_categories_list() # Recargar lista en Admin Panel
            
            # Notificar al usuario normal (BlogApp) para que actualice la barra lateral y el frame de subida
            if hasattr(self.master_app, 'blog_app_instance') and self.master_app.blog_app_instance:
                 self.master_app.blog_app_instance.load_sidebar_categories()
                 self.master_app.blog_app_instance.load_category_buttons()
        # db.admin_add_category ya muestra messagebox si hay error.

    def handle_admin_password_change(self):
        """Lógica stub para cambiar la contraseña del administrador."""
        current_pass = self.admin_current_password_entry.get()
        new_pass = self.admin_new_password_entry.get()
        confirm_pass = self.admin_confirm_password_entry.get()

        if not all([current_pass, new_pass, confirm_pass]):
            messagebox.showwarning("Advertencia", "Todos los campos de contraseña son obligatorios.", parent=self)
            return
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden.", parent=self)
            return
            
        # IMPORTANTE: Aquí deberías llamar a una función de DB (ej: db.update_admin_password(self.user_id, current_pass, new_pass))
        # Como esa función aún no existe en ConexionBDD.py, solo mostramos un mensaje.
        messagebox.showinfo("Simulación", "Funcionalidad de cambio de contraseña simulada. ¡Implementa la función en tu DB!", parent=self)
        self.admin_current_password_entry.delete(0, "end")
        self.admin_new_password_entry.delete(0, "end")
        self.admin_confirm_password_entry.delete(0, "end")


    def open_blog_view(self):
        """Cierra la ventana de administración."""
        self.destroy() 
        # Si quisieras reabrir la BlogApp si fue cerrada, la lógica se pondría aquí.
        # Ya que BlogApp se abre solo si no es admin, no necesitamos reabrirla.
