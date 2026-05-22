import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reservas Profesional")
        
        # Crear instancias de los controladores (mantenemos la estructura existente)
        self.property_controller = PropertyController()
        self.client_controller = ClientController()
        self.reservation_controller = ReservationController()

    def setup_ui(self):
        """Configurar y mostrar la interfaz gráfica principal"""
        
        # Configuración general de la ventana
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Crear un frame superior para los botones principales
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        # Estilos consistentes para los botones
        button_style = {
            'font': ('Arial', 12),
            'padding': 10,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': tk.RAISED,
            'borderwidth': 3
        }

        # Botón para crear una nueva reserva
        self.btn_new_reservation = ttk.Button(
            nav_frame,
            text="Iniciar Reserva",
            command=self.handle_new_reservation,
            **button_style
        )
        
        # Botón para ver historial de reservas
        self.btn_my_reservations = ttk.Button(
            nav_frame,
            text="Mis Reservas",
            command=self.handle_my_reservations,
            **button_style
        )
        
        # Botón para contactar al administrador
        self.btn_contact = ttk.Button(
            nav_frame,
            text="Contacto",
            command=self.handle_contact,
            **button_style
        )

        # Ubicar los botones en el frame de navegación
        self.btn_new_reservation.pack(side=tk.LEFT, padx=2)
        self.btn_my_reservations.pack(side=tk.LEFT, padx=2)
        self.btn_contact.pack(side=tk.LEFT, padx=2)

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

    def run(self):
        self.root.mainloop()
