import oracledb
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, StringVar

DB_USER = "proyectob"
DB_PASS = "proyectob"
DB_DSN = "localhost/XEPDB1"



#Configuración de la conexión Idaly
#DB_USER = "proyecto"
#DB_PASS = "proyecto"
#DB_DSN = "localhost/XEPDB1" 
def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

def user_exists(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, email, password FROM users WHERE email = :email", {"email": email})
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.callproc("add_user", [username, email, password])
        conn.commit()
        messagebox.showinfo("Éxito", "Usuario creado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear usuario: {e}")
    finally:
        cur.close()
        conn.close()

def login_window(root):
    win = Toplevel(root)
    win.title("Login")
    win.geometry("350x250")
    win.configure(bg="#1e1e2f")  # Fondo custom

    # Centrar la ventana
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    Label(win, text="Email:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    email_var = StringVar()
    Entry(win, textvariable=email_var, width=30).pack(pady=5)

    Label(win, text="Contraseña:", bg="#1e1e2f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_var = StringVar()
    Entry(win, textvariable=password_var, show="*", width=30).pack(pady=5)

    def attempt_login():
        correo = email_var.get()
        password_input = password_var.get()
        if not correo or "@gmail.com" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return

        usuario = user_exists(correo)
        if usuario:
            if password_input == usuario[3]:
                messagebox.showinfo("Bienvenido", f"Hola {usuario[1]}")
                win.destroy()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    Button(win, text="Login", command=attempt_login, bg="#61afef", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def register_window(root):
    win = Toplevel(root)
    win.title("Registro")
    win.geometry("350x350")
    win.configure(bg="#2f2f3f")

    # Centrar ventana
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    Label(win, text="Nombre:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    nombre_var = StringVar()
    Entry(win, textvariable=nombre_var, width=30).pack(pady=5)

    Label(win, text="Email:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    email_var = StringVar()
    Entry(win, textvariable=email_var, width=30).pack(pady=5)

    Label(win, text="Contraseña:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_var = StringVar()
    Entry(win, textvariable=password_var, show="*", width=30).pack(pady=5)

    Label(win, text="Confirmar contraseña:", bg="#2f2f3f", fg="white", font=("Arial", 12)).pack(pady=10)
    password_confirm_var = StringVar()
    Entry(win, textvariable=password_confirm_var, show="*", width=30).pack(pady=5)

    def attempt_register():
        nombre = nombre_var.get()
        correo = email_var.get()
        password = password_var.get()
        password_confirm = password_confirm_var.get()

        if not correo or "@gmail.com" not in correo:
            messagebox.showerror("Error", "Correo no válido")
            return
        if user_exists(correo):
            messagebox.showwarning("Aviso", "Email ya existente")
            return
        if password != password_confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        create_user(nombre, correo, password)
        win.destroy()

    Button(win, text="Registrarse", command=attempt_register, bg="#98c379", fg="white", font=("Arial", 12), relief="ridge", bd=3).pack(pady=15)

def main_menu():
    root = tk.Tk()
    root.title("Gestión de Usuarios")
    root.geometry("400x300")
    root.configure(bg="#282c34")

    # Configuración de grid para expandir botones
    root.columnconfigure(0, weight=1)
    for i in range(3):
        root.rowconfigure(i, weight=1)

    # Botones con estilo custom
    btn_login = Button(root, text="Login", command=lambda: login_window(root), bg="#61afef", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_login.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

    btn_register = Button(root, text="Registrarse", command=lambda: register_window(root), bg="#98c379", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_register.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    btn_exit = Button(root, text="Salir", command=root.destroy, bg="#e06c75", fg="white", font=("Arial", 14), relief="ridge", bd=3)
    btn_exit.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
