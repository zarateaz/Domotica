import cv2, os, json, hashlib, requests, threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet

class RegistroSenati:
    def __init__(self, root):
        self.root = root
        self.root.title("SENATI - REGISTRO DE CREDENCIALES")
        self.root.geometry("500x800")
        self.root.configure(bg="#000a12")
        
        # Rutas de Arch Garuda / Linux
        self.base_path = "/home/zarate/Domotica"
        self.key_path = os.path.join(self.base_path, "master.key")
        self.db_path = os.path.join(self.base_path, "database.json")
        self.rostros_path = os.path.join(self.base_path, "rostros")

        tk.Label(root, text="REGISTRO BIOMÉTRICO AES-256", fg="#00ffcc", bg="#000a12", font=("Courier", 14, "bold")).pack(pady=20)
        self.cam_label = tk.Label(root, bg="black", border=2, relief="solid")
        self.cam_label.pack()

        self.nombre = self.field("NOMBRE COMPLETO:")
        self.pin = self.field("NUEVO PIN (6 DÍGITOS):", True)
        self.mail = self.field("EMAIL DE RECUPERACIÓN:")

        tk.Button(root, text="GENERAR Y ACTUALIZAR", command=self.save, bg="#00ffcc", font=("Arial", 12, "bold"), pady=10).pack(pady=30)

        self.cap = cv2.VideoCapture(0)
        self.update()

    def field(self, t, h=False):
        tk.Label(self.root, text=t, fg="white", bg="#000a12").pack()
        e = tk.Entry(self.root, font=("Arial", 12), show="*" if h else "", width=35, bg="#111", fg="white", insertbackground="white")
        e.pack(pady=5); return e

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            img = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img).resize((380, 280)))
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)
        self.root.after(10, self.update)

    def save(self):
        n, p, m = self.nombre.get().strip().upper(), self.pin.get().strip(), self.mail.get().strip()
        if not n or not p or not m:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        try:
            # 1. Cargar llave AES
            with open(self.key_path, "rb") as f: 
                cipher = Fernet(f.read())

            # 2. Cifrar Rostro
            _, buf = cv2.imencode('.jpg', self.frame)
            with open(os.path.join(self.rostros_path, f"{n}.enc"), "wb") as f:
                f.write(cipher.encrypt(buf.tobytes()))
            
            # 3. Cifrar Email y Hashear PIN
            email_cifrado = cipher.encrypt(m.encode()).decode()
            pin_hash = hashlib.sha256(p.encode()).hexdigest()

            # 4. Manejo Robusto del JSON (Evita el error de char 0)
            db = {}
            if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
                with open(self.db_path, "r") as f:
                    try:
                        db = json.load(f)
                    except json.JSONDecodeError:
                        db = {} # Si el archivo está corrupto, lo reinicia

            db[n] = {"pin": pin_hash, "email": email_cifrado}

            with open(self.db_path, "w") as f:
                json.dump(db, f, indent=4)

            # 5. Notificar al Servidor
            try:
                requests.post("http://127.0.0.1:5000/reload", timeout=2)
                messagebox.showinfo("ZARATE OS", f"Sistema actualizado para {n}")
            except:
                messagebox.showwarning("Aviso", "Guardado local. Reinicia el Main manualmente.")

            self.cap.release(); self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Fallo en el cifrado: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    RegistroSenati(root)
    root.mainloop()
