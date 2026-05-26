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
        self.lbl_checkin.pack(pady=(5, 2))

        self.lbl_checkin_name = tk.Label(checkin_frame, text="", font=('Arial', 11),
                                         bg="#e8f5e9", fg="#1b5e20")
        self.lbl_checkin_name.pack()
        self.lbl_checkin_phone = tk.Label(checkin_frame, text="", font=('Arial', 11),
                                          bg="#e8f5e9", fg="#1b5e20")
        self.lbl_checkin_phone.pack()
        self.lbl_checkin_prov = tk.Label(checkin_frame, text="", font=('Arial', 11),
                                          bg="#e8f5e9", fg="#1b5e20")
        self.lbl_checkin_prov.pack()
        self.lbl_checkin_inmueble = tk.Label(checkin_frame, text="", font=('Arial', 11),
                                              bg="#e8f5e9", fg="#1b5e20")
        self.lbl_checkin_inmueble.pack(pady=(0, 15))

        # Panel derecho: Próximos Egresos
        checkout_frame = tk.Frame(columns_frame, bg="#e3f2fd", bd=2, relief=tk.GROOVE)
        checkout_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(checkout_frame, text="📤 Próximo Egreso", font=('Arial', 16, 'bold'),
                 bg="#e3f2fd", fg="#1565c0").pack(pady=(20, 5))

        self.lbl_checkout = tk.Label(checkout_frame, text="Cargando...", font=('Arial', 22, 'bold'),
                                     bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout.pack(pady=(5, 2))

        self.lbl_checkout_name = tk.Label(checkout_frame, text="", font=('Arial', 11),
                                          bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout_name.pack()
        self.lbl_checkout_phone = tk.Label(checkout_frame, text="", font=('Arial', 11),
                                           bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout_phone.pack()
        self.lbl_checkout_prov = tk.Label(checkout_frame, text="", font=('Arial', 11),
                                           bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout_prov.pack()
        self.lbl_checkout_inmueble = tk.Label(checkout_frame, text="", font=('Arial', 11),
                                               bg="#e3f2fd", fg="#0d47a1")
        self.lbl_checkout_inmueble.pack(pady=(0, 15))

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
        """Manejar la lógica para el registro de nuevos clientes"""
        client_window = tk.Toplevel(self.root)
        client_window.title("Registrar Nuevo Cliente")
        client_window.geometry("550x500")
        client_window.configure(bg="#f8f9fa")
        client_window.transient(self.root)

        # Estilos locales
        style = ttk.Style(client_window)
        style.configure("ClientFormHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("ClientFormSection.TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_frame = ttk.Frame(client_window, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Registro de Huésped", style="ClientFormHeader.TLabel").pack(pady=(0, 25))

        # Sección de Datos
        sec_form = ttk.LabelFrame(main_frame, text=" Información Personal ", padding=20, style="ClientFormSection.TLabelframe")
        sec_form.pack(fill=tk.X, pady=10)
        sec_form.columnconfigure(1, weight=1)

        # Obtener el próximo ID disponible
        db = Database()
        db.connect()
        next_id = db.get_next_available_client_id()
        self.client_fields["id_clientes"].set(str(next_id))

        # Campos del formulario (limpiar primero)
        for key in ["nombre", "apellido", "email", "telefono"]:
            self.client_fields[key].set("")

        fields_order = [
            ("ID Cliente:", "id_clientes", True), # El tercer elemento indica si es solo lectura para el usuario inicial
            ("Nombre:", "nombre", False),
            ("Apellido:", "apellido", False),
            ("Email:", "email", False),
            ("Teléfono:", "telefono", False)
        ]

        for i, (label_text, field_name, is_readonly) in enumerate(fields_order):
            ttk.Label(sec_form, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=10, padx=(0, 15))
            state = "readonly" if is_readonly else "normal"
            ttk.Entry(sec_form, textvariable=self.client_fields[field_name], state=state).grid(row=i, column=1, sticky=tk.EW, pady=10)

        # Barra de Botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 20, 0, 0))
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="CANCELAR", command=client_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="GUARDAR CLIENTE", style="Action.TButton", 
                   command=lambda: self.save_client(client_window)).pack(side=tk.RIGHT, padx=5)

    def save_client(self, client_window):
        """Guardar los datos del cliente en la base de datos"""
        # Validación de entradas
        nombre = self.client_fields["nombre"].get()
        apellido = self.client_fields["apellido"].get()
        email = self.client_fields["email"].get()
        telefono = self.client_fields["telefono"].get()
        id_cliente = self.client_fields["id_clientes"].get()

        if not (nombre and apellido and email and telefono):
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=client_window)
            return

        client_data = (
            int(id_cliente),
            nombre,
            apellido,
            email,
            telefono
        )

        db = Database()
        if db.connect():
            if db.insert_client(client_data):
                messagebox.showinfo("Éxito", f"Cliente {nombre} {apellido} registrado exitosamente con ID #{id_cliente}", parent=client_window)
                client_window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar el cliente en la base de datos", parent=client_window)
        else:
            messagebox.showerror("Error", "Error de conexión a la base de datos", parent=client_window)

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
                self.lbl_checkin.config(text=fmt_date(row[5]))
                self.lbl_checkin_name.config(text=f"👤 {row[1]}")
                self.lbl_checkin_phone.config(text=f"📞 {row[2]}")
                self.lbl_checkin_prov.config(text=f"📍 {row[3]}")
                self.lbl_checkin_inmueble.config(text=f"🏠 {row[4]}")
            else:
                self.lbl_checkin.config(text="—")
                self.lbl_checkin_name.config(text="")
                self.lbl_checkin_phone.config(text="")
                self.lbl_checkin_prov.config(text="")
                self.lbl_checkin_inmueble.config(text="")

            checkouts = db.get_upcoming_checkouts()
            if checkouts:
                row = checkouts[0]
                self.lbl_checkout.config(text=fmt_date(row[6]))
                self.lbl_checkout_name.config(text=f"👤 {row[1]}")
                self.lbl_checkout_phone.config(text=f"📞 {row[2]}")
                self.lbl_checkout_prov.config(text=f"📍 {row[3]}")
                self.lbl_checkout_inmueble.config(text=f"🏠 {row[4]}")
            else:
                self.lbl_checkout.config(text="—")
                self.lbl_checkout_name.config(text="")
                self.lbl_checkout_phone.config(text="")
                self.lbl_checkout_prov.config(text="")
                self.lbl_checkout_inmueble.config(text="")

    def run(self):
        self.setup_ui()
        self.root.mainloop()
