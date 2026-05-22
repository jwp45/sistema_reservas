import sys
import tkinter as tk
from controllers.client_controller import ClientController
from controllers.property_controller import PropertyController
from controllers.reservation_controller import ReservationController

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reservas Profesional")

        # Crear instancias de los controladores (mantenemos la estructura existente)
        self.property_controller = PropertyController()
        self.client_controller = ClientController()
        self.reservation_controller = ReservationController()

        # Variables para el formulario de clientes
        self.clients = []

        # Crear menú desplegable
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Ver Clientes", command=self.show_clients)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

    def setup_ui(self):
        # Configuración de la interfaz gráfica
        pass

    def handle_new_reservation(self):
        pass

    def handle_my_reservations(self):
        pass

    def handle_contact(self):
        pass

    def handle_clients(self):
        pass

    def select_date(self, field_name, master):
        pass

    def save_client(self, client_window):
        pass

    def handle_properties(self):
        pass

    def run(self):
        self.root.mainloop()

    def show_clients(self):
        # Mostrar los clientes cargados en la base de datos
        self.clients = self.client_controller.get_all_clients()
        print("Clientes cargados:", self.clients)

if __name__ == '__main__':
    app = MainWindow()
    app.setup_ui()  # Corregí el nombre del método
    app.run()

# Nota: La instalación de mysql-connector-python debe hacerse en la terminal, no dentro del script Python.
