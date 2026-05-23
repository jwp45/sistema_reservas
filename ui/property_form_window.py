import tkinter as tk
from tkinter import ttk, messagebox

from controllers.database import Database
from controllers.property_controller import PropertyController

class PropertyFormWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Agregar Inmueble")
        self.window.geometry("450x400")

        # Frame principal del formulario
        form_frame = ttk.Frame(self.window)
        form_frame.pack(padx=10, pady=10, expand=True)

        # Mensaje para notificaciones
        message_label = ttk.Label(form_frame, text="Ingrese los datos del inmueble", font=('Arial', 14))
        message_label.pack(side=tk.TOP, padx=5, pady=5)

        # Campos del formulario
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

            label = ttk.Label(row, text=label_text, width=15)
            label.pack(side=tk.LEFT)

            entry = ttk.Entry(row, textvariable=self.fields[field_name])
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Botón para guardar
        save_button = ttk.Button(
            form_frame,
            text="Guardar Inmueble",
            command=self.save_property,
            style="TButton"
        )
        save_button.pack(pady=10, side=tk.BOTTOM)

    def save_property(self):
        """Guardar los datos del inmueble en la base de datos"""
        # Validación de entradas
        if not self.fields["nombre"].get() or not self.fields["cantidad_personas"].get() or not self.fields["direccion"].get() or not self.fields["localidad"].get() or not self.fields["provincia"].get() or not self.fields["tipo"].get() or not self.fields["valor_dia"].get():
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        property_data = (
            self.fields["nombre"].get(),
            self.fields["cantidad_personas"].get(),
            self.fields["direccion"].get(),
            self.fields["localidad"].get(),
            self.fields["provincia"].get(),
            self.fields["tipo"].get(),
            self.fields["valor_dia"].get()
        )

        db = Database()
        if db.connect():
            query = "INSERT INTO inmuebles (nombre, cantidad_personas, direccion, localidad, provincia, tipo, valor_dia) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor = db.connection.cursor()
            cursor.execute(query, property_data)
            db.connection.commit()
            messagebox.showinfo("Éxito", "Inmueble guardado exitosamente", parent=self.window)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

    def show(self):
        """Mostrar la ventana"""
        self.window.mainloop()
