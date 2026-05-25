from controllers.database import Database
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import calendar

class CalendarDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.geometry("400x380") # Aumentado el ancho de 300 a 400
        self.callback = callback
        self.now = date.today()
        self.year = self.now.year
        self.month = self.now.month
        
        self.setup_ui()
        self.draw_calendar()
        self.grab_set() # Hacer el diálogo modal

    def setup_ui(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(header, text="<<", width=5, command=self.prev_month).pack(side=tk.LEFT)
        self.month_label = ttk.Label(header, text="", font=('Arial', 12, 'bold'))
        self.month_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(header, text=">>", width=5, command=self.next_month).pack(side=tk.RIGHT)
        
        days_header = ttk.Frame(self)
        days_header.pack(fill=tk.X, padx=10)
        # Nombres de días con un poco más de espacio
        for d in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]:
            ttk.Label(days_header, text=d, width=5, anchor="center", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, expand=True)
            
        self.days_frame = ttk.Frame(self)
        self.days_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def draw_calendar(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()
            
        # Nombres de meses en español (manual para evitar dependencia de locale)
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        self.month_label.config(text=f"{meses[self.month]} {self.year}")
        
        cal = calendar.monthcalendar(self.year, self.month)
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.days_frame, text="").grid(row=row_idx, column=col_idx, sticky="nsew")
                else:
                    # Botones más anchos y con padding
                    btn = ttk.Button(self.days_frame, text=str(day), width=5,
                                    command=lambda d=day: self.select_day(d))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")
                    
                    if day == self.now.day and self.month == self.now.month and self.year == self.now.year:
                        # Resaltar el día actual si es posible
                        pass

        for i in range(7):
            self.days_frame.columnconfigure(i, weight=1)
        for i in range(len(cal)):
            self.days_frame.rowconfigure(i, weight=1)

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.draw_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.draw_calendar()

    def select_day(self, day):
        selected_date = f"{day:02d}/{self.month:02d}/{self.year}"
        self.callback(selected_date)
        self.destroy()

