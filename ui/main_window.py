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
from ui.finance_window import FinanceWindow

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
            "provincia": StringVar(),
            "fecha_registro": StringVar(),
            "cantidad_personas": StringVar(),
            "adelanto": StringVar(),
            "discount_is_percentage": BooleanVar(),
            "descuento": StringVar(),
            "inmueble": StringVar(),
            "fecha_ingreso": StringVar(),
            "fecha_egreso": StringVar()
        }

    def setup_ui(self):
        """Configurar la interfaz gráfica principal con un diseño de Dashboard Profesional"""
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f2f5")

        # --- ESTILOS ---
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#2c3e50")
        style.configure("Content.TFrame", background="#f0f2f5")
        style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), padding=12, width=22)
        style.configure("DashboardHeader.TLabel", font=("Segoe UI", 22, "bold"), background="#f0f2f5", foreground="#2c3e50")
        style.configure("Card.TFrame", background="white", relief="flat", borderwidth=0)
        style.configure("CardHeader.TLabel", font=("Segoe UI", 14, "bold"), background="white", foreground="#34495e")

        # --- ESTRUCTURA PRINCIPAL ---
        # Sidebar (Izquierda)
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Contenedor Principal (Derecha)
        self.main_container = ttk.Frame(self.root, style="Content.TFrame")
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- CONTENIDO SIDEBAR ---
        ttk.Label(self.sidebar, text="SISTEMA HOTEL", font=("Segoe UI", 16, "bold"), background="#2c3e50", foreground="#ecf0f1").pack(pady=40)
        
        nav_items = [
            ("INICIO / REFRESCAR", self.refresh_dashboard),
            ("NUEVA RESERVA", self.handle_new_reservation),
            ("VER RESERVAS", self.handle_my_reservations),
            ("VER CLIENTES", self.show_client_list),
            ("VER INMUEBLES", self.show_property_list),
            ("REGISTRAR CLIENTE", self.handle_clients),
            ("REGISTRAR INMUEBLE", self.handle_properties),
            ("CONTROL FINANCIERO", self.show_finance_dashboard)
        ]

        for text, cmd in nav_items:
            btn = ttk.Button(self.sidebar, text=text, command=cmd, style="Nav.TButton")
            btn.pack(fill=tk.X, padx=20, pady=6)

        ttk.Label(self.sidebar, text="Admin Panel v2.5", font=("Segoe UI", 8), background="#2c3e50", foreground="#95a5a6").pack(side=tk.BOTTOM, pady=30)

        # --- CONTENIDO PRINCIPAL ---
        header_area = ttk.Frame(self.main_container, style="Content.TFrame", padding=(40, 40, 40, 10))
        header_area.pack(fill=tk.X)
        
        ttk.Label(header_area, text="Panel de Control General", style="DashboardHeader.TLabel").pack(side=tk.LEFT)
        self.lbl_today = ttk.Label(header_area, text=date.today().strftime("%d de %B, %Y"), font=("Segoe UI", 12), background="#f0f2f5", foreground="#7f8c8d")
        self.lbl_today.pack(side=tk.RIGHT, pady=15)

        # Área de Widgets/Cards
        widgets_area = ttk.Frame(self.main_container, style="Content.TFrame", padding=40)
        widgets_area.pack(fill=tk.BOTH, expand=True)
        widgets_area.columnconfigure(0, weight=1)
        widgets_area.columnconfigure(1, weight=1)

        # --- CARD: PRÓXIMOS INGRESOS ---
        self.card_in = tk.Frame(widgets_area, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        self.card_in.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        
        in_header = tk.Frame(self.card_in, bg="#27ae60", height=5)
        in_header.pack(fill=tk.X)
        
        in_content = tk.Frame(self.card_in, bg="white", padx=30, pady=30)
        in_content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(in_content, text="📥 PRÓXIMO CHECK-IN", font=("Segoe UI", 11, "bold"), bg="white", fg="#27ae60").pack(anchor="w")
        self.lbl_checkin = tk.Label(in_content, text="—", font=("Segoe UI", 28, "bold"), bg="white", fg="#2c3e50")
        self.lbl_checkin.pack(anchor="w", pady=15)
        
        self.lbl_checkin_name = tk.Label(in_content, text="", font=("Segoe UI", 14, "bold"), bg="white", fg="#34495e")
        self.lbl_checkin_name.pack(anchor="w")
        self.lbl_checkin_inmueble = tk.Label(in_content, text="", font=("Segoe UI", 12), bg="white", fg="#7f8c8d")
        self.lbl_checkin_inmueble.pack(anchor="w", pady=(5, 15))
        
        info_in = tk.Frame(in_content, bg="white")
        info_in.pack(fill=tk.X)
        self.lbl_checkin_phone = tk.Label(info_in, text="", font=("Segoe UI", 11), bg="white", fg="#2c3e50")
        self.lbl_checkin_phone.pack(side=tk.LEFT)
        self.lbl_checkin_prov = tk.Label(info_in, text="", font=("Segoe UI", 11, "italic"), bg="white", fg="#95a5a6")
        self.lbl_checkin_prov.pack(side=tk.RIGHT)

        # --- CARD: PRÓXIMOS EGRESOS ---
        self.card_out = tk.Frame(widgets_area, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        self.card_out.grid(row=0, column=1, padx=(20, 0), sticky="nsew")
        
        out_header = tk.Frame(self.card_out, bg="#2980b9", height=5)
        out_header.pack(fill=tk.X)
        
        out_content = tk.Frame(self.card_out, bg="white", padx=30, pady=30)
        out_content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(out_content, text="📤 PRÓXIMO CHECK-OUT", font=("Segoe UI", 11, "bold"), bg="white", fg="#2980b9").pack(anchor="w")
        self.lbl_checkout = tk.Label(out_content, text="—", font=("Segoe UI", 28, "bold"), bg="white", fg="#2c3e50")
        self.lbl_checkout.pack(anchor="w", pady=15)
        
        self.lbl_checkout_name = tk.Label(out_content, text="", font=("Segoe UI", 14, "bold"), bg="white", fg="#34495e")
        self.lbl_checkout_name.pack(anchor="w")
        self.lbl_checkout_inmueble = tk.Label(out_content, text="", font=("Segoe UI", 12), bg="white", fg="#7f8c8d")
        self.lbl_checkout_inmueble.pack(anchor="w", pady=(5, 15))
        
        info_out = tk.Frame(out_content, bg="white")
        info_out.pack(fill=tk.X)
        self.lbl_checkout_phone = tk.Label(info_out, text="", font=("Segoe UI", 11), bg="white", fg="#2c3e50")
        self.lbl_checkout_phone.pack(side=tk.LEFT)
        self.lbl_checkout_prov = tk.Label(info_out, text="", font=("Segoe UI", 11, "italic"), bg="white", fg="#95a5a6")
        self.lbl_checkout_prov.pack(side=tk.RIGHT)

        self.refresh_dashboard()

    def handle_new_reservation(self):
        """Manejar la lógica para iniciar una nueva reserva"""
        self.reservation_controller.create_reservation()

    def handle_my_reservations(self):
        ReservationListWindow(self.root)

    def handle_contact(self):
        """Manejar la sección de contacto y soporte"""
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
            ("ID Cliente:", "id_clientes", True),
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

    def show_finance_dashboard(self):
        """Mostrar la ventana de control financiero"""
        FinanceWindow(self.root)

    def refresh_dashboard(self):
        from datetime import datetime
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        def fmt_date(d):
            try:
                dt = datetime.strptime(str(d), "%Y-%m-%d")
                return f"{dt.day} {meses[dt.month]} {dt.year}"
            except: return str(d)

        db = Database()
        if db.connect():
            # Actualizar Ingreso
            checkins = db.get_upcoming_checkins()
            if checkins:
                r = checkins[0]
                self.lbl_checkin.config(text=fmt_date(r[5]))
                self.lbl_checkin_name.config(text=str(r[1]).upper())
                self.lbl_checkin_phone.config(text=f"📞 {r[2]}")
                self.lbl_checkin_prov.config(text=f"📍 {r[3]}")
                self.lbl_checkin_inmueble.config(text=f"🏠 {r[4]}")
            else:
                self.lbl_checkin.config(text="Sin ingresos")
                self.lbl_checkin_name.config(text="")
                self.lbl_checkin_inmueble.config(text="Agenda libre")

            # Actualizar Egreso
            checkouts = db.get_upcoming_checkouts()
            if checkouts:
                r = checkouts[0]
                self.lbl_checkout.config(text=fmt_date(r[6]))
                self.lbl_checkout_name.config(text=str(r[1]).upper())
                self.lbl_checkout_phone.config(text=f"📞 {r[2]}")
                self.lbl_checkout_prov.config(text=f"📍 {r[3]}")
                self.lbl_checkout_inmueble.config(text=f"🏠 {r[4]}")
            else:
                self.lbl_checkout.config(text="Sin egresos")
                self.lbl_checkout_name.config(text="")
                self.lbl_checkout_inmueble.config(text="Todo al día")

    def run(self):
        self.setup_ui()
        self.root.mainloop()
