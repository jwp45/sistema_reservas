import tkinter as tk
from tkinter import ttk, messagebox

from controllers.database import Database
from controllers.client_controller import ClientController

class ClientListWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Lista de Clientes")
        self.window.geometry("600x400")

        # Crear un frame para la lista de clientes
        client_frame = ttk.Frame(self.window)
        client_frame.pack(padx=10, pady=10, expand=True)

        # Crear una tabla para mostrar los clientes
        self.client_table = ttk.Treeview(client_frame, columns=("ID", "Nombre", "Apellido", "Email", "Teléfono"), show="headings")
        self.client_table.heading("ID", text="ID")
        self.client_table.heading("Nombre", text="Nombre")
        self.client_table.heading("Apellido", text="Apellido")
        self.client_table.heading("Email", text="Email")
        self.client_table.heading("Teléfono", text="Teléfono")

        # Configurar el ancho de las columnas
        self.client_table.column("ID", width=50)
        self.client_table.column("Nombre", width=100)
        self.client_table.column("Apellido", width=100)
        self.client_table.column("Email", width=150)
        self.client_table.column("Teléfono", width=100)

        # Añadir la tabla al frame
        self.client_table.pack(fill=tk.BOTH, expand=True)

        # Crear un botón para eliminar cliente
        delete_button = ttk.Button(client_frame, text="Eliminar Cliente", command=self.delete_client)
        delete_button.pack(pady=10)

        # Cargar los clientes desde la base de datos
        self.load_clients()

    def load_clients(self):
        """Cargar los clientes desde la base de datos y mostrarlos en la tabla"""
        db = Database()
        if db.connect():
            clients = db.get_all_clients()  # Asumimos que este método existe en la clase Database
            for client in clients:
                self.client_table.insert("", "end", values=client)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def delete_client(self):
        """Eliminar el cliente seleccionado"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para eliminar.")
            return

        client_id = self.client_table.item(selected_item)['values'][0]
        client_controller = ClientController()
        if client_controller.delete_client(client_id):
            self.client_table.delete(selected_item)
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
        else:
            messagebox.showerror("Error", "No se pudo eliminar el cliente")

    def show(self):
        """Mostrar la ventana"""
        self.window.mainloop()