class ReservationController:
    def __init__(self, master):
        self.master = master
        self.db = Database()
        # Configurar nombres de meses en español
        self.months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
    
    def create_reservation(self):
        # Lógica para crear una nueva reserva
        print("Crear Reserva")
        
        # Crear una nueva ventana para el formulario de reserva
        reservation_window = tk.Toplevel(self.master)
        reservation_window.title("Detalle de Reserva")
        reservation_window.geometry("800x700")

        # Frame principal del formulario
        form_frame = ttk.Frame(reservation_window)
        form_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Mensaje para notificaciones
        message_label = ttk.Label(form_frame, text="Ingrese los datos de la reserva", font=('Arial', 14))
        message_label.pack(side=tk.TOP, padx=5, pady=5)

        # Campos del formulario
        fields = [
            ("ID Cliente:", "id_clientes"),
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Correo electrónico:", "email"),
            ("Teléfono:", "telefono"),
            ("Provincia:", "provincia"),
            ("Fecha de registro:", "fecha_registro"),
            ("Cantidad de personas:", "cantidad_personas"),
            ("Porcentaje de adelanto:", "porcentaje_adelanto"),
            ("Adelanto:", "adelanto"),
            ("Porcentaje de descuento:", "porcentaje_descuento"),
            ("Descuento:", "descuento"),
            ("Inmueble:", "inmueble"),
            ("Valor por Día:", "valor_dia"),
            ("Fecha de ingreso:", "fecha_ingreso"),
            ("Fecha de egreso:", "fecha_egreso"),
            ("Costo Total:", "costo_total")
        ]

        client_fields = {
            "id_clientes": tk.StringVar(),
            "nombre": tk.StringVar(),
            "apellido": tk.StringVar(),
            "email": tk.StringVar(),
            "telefono": tk.StringVar(),
            "provincia": tk.StringVar(),
            "fecha_registro": tk.StringVar(),
            "cantidad_personas": tk.StringVar(),
            "porcentaje_adelanto": tk.StringVar(),
            "adelanto": tk.StringVar(),
            "porcentaje_descuento": tk.StringVar(),
            "descuento": tk.StringVar(),
            "inmueble": tk.StringVar(),
            "valor_dia": tk.StringVar(),
            "fecha_ingreso": tk.StringVar(),
            "fecha_egreso": tk.StringVar(),
            "costo_total": tk.StringVar()
        }

        # Establecer fecha de registro y provincia por defecto
        client_fields["fecha_registro"].set(date.today().strftime("%d/%m/%Y"))
        client_fields["provincia"].set("Buenos Aires")

        provincias = [
            "Buenos Aires", "Catamarca", "Chaco", "Chubut", "CABA",
            "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
            "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén",
            "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz",
            "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"
        ]

        def filtrar_provincias(entry, var):
            _last_filter = {}
            def _on_keyrelease(event):
                nonlocal _last_filter
                typing = var.get().lower()
                if _last_filter.get(id(entry)) == typing:
                    return
                _last_filter[id(entry)] = typing
                filtradas = [p for p in provincias if p.lower().startswith(typing)]
                entry['values'] = filtradas if filtradas else provincias
                if filtradas:
                    entry.event_generate('<Down>')
            return _on_keyrelease

        for field in fields:
            row = ttk.Frame(form_frame)
            row.pack(fill=tk.X, padx=5, pady=2)

            label = ttk.Label(row, text=field[0], width=20)
            label.pack(side=tk.LEFT)

            if field[1] == "provincia":
                var = client_fields["provincia"]
                entry = ttk.Combobox(row, textvariable=var, values=provincias)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                entry.bind("<KeyRelease>", filtrar_provincias(entry, var))
            elif field[1] == "inmueble":
                # Cargar los inmuebles desde la base de datos
                if not self.db.connection or not self.db.connection.is_connected():
                    self.db.connect()
                
                properties = self.db.get_all_properties()
                self.property_map = {p[1]: p for p in properties}
                property_names = list(self.property_map.keys())
                entry = ttk.Combobox(row, textvariable=client_fields[field[1]], values=property_names, state="readonly")
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

                def on_inmueble_select(event):
                    selected = client_fields["inmueble"].get()
                    if selected in self.property_map:
                        valor = self.property_map[selected][7]
                        client_fields["valor_dia"].set(f"${valor:,.2f}")
                        self.update_cost_total(client_fields)  # <-- Aquí se llama a la función de actualización

                entry.bind("<<ComboboxSelected>>", on_inmueble_select)
            elif field[1] == "valor_dia":
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field[1] in ["fecha_ingreso", "fecha_egreso"]:
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                date_btn = ttk.Button(
                    row, 
                    text="📅", 
                    width=3,
                    command=lambda f=field[1]: self.select_date(f, client_fields, reservation_window)
                )
                date_btn.pack(side=tk.RIGHT, padx=5)
            else:
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            # Si es el campo ID Cliente, vincular la tecla Enter para autocompletar
            if field[1] == "id_clientes":
                entry.bind("<Return>", lambda event: self.autofill_client_data(client_fields))

        # Botón para reservar
        reserve_button = ttk.Button(
            form_frame,
            text="Reservar",
            command=lambda: self.save_reservation(reservation_window, client_fields),
            style="TButton"
        )
        reserve_button.pack(pady=10, side=tk.BOTTOM)

    def select_date(self, field_name, client_fields, parent):
        """Abrir un diálogo de calendario visual para seleccionar la fecha"""
        def update_date_field(selected_date):
            client_fields[field_name].set(selected_date)
            self.update_cost_total(client_fields)
            
        CalendarDialog(parent, update_date_field)

    def autofill_client_data(self, client_fields):
        # Obtener el ID del cliente ingresado
        client_id = client_fields["id_clientes"].get()
        
        if not client_id:
            return

        # Asegurar que la base de datos esté conectada
        if not self.db.connection or not self.db.connection.is_connected():
            if not self.db.connect():
                messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.master)
                return

        # Buscar el cliente en la base de datos
        client_data = self.db.get_client_by_id(client_id)

        if client_data:
            client_fields["nombre"].set(client_data[1])
            client_fields["apellido"].set(client_data[2])
            client_fields["email"].set(client_data[3])
            client_fields["telefono"].set(client_data[4])
        else:
            messagebox.showerror("Error", "Cliente no encontrado", parent=self.master)

    def update_cost_total(self, client_fields):
        # Obtener valores del formulario
        fecha_ingreso_str = client_fields["fecha_ingreso"].get()
        fecha_egreso_str = client_fields["fecha_egreso"].get()
        valor_dia_str = client_fields["valor_dia"].get()
        
        if not (fecha_ingreso_str and fecha_egreso_str and valor_dia_str):
            return

        try:
            # Convertir fechas a objetos date
            fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%d/%m/%Y").date()
            fecha_egreso = datetime.strptime(fecha_egreso_str, "%d/%m/%Y").date()
            
            # Calcular número de noches
            delta = fecha_egreso - fecha_ingreso
            noches = delta.days
            
            # Convertir valor por día a número
            valor_dia = float(valor_dia_str.replace('$', '').replace(',', ''))  # Remover símbolos antes de convertir
            
            # Calcular costo total
            costo_total = noches * valor_dia
            
            # Actualizar campo de costo total
            client_fields["costo_total"].set(f"${costo_total:,.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha inválido: {str(e)}", parent=self.master)

    def save_reservation(self, reservation_window, client_fields):
        # Obtener valores del formulario
        fecha_ingreso_str = client_fields["fecha_ingreso"].get()
        fecha_egreso_str = client_fields["fecha_egreso"].get()
        valor_dia_str = client_fields["valor_dia"].get()
        
        # Validar campos obligatorios
        if not (fecha_ingreso_str and fecha_egreso_str and valor_dia_str):
            messagebox.showerror("Error", "Por favor complete todos los campos", parent=reservation_window)
            return

        try:
            # Convertir fechas a objetos date
            fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%d/%m/%Y").date()
            fecha_egreso = datetime.strptime(fecha_egreso_str, "%d/%m/%Y").date()
            
            # Calcular número de noches
            delta = fecha_egreso - fecha_ingreso
            noches = delta.days
            
            # Convertir valor por día a número
            valor_dia = float(valor_dia_str.replace('$', '').replace(',', ''))  # Remover símbolos antes de convertir
            
            # Calcular costo total
            costo_total = noches * valor_dia
            
            # Actualizar campo de costo total
            client_fields["costo_total"].set(f"${costo_total:,.2f}")
            
            # Guardar la reserva en la base de datos
            reservation_data = {
                "fecha_ingreso": fecha_ingreso,
                "fecha_egyreso": fecha_egreso,
                "valor_dia": valor_dia,
                "noches": noches,
                "costo_total": costo_total
            }
            
            # Lógica para guardar en la base de datos
            self.db.insert_reservation(reservation_data)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Reserva guardada correctamente", parent=reservation_window)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha inválido: {str(e)}", parent=reservation_window)
