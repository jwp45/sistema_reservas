import tkinter as tk
from tkinter import ttk, messagebox
from controllers.database import Database

class ClientListWindow:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Lista de Clientes")
        self.window.geometry("700x500")

        # Crear un frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Crear un frame para la tabla
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Crear una tabla para mostrar los clientes
        self.client_table = ttk.Treeview(table_frame, columns=("ID", "Nombre", "Apellido", "Email", "Teléfono"), show="headings")
        
        self.client_table.heading("ID", text="ID")
        self.client_table.heading("Nombre", text="Nombre")
        self.client_table.heading("Apellido", text="Apellido")
        self.client_table.heading("Email", text="Email")
        self.client_table.heading("Teléfono", text="Teléfono")

        # Configurar el ancho de las columnas
        self.client_table.column("ID", width=50, anchor="center")
        self.client_table.column("Nombre", width=100)
        self.client_table.column("Apellido", width=100)
        self.client_table.column("Email", width=200)
        self.client_table.column("Teléfono", width=100)

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.client_table.yview)
        self.client_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.client_table.pack(fill=tk.BOTH, expand=True)

        # Frame para botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Botón para eliminar cliente
        self.btn_delete = ttk.Button(
            button_frame, 
            text="Eliminar Cliente Seleccionado", 
            command=self.handle_delete_client
        )
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        # Botón para refrescar la lista
        self.btn_refresh = ttk.Button(
            button_frame, 
            text="Refrescar Lista", 
            command=self.load_clients
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        # Cargar los clientes desde la base de datos
        self.load_clients()

    def load_clients(self):
        """Cargar los clientes desde la base de datos y mostrarlos en la tabla"""
        # Limpiar la tabla antes de cargar
        for item in self.client_table.get_children():
            self.client_table.delete(item)

        db = Database()
        if db.connect():
            clients = db.get_all_clients()
            for client in clients:
                self.client_table.insert("", "end", values=client)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def handle_delete_client(self):
        """Manejar la eliminación del cliente seleccionado"""
        selected_item = self.client_table.selection()
        
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente de la lista.")
            return

        # Obtener los datos de la fila seleccionada (el ID es el primer elemento)
        item_values = self.client_table.item(selected_item, 'values')
        client_id = item_values[0]
        client_name = f"{item_values[1]} {item_values[2]}"

        # Confirmar eliminación
        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar al cliente {client_name} (ID: {client_id})?"
        )

        if confirm:
            db = Database()
            if db.connect():
                if db.delete_client(client_id):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                    self.load_clients()  # Refrescar la tabla
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente.")
            else:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

    def show(self):
        """Mostrar la ventana"""
        self.window.focus_set()
        self.window.grab_set() # Hacer la ventana modal
        self.window.wait_window()
