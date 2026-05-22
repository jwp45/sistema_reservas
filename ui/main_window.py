import tkinter as tk
from tkinter import ttk, messagebox, StringVar, Frame
from datetime import date
from controllers.client_controller import ClientController
from controllers.property_controller import PropertyController
from controllers.reservation_controller import ReservationController
from controllers.database import Database

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reservas Profesional")

        # Crear instancias de los controladores (mantenemos la estructura existente)
        self.property_controller = PropertyController()
        self.client_controller = ClientController()
        self.reservation_controller = ReservationController()

        # Variables para el formulario de clientes
        self.client_fields = {
            "id_clientes": StringVar(),
            "nombre": StringVar(),
            "apellido": StringVar(),
            "email": StringVar(),
            "telefono": StringVar()
        }

    def setup_ui(self):
        """Configurar y mostrar la interfaz gráfica principal"""

        # Configuración general de la ventana
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Crear un frame superior para los botones principales
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        # Estilos consistentes para los botones
        style = ttk.Style()
        style.configure("TButton", font=('Arial', 12), padding=10,
                        background='#4CAF50', foreground='white',
                        relief="raised", borderwidth=3)

        # Botón para crear una nueva reserva
        self.btn_new_reservation = ttk.Button(
            nav_frame,
            text="Iniciar Reserva",
            command=self.handle_new_reservation,
            style="TButton"
        )

        # Botón para ver historial de reservas
        self.btn_my_reservations = ttk.Button(
            nav_frame,
            text="Mis Reservas",
            command=self.handle_my_reservations,
            style="TButton"
        )

        # Botón para contactar al administrador
        self.btn_contact = ttk.Button(
            nav_frame,
            text="Contacto",
            command=self.handle_contact,
            style="TButton"
        )

        # Nuevo botón para clientes
        self.btn_clients = ttk.Button(
            nav_frame,
            text="Clientes",
            command=self.handle_clients,
            style="TButton"
        )

        # Nuevo botón para inmuebles
        self.btn_properties = ttk.Button(
            nav_frame,
            text="Inmuebles",
            command=self.handle_properties,
            style="TButton"
        )

        # Ubicar los botones en el frame de navegación
        self.btn_new_reservation.pack(side=tk.LEFT, padx=2)
        self.btn_my_reservations.pack(side=tk.LEFT, padx=2)
        self.btn_contact.pack(side=tk.LEFT, padx=2)
        self.btn_clients.pack(side=tk.LEFT, padx=2)
        self.btn_properties.pack(side=tk.LEFT, padx=2)

        # Crear un area principal para el contenido
        main_content = ttk.Frame(self.root)
        main_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame superior para encabezado del contenido
        content_header = ttk.LabelFrame(main_content, text="Bienvenido al sistema de reservas")
        content_header.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        # Área central para el desarrollo futuro (reservaciones, detalles, etc.)
        self.content_area = ttk.Frame(main_content)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def handle_new_reservation(self):
        """Manejar la lógica para iniciar una nueva reserva"""
        # En el futuro implementaremos aquí la funcionalidad de reserva
        pass

    def handle_my_reservations(self):
        """Mostrar las reservas del usuario"""
        # Aquí irá la implementación del historial de reservas
        pass

    def handle_contact(self):
        """Manejar la sección de contacto y soporte"""
        # Implementación futura para el contacto y soporte al usuario
        pass

    def handle_clients(self):
        """Manejar la lógica para clientes"""
        # Crear una nueva ventana para el formulario de clientes
        client_window = tk.Toplevel(self.root)
        client_window.title("Gestión de Clientes")
        client_window.geometry("450x300")

        # Frame principal del formulario
        form_frame = ttk.Frame(client_window)
        form_frame.pack(padx=10, pady=10, expand=True)

        # Mensaje para notificaciones
        message_label = ttk.Label(form_frame, text="Ingrese los datos del cliente", font=('Arial', 14))
        message_label.pack(side=tk.TOP, padx=5, pady=5)

        # Campos del formulario
        fields = [
            ("ID Cliente:", "id_clientes"),
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Correo electrónico:", "email"),
            ("Teléfono:", "telefono")
        ]

        for field in fields:
            row = ttk.Frame(form_frame)
            row.pack(fill=tk.X, padx=5, pady=2)

            label = ttk.Label(row, text=field[0], width=15)
            label.pack(side=tk.LEFT)

            entry = ttk.Entry(row, textvariable=self.client_fields[field[1]])
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Botón para guardar
        save_button = ttk.Button(
            form_frame,
            text="Guardar Cliente",
            command=lambda: self.save_client(),
            style="TButton"
        )
        save_button.pack(pady=10, side=tk.BOTTOM)

    def select_date(self, field_name, master):
        """Manejar la selección de fecha de nacimiento"""
        date_dialog = tk.Toplevel(master)
        date_dialog.title("Seleccionar Fecha")

        today = date.today()
        self.client_fields[field_name].set(today.strftime("%d/%m/%Y"))

    def save_client(self):
        """Guardar los datos del cliente en la base de datos"""
        client_data = (
            self.client_fields["nombre"].get(),
            self.client_fields["apellido"].get(),
            self.client_fields["email"].get(),
            self.client_fields["telefono"].get()
        )

        db = Database()
        if db.connect():
            next_id = db.get_next_id()
            if next_id is not None:
                self.client_fields["id_clientes"].set(next_id)
            db.insert_client(client_data)
            messagebox.showinfo("Éxito", "Cliente guardado exitosamente")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def handle_properties(self):
        """Manejar la lógica para inmuebles"""
        print("Manejando inmuebles")
        # Aquí puedes agregar la lógica para manejar los inmuebles

    def run(self):
        self.root.mainloop()
