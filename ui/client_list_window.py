import tkinter as tk
from tkinter import ttk, messagebox

from controllers.database import Database
from controllers.client_controller import ClientController

class EditClientWindow:
    def __init__(self, master, client_id, client_list_window):
        self.master = master
        self.client_id = client_id
        self.client_list_window = client_list_window

        self.window = tk.Toplevel(master)
        self.window.title("Editar Cliente")
        self.window.geometry("500x450")
        self.window.configure(bg="#f8f9fa")
        self.window.transient(master)

        # Estilos locales
        style = ttk.Style(self.window)
        style.configure("EditHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("EditSection.TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_frame = ttk.Frame(self.window, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"Editando Cliente #{client_id}", style="EditHeader.TLabel").pack(pady=(0, 25))

        # Frame principal del formulario
        sec_form = ttk.LabelFrame(main_frame, text=" Información Personal ", padding=20, style="EditSection.TLabelframe")
        sec_form.pack(fill=tk.X, pady=10)
        sec_form.columnconfigure(1, weight=1)

        # Campos del formulario
        self.fields = {
            "nombre": tk.StringVar(),
            "apellido": tk.StringVar(),
            "email": tk.StringVar(),
            "telefono": tk.StringVar()
        }

        fields_order = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Email:", "email"),
            ("Teléfono:", "telefono")
        ]

        for i, (label_text, field_name) in enumerate(fields_order):
            ttk.Label(sec_form, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            ttk.Entry(sec_form, textvariable=self.fields[field_name]).grid(row=i, column=1, sticky=tk.EW, pady=8)

        # Cargar los datos del cliente
        self.load_client_data()

        # Botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 20, 0, 0))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="GUARDAR CAMBIOS", style="Action.TButton", command=self.save_changes).pack(side=tk.RIGHT, padx=5)

    def load_client_data(self):
        """Cargar los datos del cliente desde la base de datos"""
        db = Database()
        if db.connect():
            query = "SELECT nombre, apellido, email, telefono FROM clientes WHERE id_clientes = %s"
            cursor = db.connection.cursor()
            cursor.execute(query, (self.client_id,))
            result = cursor.fetchone()
            if result:
                self.fields["nombre"].set(result[0])
                self.fields["apellido"].set(result[1])
                self.fields["email"].set(result[2])
                self.fields["telefono"].set(result[3])
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def save_changes(self):
        """Guardar los cambios en la base de datos"""
        if not self.fields["nombre"].get() or not self.fields["apellido"].get() or not self.fields["email"].get() or not self.fields["telefono"].get():
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        client_data = (
            self.fields["nombre"].get(),
            self.fields["apellido"].get(),
            self.fields["email"].get(),
            self.fields["telefono"].get()
        )

        db = Database()
        if db.connect():
            query = "UPDATE clientes SET nombre=%s, apellido=%s, email=%s, telefono=%s WHERE id_clientes=%s"
            cursor = db.connection.cursor()
            cursor.execute(query, client_data + (self.client_id,))
            db.connection.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado exitosamente", parent=self.window)
            self.window.destroy()
            self.client_list_window.refresh_clients()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

class ClientListWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Gestión de Clientes")
        self.window.geometry("900x650")
        self.window.configure(bg="#f8f9fa")

        # Estilos locales
        style = ttk.Style(self.window)
        style.configure("Dashboard.TFrame", background="#f8f9fa")
        style.configure("Card.TFrame", background="white", relief="ridge")
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("Stat.TLabel", font=("Segoe UI", 10), foreground="#7f8c8d", background="#f8f9fa")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_container = ttk.Frame(self.window, padding=20, style="Dashboard.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- CABECERA ---
        header_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header_frame, text="Directorio de Clientes", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.lbl_total_clients = ttk.Label(header_frame, text="Total: 0 clientes", style="Stat.TLabel")
        self.lbl_total_clients.pack(side=tk.LEFT, padx=20, pady=(10, 0))

        # --- BARRA DE BÚSQUEDA ---
        search_card = ttk.Frame(main_container, padding=15, style="Card.TFrame")
        search_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_card, text="Buscar:", font=("Segoe UI", 10, "bold"), background="white").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_card, textvariable=self.search_var, font=("Segoe UI", 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_clients())

        ttk.Button(search_card, text="Actualizar", command=self.refresh_clients).pack(side=tk.RIGHT, padx=5)

        # --- TABLA DE CLIENTES ---
        table_frame = ttk.Frame(main_container, style="Card.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.client_table = ttk.Treeview(table_frame, columns=("ID", "Nombre", "Apellido", "Email", "Teléfono"), 
                                         show="headings", yscrollcommand=tree_scroll.set, selectmode="browse")
        self.client_table.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        tree_scroll.config(command=self.client_table.yview)

        # Cabeceras
        self.client_table.heading("ID", text="ID", anchor=tk.CENTER)
        self.client_table.heading("Nombre", text="Nombre", anchor=tk.W)
        self.client_table.heading("Apellido", text="Apellido", anchor=tk.W)
        self.client_table.heading("Email", text="Email", anchor=tk.W)
        self.client_table.heading("Teléfono", text="Teléfono", anchor=tk.W)

        # Columnas
        self.client_table.column("ID", width=60, anchor=tk.CENTER)
        self.client_table.column("Nombre", width=150)
        self.client_table.column("Apellido", width=150)
        self.client_table.column("Email", width=250)
        self.client_table.column("Teléfono", width=150)

        # --- BARRA DE ACCIONES (INFERIOR) ---
        actions_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        actions_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(actions_frame, text="ELIMINAR SELECCIONADO", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="EDITAR CLIENTE", style="Action.TButton", command=self.edit_client).pack(side=tk.RIGHT, padx=5)

        # Cargar los clientes
        self.load_clients()

    def load_clients(self):
        """Cargar los clientes desde la base de datos y mostrarlos en la tabla"""
        db = Database()
        if db.connect():
            clients = db.get_all_clients()
            self.lbl_total_clients.config(text=f"Total: {len(clients)} clientes")
            for client in clients:
                self.client_table.insert("", "end", values=client)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def filter_clients(self):
        """Filtrar los clientes en tiempo real"""
        search_text = self.search_var.get().lower()
        self.refresh_clients_with_filter(search_text)

    def refresh_clients_with_filter(self, filter_text):
        for item in self.client_table.get_children():
            self.client_table.delete(item)
        
        db = Database()
        if db.connect():
            clients = db.get_all_clients()
            filtered = []
            for c in clients:
                # c = (id, nombre, apellido, email, telefono)
                full_name = f"{c[1]} {c[2]}".lower()
                # También permitimos apellido + nombre por si acaso
                full_name_reverse = f"{c[2]} {c[1]}".lower()
                
                # Buscar en campos individuales Y en el nombre completo
                searchable_values = [str(v).lower() for v in c]
                if (filter_text in full_name or 
                    filter_text in full_name_reverse or 
                    any(filter_text in v for v in searchable_values)):
                    filtered.append(c)
            
            for client in filtered:
                self.client_table.insert("", "end", values=client)
            self.lbl_total_clients.config(text=f"Encontrados: {len(filtered)} de {len(clients)}")

    def delete_client(self):
        """Eliminar el cliente seleccionado"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para eliminar.")
            return

        client_id = self.client_table.item(selected_item)['values'][0]
        client_name = self.client_table.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirmación", f"¿Está seguro de eliminar a {client_name}?"):
            client_controller = ClientController()
            if client_controller.delete_client(client_id):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self.refresh_clients()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente")

    def edit_client(self):
        """Editar el cliente seleccionado"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para editar.")
            return

        client_id = self.client_table.item(selected_item)['values'][0]
        EditClientWindow(self.window, client_id, self)

    def refresh_clients(self):
        """Refrescar la lista de clientes"""
        self.search_var.set("")
        for item in self.client_table.get_children():
            self.client_table.delete(item)
        self.load_clients()

    def show(self):
        pass
