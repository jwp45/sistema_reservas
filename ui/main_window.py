import tkinter as tk
from controllers.property_controller import PropertyController
from controllers.client_controller import ClientController
from controllers.reservation_controller import ReservationController

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestor de Reservas")

        # Crear instancias de los controladores
        self.property_controller = PropertyController()
        self.client_controller = ClientController()
        self.reservation_controller = ReservationController()

        # Configurar la interfaz gráfica
        self.setup_ui()

    def setup_ui(self):
        # Botón para crear una nueva propiedad
        create_property_button = tk.Button(self.root, text="Crear Propiedad", command=self.property_controller.create_property)
        create_property_button.pack(pady=10)

        # Botón para crear un nuevo cliente
        create_client_button = tk.Button(self.root, text="Crear Cliente", command=self.client_controller.create_client)
        create_client_button.pack(pady=10)

        # Botón para crear una nueva reserva
        create_reservation_button = tk.Button(self.root, text="Crear Reserva", command=self.reservation_controller.create_reservation)
        create_reservation_button.pack(pady=10)

    def run(self):
        self.root.mainloop()

