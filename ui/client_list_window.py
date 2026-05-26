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
        self.window.title("Perfil de Cliente - Panel de Gestión")
        self.window.geometry("550x550")
        self.window.configure(bg="#f0f2f5")
        self.window.transient(master)

        # --- ESTILOS LOCALES ---
        style = ttk.Style(self.window)
        style.configure("EditHeader.TFrame", background="#2c3e50")
        style.configure("EditContent.TFrame", background="#f0f2f5")
        style.configure("EditSection.TLabelframe", font=("Segoe UI", 10, "bold"), background="white")
        style.configure("EditAction.TButton", font=("Segoe UI", 10, "bold"), padding=12)

        # --- ENCABEZADO ---
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"👤 PERFIL DEL CLIENTE #{client_id}", font=("Segoe UI", 14, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=30, pady=18)

        # --- CONTENIDO ---
        main_frame = ttk.Frame(self.window, padding=30, style="EditContent.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tarjeta de Datos
        sec_form = tk.LabelFrame(main_frame, text=" INFORMACIÓN PERSONAL ", font=("Segoe UI", 9, "bold"), 
                                bg="white", fg="#2c3e50", padx=25, pady=25, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        sec_form.pack(fill=tk.X, pady=10)
        sec_form.columnconfigure(1, weight=1)

        # Campos del formulario
        self.fields = {
            "documento": tk.StringVar(),
            "nombre": tk.StringVar(),
            "apellido": tk.StringVar(),
            "email": tk.StringVar(),
            "telefono": tk.StringVar()
        }

        fields_order = [
            ("DOCUMENTO:", "documento"),
            ("NOMBRE:", "nombre"),
            ("APELLIDO:", "apellido"),
            ("CORREO ELECTRÓNICO:", "email"),
            ("TELÉFONO DE CONTACTO:", "telefono")
        ]

        for i, (label_text, field_name) in enumerate(fields_order):
            tk.Label(sec_form, text=label_text, bg="white", font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky=tk.W, pady=12, padx=(0, 15))
            ttk.Entry(sec_form, textvariable=self.fields[field_name], font=("Segoe UI", 10)).grid(row=i, column=1, sticky=tk.EW, pady=12)

        # Cargar los datos del cliente
        self.load_client_data()

        # Barra de Botones Inferior
        btn_container = tk.Frame(self.window, bg="#f0f2f5", pady=25, padx=30)
        btn_container.pack(fill=tk.X)
        
        ttk.Button(btn_container, text="CANCELAR", command=self.window.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_container, text="GUARDAR CAMBIOS", style="EditAction.TButton", 
                   command=self.save_changes).pack(side=tk.RIGHT)

    def load_client_data(self):
        """Cargar los datos del cliente desde la base de datos"""
        db = Database()
        if db.connect():
            query = "SELECT nombre, apellido, email, telefono, documento FROM clientes WHERE id_clientes = %s"
            cursor = db.connection.cursor()
            cursor.execute(query, (self.client_id,))
            result = cursor.fetchone()
            if result:
                self.fields["nombre"].set(result[0])
                self.fields["apellido"].set(result[1])
                self.fields["email"].set(result[2])
                self.fields["telefono"].set(result[3])
                self.fields["documento"].set(result[4] if result[4] else "")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

    def save_changes(self):
        """Guardar los cambios en la base de datos"""
        if not self.fields["nombre"].get() or not self.fields["apellido"].get() or not self.fields["email"].get() or not self.fields["telefono"].get() or not self.fields["documento"].get():
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        client_data = (
            self.fields["nombre"].get(),
            self.fields["apellido"].get(),
            self.fields["email"].get(),
            self.fields["telefono"].get(),
            self.fields["documento"].get()
        )

        db = Database()
        if db.connect():
            query = "UPDATE clientes SET nombre=%s, apellido=%s, email=%s, telefono=%s, documento=%s WHERE id_clientes=%s"
            cursor = db.connection.cursor()
            cursor.execute(query, client_data + (self.client_id,))
            db.connection.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado exitosamente", parent=self.window)
            self.window.destroy()
            self.client_list_window.refresh_clients()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

class ClientListWindow:
    def __init__(self, master, select_callback=None):
        self.master = master
        self.select_callback = select_callback

        self.window = tk.Toplevel(master)
        self.window.title("Directorio de Clientes - Gestión Hotelera")
        self.window.geometry("1000x750")
        self.window.configure(bg="#f0f2f5")

        # --- ESTILOS LOCALES ---
        style = ttk.Style(self.window)
        style.configure("ClDashboard.TFrame", background="#f0f2f5")
        style.configure("ClCard.TFrame", background="white", relief="flat")
        style.configure("ClHeader.TLabel", font=("Segoe UI", 20, "bold"), foreground="#2c3e50", background="#f0f2f5")
        style.configure("ClStat.TLabel", font=("Segoe UI", 11), foreground="#7f8c8d", background="#f0f2f5")
        style.configure("ClAction.TButton", font=("Segoe UI", 10, "bold"), padding=12)

        # --- ENCABEZADO DASHBOARD ---
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="👥 DIRECTORIO DE CLIENTES", font=("Segoe UI", 16, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=30, pady=20)
        
        self.lbl_total_clients = tk.Label(header_frame, text="Cargando...", font=("Segoe UI", 10), 
                                         bg="#2c3e50", fg="#95a5a6")
        self.lbl_total_clients.pack(side=tk.RIGHT, padx=30)

        main_container = ttk.Frame(self.window, padding=30, style="ClDashboard.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- ÁREA DE BÚSQUEDA (CARD) ---
        search_card = tk.Frame(main_container, bg="white", highlightbackground="#e0e0e0", highlightthickness=1, padx=20, pady=20)
        search_card.pack(fill=tk.X, pady=(0, 25))
        
        tk.Label(search_card, text="🔎 FILTRAR DIRECTORIO:", font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 15))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_card, textvariable=self.search_var, font=("Segoe UI", 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_clients())

        ttk.Button(search_card, text="RECARGAR LISTA", command=self.refresh_clients).pack(side=tk.RIGHT, padx=(15, 0))

        # --- TABLA DE RESULTADOS (CARD) ---
        table_container = tk.Frame(main_container, bg="white", highlightbackground="#e0e0e0", highlightthickness=1, padx=2, pady=2)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(table_container)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.client_table = ttk.Treeview(table_container, columns=("ID", "Documento", "Nombre", "Apellido", "Email", "Teléfono"), 
                                         show="headings", yscrollcommand=tree_scroll.set, selectmode="browse")
        self.client_table.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.client_table.yview)

        # Cabeceras y Columnas
        headers = [("ID", 60, tk.CENTER), ("Documento", 110, tk.W), ("Nombre", 160, tk.W), ("Apellido", 160, tk.W), ("Email", 240, tk.W), ("Teléfono", 140, tk.W)]
        for h, w, a in headers:
            self.client_table.heading(h, text=h.upper(), anchor=a)
            self.client_table.column(h, width=w, anchor=a)

        # --- BARRA DE ACCIONES INFERIOR ---
        actions_frame = ttk.Frame(main_container, style="ClDashboard.TFrame")
        actions_frame.pack(fill=tk.X, pady=(25, 0))

        if self.select_callback:
            ttk.Button(actions_frame, text="✅ SELECCIONAR CLIENTE PARA RESERVA", 
                       style="ClAction.TButton", command=self.select_client_and_close).pack(side=tk.RIGHT)
            self.client_table.bind("<Double-Button-1>", lambda e: self.select_client_and_close())
        else:
            ttk.Button(actions_frame, text="ELIMINAR SELECCIONADO", command=self.delete_client).pack(side=tk.LEFT)
            ttk.Button(actions_frame, text="GESTIONAR PERFIL", style="ClAction.TButton", command=self.edit_client).pack(side=tk.RIGHT)

        # Cargar los clientes
        self.load_clients()

    def select_client_and_close(self):
        """Selecciona el cliente y llama al callback"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente.", parent=self.window)
            return
        
        client_data = self.client_table.item(selected_item)['values']
        self.select_callback(client_data) # Enviamos todos los valores (id, documento, nombre, apellido, email, telefono)
        self.window.destroy()

    def load_clients(self):
        """Cargar los clientes desde la base de datos y mostrarlos en la tabla"""
        db = Database()
        if db.connect():
            clients = db.get_all_clients()
            self.lbl_total_clients.config(text=f"TOTAL: {len(clients)} CLIENTES")
            for client in clients:
                self.client_table.insert("", "end", values=client)
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

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
                # c = (id, documento, nombre, apellido, email, telefono)
                full_name = f"{c[2]} {c[3]}".lower()
                full_name_reverse = f"{c[3]} {c[2]}".lower()
                searchable_values = [str(v).lower() for v in c]
                if (filter_text in full_name or 
                    filter_text in full_name_reverse or 
                    any(filter_text in v for v in searchable_values)):
                    filtered.append(c)
            
            for client in filtered:
                self.client_table.insert("", "end", values=client)
            self.lbl_total_clients.config(text=f"RESULTADOS: {len(filtered)} / TOTAL: {len(clients)}")

    def delete_client(self):
        """Eliminar el cliente seleccionado"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para eliminar.", parent=self.window)
            return

        client_id = self.client_table.item(selected_item)['values'][0]
        client_name = self.client_table.item(selected_item)['values'][1]

        if messagebox.askyesno("Confirmación", f"¿Está seguro de eliminar a {client_name}?", parent=self.window):
            client_controller = ClientController()
            if client_controller.delete_client(client_id):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente", parent=self.window)
                self.refresh_clients()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente", parent=self.window)

    def edit_client(self):
        """Editar el cliente seleccionado"""
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para editar.", parent=self.window)
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
