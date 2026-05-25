import tkinter as tk
from tkinter import ttk, messagebox, StringVar, BooleanVar, Frame
from datetime import date
from controllers.client_controller import ClientController
from controllers.property_controller import PropertyController
from controllers.reservation_controller import ReservationController
from controllers.database import Database
from ui.client_list_window import ClientListWindow
from ui.property_form_window import PropertyFormWindow
from ui.property_list_window import PropertyListWindow
from ui.reservation_list_window import ReservationListWindow

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reservas Profesional")

        # Crear instancias de los controladores (mantenemos la estructura existente)
        self.property_controller = PropertyController()
        self.client_controller = ClientController()
        self.reservation_controller = ReservationController(self.root)

        # Variables para el formulario de clientes
        self.client_fields = {
            "id_clientes": StringVar(),
            "nombre": StringVar(),
            "apellido": StringVar(),
            "email": StringVar(),
            "telefono": StringVar(),
            "provincia": StringVar(),  # Añadir la variable 'provincia'
            "fecha_registro": StringVar(),  # Añadir la variable 'fecha_registro'
            "cantidad_personas": StringVar(),  # Añadir la variable 'cantidad_personas'
            "adelanto": StringVar(),  # Añadir la variable 'adelanto'
            "discount_is_percentage": BooleanVar(),
            "descuento": StringVar(),  # Añadir la variable 'descuento'
            "inmueble": StringVar(),  # Añadir la variable 'inmueble'
            "fecha_ingreso": StringVar(),  # Añadir la variable 'fecha_ingreso'
            "fecha_egreso": StringVar()  # Añadir la variable 'fecha_egreso'
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

        # Menú desplegable superior
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=file_menu)
        file_menu.add_command(label="Clientes", command=self.show_client_list)
        file_menu.add_command(label="Inmuebles", command=self.show_property_list)  # Nuevo menú para inmuebles

        # Ubicar los botones en el frame de navegación
        self.btn_new_reservation.pack(side=tk.LEFT, padx=2)
        self.btn_my_reservations.pack(side=tk.LEFT, padx=2)
        self.btn_contact.pack(side=tk.LEFT, padx=2)
        self.btn_clients.pack(side=tk.LEFT, padx=2)
        self.btn_properties.pack(side=tk.LEFT, padx=2)

        # Crear un area principal para el contenido
        main_content = ttk.Frame(self.root)
        main_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        content_header = ttk.LabelFrame(main_content, text="Panel de Control")
        content_header.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        ttk.Label(content_header, text="Bienvenido al Sistema de Reservas", font=('Arial', 14, 'bold')).pack(padx=10, pady=5)

        # Contenedor de dos columnas
        columns_frame = ttk.Frame(main_content)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Panel izquierdo: Próximos Ingresos
        checkin_frame = tk.Frame(columns_frame, bg="#e8f5e9", bd=2, relief=tk.GROOVE)
        checkin_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(checkin_frame, text="📥 Próximo Ingreso", font=('Arial', 16, 'bold'),
                 bg="#e8f5e9", fg="#2e7d32").pack(pady=(20, 5))

        self.lbl_checkin = tk.Label(checkin_frame, text="Cargando...", font=('Arial', 22, 'bold'),
                                    bg="#e8f5e9", fg="#1b5e20")
        self.lbl_checkin.pack(pady=(5, 20))

        # Panel derecho: Próximos Egresos
        checkout_frame = tk.Frame(columns_frame, bg="#e3f2fd", bd=2, relief=tk.GROOVE)
        checkout_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(checkout_frame, text="📤 Próximo Egreso", font=('Arial', 16, 'bold'),
                 bg="#e3f2fd", fg="#1565c0").pack(pady=(20, 5))

        self.lbl_checkout = tk.Label(checkout_frame, text="Cargando...", font=('Arial', 22, 'bold'),
                                     bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout.pack(pady=(5, 20))

        self.refresh_dashboard()

    def handle_new_reservation(self):
        """Manejar la lógica para iniciar una nueva reserva"""
        self.reservation_controller.create_reservation()

    def handle_my_reservations(self):
        ReservationListWindow(self.root)

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
            command=lambda: self.save_client(client_window),
            style="TButton"
        )
        save_button.pack(pady=10, side=tk.BOTTOM)

    def select_date(self, field_name, master):
        """Manejar la selección de fecha de nacimiento"""
        date_dialog = tk.Toplevel(master)
        date_dialog.title("Seleccionar Fecha")

        today = date.today()
        self.client_fields[field_name].set(today.strftime("%d/%m/%Y"))

    def save_client(self, client_window):
        """Guardar los datos del cliente en la base de datos"""
        # Validación de entradas
        if not self.client_fields["nombre"].get() or not self.client_fields["apellido"].get() or not self.client_fields["email"].get() or not self.client_fields["telefono"].get():
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=client_window)
            return

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
            messagebox.showinfo("Éxito", "Cliente guardado exitosamente", parent=client_window)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=client_window)

    def save_reservation(self, reservation_window):
        """Guardar los datos de la reserva en la base de datos"""
        # Implementación futura para guardar la reserva
        pass

    def handle_properties(self):
        """Manejar la lógica para inmuebles"""
        property_form = PropertyFormWindow(self.root)
        property_form.show()

    def show_client_list(self):
        """Mostrar la ventana de lista de clientes"""
        client_list_window = ClientListWindow(self.root)
        client_list_window.show()

    def show_property_list(self):
        """Mostrar la ventana de lista de inmuebles"""
        property_list_window = PropertyListWindow(self.root)
        property_list_window.show()

    def refresh_dashboard(self):
        from datetime import datetime
        meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

        def fmt_date(d):
            try:
                dt = datetime.strptime(str(d), "%Y-%m-%d")
                return f"{dt.day} {meses[dt.month]} {dt.year}"
            except ValueError:
                return str(d)

        db = Database()
        if db.connect():
            checkins = db.get_upcoming_checkins()
            if checkins:
                row = checkins[0]
                self.lbl_checkin.config(text=fmt_date(row[4]))
            else:
                self.lbl_checkin.config(text="—")

            checkouts = db.get_upcoming_checkouts()
            if checkouts:
                row = checkouts[0]
                self.lbl_checkout.config(text=fmt_date(row[5]))
            else:
                self.lbl_checkout.config(text="—")

    def run(self):
        self.setup_ui()
        self.root.mainloop()
