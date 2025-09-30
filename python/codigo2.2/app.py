import customtkinter as ctk
from logindiseño import AuthWindow

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw() 
        
        auth_window = AuthWindow(master=self)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()