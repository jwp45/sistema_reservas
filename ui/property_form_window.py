import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os

from controllers.database import Database
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "inmuebles")


class PropertyFormWindow:
    def __init__(self, master):
        self.master = master
        self.imagen_path = ""

        self.window = tk.Toplevel(master)
        self.window.title("Agregar Inmueble")
        self.window.geometry("500x550")

        form_frame = ttk.Frame(self.window)
        form_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        ttk.Label(form_frame, text="Ingrese los datos del inmueble", font=('Arial', 14)).pack(pady=5)

        self.fields = {
            "nombre": tk.StringVar(),
            "cantidad_personas": tk.StringVar(),
            "direccion": tk.StringVar(),
            "localidad": tk.StringVar(),
            "provincia": tk.StringVar(),
            "tipo": tk.StringVar(),
            "valor_dia": tk.StringVar()
        }

        fields_order = [
            ("Nombre:", "nombre"),
            ("Cantidad:", "cantidad_personas"),
            ("Dirección:", "direccion"),
            ("Localidad:", "localidad"),
            ("Provincia:", "provincia"),
            ("Tipo:", "tipo"),
            ("Valor por Día:", "valor_dia")
        ]

        for label_text, field_name in fields_order:
            row = ttk.Frame(form_frame)
            row.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(row, text=label_text, width=15).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=self.fields[field_name]).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Imagen
        img_frame = ttk.LabelFrame(form_frame, text="Imagen", padding=5)
        img_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_row = ttk.Frame(img_frame)
        btn_row.pack(fill=tk.X, pady=2)
        ttk.Button(btn_row, text="Seleccionar Imagen", command=self.select_image).pack(side=tk.LEFT, padx=5)
        self.lbl_img_name = ttk.Label(btn_row, text="Ninguna imagen seleccionada", foreground="gray")
        self.lbl_img_name.pack(side=tk.LEFT, padx=5)

        self.img_preview = ttk.Label(img_frame)
        self.img_preview.pack(pady=5)

        ttk.Button(form_frame, text="Guardar Inmueble", command=self.save_property, style="TButton").pack(pady=10, side=tk.BOTTOM)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            self.imagen_path = path
            self.lbl_img_name.config(text=os.path.basename(path), foreground="black")
            try:
                img = Image.open(path)
                img.thumbnail((200, 150))
                tk_img = ImageTk.PhotoImage(img)
                self.img_preview.config(image=tk_img)
                self.img_preview.image = tk_img
            except Exception as e:
                print(f"Error al cargar imagen: {e}")

    def save_property(self):
        if not all(v.get() for v in self.fields.values()):
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        valor_dia_clean = self.fields["valor_dia"].get().replace(".", "")
        property_data = (
            self.fields["nombre"].get(),
            self.fields["cantidad_personas"].get(),
            self.fields["direccion"].get(),
            self.fields["localidad"].get(),
            self.fields["provincia"].get(),
            self.fields["tipo"].get(),
            valor_dia_clean
        )

        db = Database()
        if db.connect():
            cursor = db.connection.cursor()
            query = "INSERT INTO inmuebles (nombre, cantidad_personas, direccion, localidad, provincia, tipo, valor_dia) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, property_data)
            db.connection.commit()
            id_inmueble = cursor.lastrowid

            # Copiar imagen si se seleccionó
            if self.imagen_path:
                ext = os.path.splitext(self.imagen_path)[1]
                dest = os.path.join(ASSETS_DIR, f"{id_inmueble}{ext}")
                try:
                    shutil.copy2(self.imagen_path, dest)
                    cursor.execute("UPDATE inmuebles SET imagen = %s WHERE id_inmueble = %s", (dest, id_inmueble))
                    db.connection.commit()
                except Exception as e:
                    print(f"Error al copiar imagen: {e}")

            cursor.close()
            messagebox.showinfo("Éxito", "Inmueble guardado exitosamente", parent=self.window)
            self.window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

    def show(self):
        self.window.mainloop()
