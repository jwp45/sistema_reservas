from controllers.database import Database
import tkinter as tk
from tkinter import ttk, messagebox

class ReservationController:
    def __init__(self, master):
        self.master = master
        self.db = Database()

    def create_reservation(self):
        # Lógica para crear una nueva reserva
        print("Crear Reserva")
        
        # Crear una nueva ventana para el formulario de reserva
        reservation_window = tk.Toplevel(self.master)
        reservation_window.title("Detalle de Reserva")
        reservation_window.geometry("800x600")

        # Frame principal del formulario
        form_frame = ttk.Frame(reservation_window)
        form_frame.pack(padx=10, pady=10, expand=True)

        # Mensaje para notificaciones
        message_label = ttk.Label(form_frame, text="Ingrese los datos de la reserva", font=('Arial', 14))
        message_label.pack(side=tk.TOP, padx=5, pady=5)

        # Campos del formulario
        fields = [
            ("ID Cliente:", "id_clientes"),
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Correo electrónico:", "email"),
            ("Teléfono:", "telefono"),
            ("Provincia:", "provincia"),
            ("Fecha de registro:", "fecha_registro"),
            ("Cantidad de personas:", "cantidad_personas"),
            ("Porcentaje de adelanto:", "porcentaje_adelanto"),
            ("Adelanto:", "adelanto"),
            ("Porcentaje de descuento:", "porcentaje_descuento"),
            ("Descuento:", "descuento"),
            ("Inmueble:", "inmueble"),
            ("Fecha de ingreso:", "fecha_ingreso"),
            ("Fecha de egreso:", "fecha_egreso")
        ]

        client_fields = {
            "id_clientes": tk.StringVar(),
            "nombre": tk.StringVar(),
            "apellido": tk.StringVar(),
            "email": tk.StringVar(),
            "telefono": tk.StringVar(),
            "provincia": tk.StringVar(),  # Añadir la variable 'provincia'
            "fecha_registro": tk.StringVar(),  # Añadir la variable 'fecha_registro'
            "cantidad_personas": tk.StringVar(),  # Añadir la variable 'cantidad_personas'
            "porcentaje_adelanto": tk.StringVar(),  # Añadir la variable 'porcentaje_adelanto'
            "adelanto": tk.StringVar(),  # Añadir la variable 'adelanto'
            "porcentaje_descuento": tk.StringVar(),  # Añadir la variable 'porcentaje_descuento'
            "descuento": tk.StringVar(),  # Añadir la variable 'descuento'
            "inmueble": tk.StringVar(),  # Añadir la variable 'inmueble'
            "fecha_ingreso": tk.StringVar(),  # Añadir la variable 'fecha_ingreso'
            "fecha_egreso": tk.StringVar()  # Añadir la variable 'fecha_egreso'
        }

        for field in fields:
            row = ttk.Frame(form_frame)
            row.pack(fill=tk.X, padx=5, pady=2)

            label = ttk.Label(row, text=field[0], width=15)
            label.pack(side=tk.LEFT)

            if field[1] == "inmueble":
                # Cargar los inmuebles desde la base de datos
                if not self.db.connection or not self.db.connection.is_connected():
                    self.db.connect()
                
                properties = self.db.get_all_properties()
                property_names = [property_data[1] for property_data in properties]
                entry = ttk.Combobox(row, textvariable=client_fields[field[1]], values=property_names, state="readonly")
            else:
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])

            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

            # Si es el campo ID Cliente, vincular la tecla Enter para autocompletar
            if field[1] == "id_clientes":
                entry.bind("<Return>", lambda event: self.autofill_client_data(client_fields))

        # Botón para reservar
        reserve_button = ttk.Button(
            form_frame,
            text="Reservar",
            command=lambda: self.save_reservation(reservation_window, client_fields),
            style="TButton"
        )
        reserve_button.pack(pady=10, side=tk.BOTTOM)

    def autofill_client_data(self, client_fields):
        # Obtener el ID del cliente ingresado
        client_id = client_fields["id_clientes"].get()
        
        if not client_id:
            return

        # Asegurar que la base de datos esté conectada
        if not self.db.connection or not self.db.connection.is_connected():
            if not self.db.connect():
                messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.master)
                return

        # Buscar el cliente en la base de datos
        client_data = self.db.get_client_by_id(client_id)

        if client_data:
            client_fields["nombre"].set(client_data[1])
            client_fields["apellido"].set(client_data[2])
            client_fields["email"].set(client_data[3])
            client_fields["telefono"].set(client_data[4])
        else:
            messagebox.showerror("Error", "Cliente no encontrado", parent=self.master)

    def save_reservation(self, reservation_window, client_fields):
        # Implementación futura para guardar la reserva
        pass
