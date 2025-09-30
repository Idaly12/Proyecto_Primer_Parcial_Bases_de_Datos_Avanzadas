import customtkinter as ctk
from logindiseño import AuthWindow

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Ocultamos la ventana raíz principal al inicio
        self.withdraw() 
        
        # Abrimos la ventana de login
        auth_window = AuthWindow(master=self)
        auth_window.mainloop()

if __name__ == "__main__":
    app = MainApplication()