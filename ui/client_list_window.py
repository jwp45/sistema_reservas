import tkinter as tk
from tkinter import ttk, messagebox, StringVar, Frame

class ClientListWindow:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Lista de Clientes")
        self.root.geometry("450x300")

        # Frame principal del formulario
        form_frame = ttk.Frame(self.root)
        form_frame.pack(padx=10, pady=10, expand=True)

        # Lista de clientes
        self.client_list = ttk.Treeview(form_frame, columns=("ID", "Nombre", "Apellido", "Email", "Teléfono"), show="headings")
        self.client_list.heading("ID", text="ID Cliente")
        self.client_list.heading("Nombre", text="Nombre")
        self.client_list.heading("Apellido", text="Apellido")
        self.client_list.heading("Email", text="Correo electrónico")
        self.client_list.heading("Teléfono", text="Teléfono")
        self.client_list.pack(fill=tk.BOTH, expand=True)

        # Botón para cargar clientes
        load_button = ttk.Button(
            form_frame,
            text="Cargar Clientes",
            command=lambda: self.load_clients(),
            style="TButton"
        )
        load_button.pack(pady=10, side=tk.BOTTOM)

    def load_clients(self):
        """Cargar los clientes en la lista"""
        client_controller = ClientController()
        clients = client_controller.get_all_clients()

        for client in clients:
            self.client_list.insert("", tk.END, values=client)
