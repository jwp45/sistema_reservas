import tkinter as tk
from tkinter import ttk, messagebox

from controllers.database import Database
from controllers.property_controller import PropertyController

class EditPropertyWindow:
    def __init__(self, master, property_id, property_list_window):
        self.master = master
        self.property_id = property_id
        self.property_list_window = property_list_window

        self.window = tk.Toplevel(master)
        self.window.title("Editar Inmueble")
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

        # Cargar los datos del inmueble
        self.load_property_data()

        # Botón para guardar cambios
        save_button = ttk.Button(
            form_frame,
            text="Guardar Cambios",
            command=self.save_changes,
            style="TButton"
        )
        save_button.pack(pady=10, side=tk.BOTTOM)

    def load_property_data(self):
        """Cargar los datos del inmueble desde la base de datos"""
        db = Database()
        if db.connect():
            query = "SELECT nombre, cantidad_personas, direccion, localidad, provincia, tipo, valor_dia FROM inmuebles WHERE id_inmueble = %s"
            cursor = db.connection.cursor()
            cursor.execute(query, (self.property_id,))
            result = cursor.fetchone()
            if result:
                self.fields["nombre"].set(result[0])
                self.fields["cantidad_personas"].set(result[1])
                self.fields["direccion"].set(result[2])
                self.fields["localidad"].set(result[3])
                self.fields["provincia"].set(result[4])
                self.fields["tipo"].set(result[5])
                # Formatear valor_dia con separador de miles
                try:
                    valor = float(result[6])
                    self.fields["valor_dia"].set(f"{valor:,.0f}".replace(",", "."))
                except (ValueError, TypeError):
                    self.fields["valor_dia"].set(result[6])
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def save_changes(self):
        """Guardar los cambios en la base de datos"""
        # Validación de entradas
        if not self.fields["nombre"].get() or not self.fields["cantidad_personas"].get() or not self.fields["direccion"].get() or not self.fields["localidad"].get() or not self.fields["provincia"].get() or not self.fields["tipo"].get() or not self.fields["valor_dia"].get():
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        # Limpiar el separador de miles antes de guardar
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
            query = "UPDATE inmuebles SET nombre=%s, cantidad_personas=%s, direccion=%s, localidad=%s, provincia=%s, tipo=%s, valor_dia=%s WHERE id_inmueble=%s"
            cursor = db.connection.cursor()
            cursor.execute(query, property_data + (self.property_id,))
            db.connection.commit()
            messagebox.showinfo("Éxito", "Inmueble actualizado exitosamente", parent=self.window)
            self.window.destroy()
            self.property_list_window.refresh_properties()  # Refrescar la lista de inmuebles
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

class PropertyListWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Lista de Inmuebles")
        self.window.geometry("800x600")

        # Crear un frame para la lista de inmuebles
        property_frame = ttk.Frame(self.window)
        property_frame.pack(padx=10, pady=10, expand=True)

        # Crear una entrada de búsqueda
        search_frame = ttk.Frame(property_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_button = ttk.Button(search_frame, text="Buscar", command=self.filter_properties, padding=(5,1))
        search_button.pack(side=tk.RIGHT, padx=5)

        # Crear una tabla para mostrar los inmuebles
        self.property_table = ttk.Treeview(property_frame, columns=("ID", "Nombre", "Cantidad", "Dirección", "Localidad", "Provincia", "Tipo", "Valor por Día"), show="headings")
        self.property_table.heading("ID", text="ID")
        self.property_table.heading("Nombre", text="Nombre")
        self.property_table.heading("Cantidad", text="Cantidad")
        self.property_table.heading("Dirección", text="Dirección")
        self.property_table.heading("Localidad", text="Localidad")
        self.property_table.heading("Provincia", text="Provincia")
        self.property_table.heading("Tipo", text="Tipo")
        self.property_table.heading("Valor por Día", text="Valor por Día")

        # Configurar el ancho de las columnas
        self.property_table.column("ID", width=50)
        self.property_table.column("Nombre", width=100)
        self.property_table.column("Cantidad", width=80)
        self.property_table.column("Dirección", width=150)
        self.property_table.column("Localidad", width=100)
        self.property_table.column("Provincia", width=100)
        self.property_table.column("Tipo", width=80)
        self.property_table.column("Valor por Día", width=100)

        # Añadir la tabla al frame
        self.property_table.pack(fill=tk.BOTH, expand=True)

        # Crear un botón para eliminar inmueble
        delete_button = ttk.Button(property_frame, text="Eliminar Inmueble", command=self.delete_property)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Crear un botón para editar inmueble
        edit_button = ttk.Button(property_frame, text="Editar Inmueble", command=self.edit_property)
        edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Cargar los inmuebles desde la base de datos
        self.load_properties()

    def load_properties(self):
        """Cargar los inmuebles desde la base de datos y mostrarlos en la tabla"""
        db = Database()
        if db.connect():
            properties = db.get_all_properties()  # Asumimos que este método existe en la clase Database
            for prop in properties:
                # Formatear el valor_dia (índice 7) con separador de miles
                formatted_prop = list(prop)
                try:
                    valor = float(formatted_prop[7])
                    formatted_prop[7] = f"{valor:,.0f}".replace(",", ".")
                except (ValueError, TypeError):
                    pass
                self.property_table.insert("", "end", values=formatted_prop)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def filter_properties(self):
        """Filtrar los inmuebles según el texto ingresado en el campo de búsqueda"""
        search_text = self.search_var.get().lower()
        for item in self.property_table.get_children():
            values = self.property_table.item(item, 'values')
            if any(search_text in str(value).lower() for value in values):
                self.property_table.item(item, open=True)
            else:
                self.property_table.delete(item)

    def delete_property(self):
        """Eliminar el inmueble seleccionado"""
        selected_item = self.property_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un inmueble para eliminar.")
            return

        property_id = self.property_table.item(selected_item)['values'][0]
        property_name = self.property_table.item(selected_item)['values'][1]

        # Preguntar al usuario si está seguro de eliminar el inmueble
        confirm = messagebox.askyesno("Confirmación", f"¿Está seguro de eliminar el inmueble {property_name}?")
        if confirm:
            property_controller = PropertyController()
            if property_controller.delete_property(property_id):
                self.property_table.delete(selected_item)
                messagebox.showinfo("Éxito", "Inmueble eliminado correctamente")
                self.refresh_properties()  # Refrescar la lista de inmuebles
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inmueble")

    def edit_property(self):
        """Editar el inmueble seleccionado"""
        selected_item = self.property_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un inmueble para editar.")
            return

        property_id = self.property_table.item(selected_item)['values'][0]
        edit_window = EditPropertyWindow(self.master, property_id, self)

    def refresh_properties(self):
        """Refrescar la lista de inmuebles"""
        for item in self.property_table.get_children():
            self.property_table.delete(item)
        self.load_properties()

    def show(self):
        """Mostrar la ventana"""
        self.window.mainloop()
