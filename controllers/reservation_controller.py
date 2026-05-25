from controllers.database import Database
from utils.email_sender import send_reservation_email
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import calendar

class CalendarDialog(tk.Toplevel):
    def __init__(self, parent, callback, reserved_ranges=None):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.geometry("400x500")
        self.callback = callback
        self.reserved_ranges = reserved_ranges or []
        self.now = date.today()
        self.year = self.now.year
        self.month = self.now.month

        style = ttk.Style(self)
        style.configure("Reserved.TButton", background="gray")

        self.setup_ui()
        self.draw_calendar()
        self.grab_set()

    def _is_reserved(self, d):
        for ingreso, egreso in self.reserved_ranges:
            if isinstance(ingreso, str):
                ingreso = datetime.strptime(str(ingreso), "%Y-%m-%d").date()
            if isinstance(egreso, str):
                egreso = datetime.strptime(str(egreso), "%Y-%m-%d").date()
            if ingreso <= d < egreso:
                return True
        return False

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
                    d = date(self.year, self.month, day)
                    is_reserved = self._is_reserved(d)
                    btn = ttk.Button(self.days_frame, text=str(day), width=5,
                                    state=tk.DISABLED if is_reserved else tk.NORMAL,
                                    command=lambda dd=day: self.select_day(dd))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

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
        try:
            selected_date_obj = date(self.year, self.month, day)
            
            # Validación: La fecha seleccionada no debe ser anterior a hoy
            if selected_date_obj < self.now:
                messagebox.showwarning("Fecha Inválida", "No es posible seleccionar una fecha pasada. Por favor, elija una fecha a partir de hoy.", parent=self)
                return
            
            selected_date_str = f"{day:02d}/{self.month:02d}/{self.year}"
            self.callback(selected_date_str)
            self.destroy()
        except Exception as e:
            # Manejo de cualquier error de fecha inesperado
            messagebox.showerror("Error", f"Error al seleccionar la fecha: {e}", parent=self)
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
    
    def _format_with_thousands_separator(self, number_str):
        """Función auxiliar para añadir separadores de miles a una cadena numérica."""
        if not number_str:
            return ""
        
        # Separar la parte entera y decimal
        parts = number_str.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""
        
        # Formatear la parte entera
        formatted_integer = ""
        for i in range(len(integer_part) - 1, -1, -1):
            formatted_integer = integer_part[i] + formatted_integer
            if i > 0 and (len(integer_part) - i) % 3 == 0:
                formatted_integer = "," + formatted_integer
        
        return f"{formatted_integer}.{decimal_part}"


    def format_discount_input(self, event, client_fields):
        text = client_fields["descuento"].get()
        cleaned_text = ''.join(filter(lambda char: char.isdigit() or char == '.', text))

        if client_fields["discount_is_percentage"].get():
            client_fields["descuento"].set(cleaned_text)
        else:
            new_value = self._format_with_thousands_separator(cleaned_text)
            client_fields["descuento"].set(new_value)

        self.update_cost_total(client_fields)


    def format_down_payment_input(self, event, client_fields):
        """Formatea el campo de adelanto con separador de miles y recalcula costos."""
        text = client_fields["adelanto"].get()
        
        # 1. Limpiar: dejar solo dígitos y un punto decimal
        # Esto permite que el usuario escriba números sin formato.
        cleaned_text = ''.join(filter(lambda char: char.isdigit() or char == '.', text))
        
        # 2. Formatear el valor limpio
        new_value = self._format_with_thousands_separator(cleaned_text)
        
        # 3. Actualizar el StringVar
        client_fields["adelanto"].set(new_value)
        
        # 4. Recalcular costos
        self.update_cost_total(client_fields)


    def create_reservation(self):
        # Lógica para crear una nueva reserva
        print("Crear Reserva")
        
        # Crear una nueva ventana para el formulario de reserva
        reservation_window = tk.Toplevel(self.master)
        reservation_window.title("Detalle de Reserva")
        reservation_window.geometry("800x700") # Aumentado el tamaño para acomodar el resumen
        
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
            ("Inmueble:", "inmueble"), # Movido arriba
            ("Cantidad de personas:", "cantidad_personas"), # Movido abajo
            ("Adelanto:", "adelanto"),
            ("Descuento:", "descuento"),
            ("Valor por Día:", "valor_dia"),
            ("Fecha de ingreso:", "fecha_ingreso"),
            ("Fecha de egreso:", "fecha_egreso"),
            ("Cantidad de Noches:", "noches"),
            ("Costo Total:", "costo_total"),
            ("Costo con Descuento:", "costo_con_descuento"),
            ("Pago pendiente:", "pago_pendiente") # Campo principal
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
            "adelanto": tk.StringVar(),
            "descuento": tk.StringVar(),
            "inmueble": tk.StringVar(),
            "valor_dia": tk.StringVar(),
            "fecha_ingreso": tk.StringVar(),
            "fecha_egreso": tk.StringVar(),
            "noches": tk.StringVar(),
            "costo_total": tk.StringVar(),
            "costo_con_descuento": tk.StringVar(),
            "pago_pendiente": tk.StringVar(),
            # Checkbox para modo porcentaje en descuento
            "discount_is_percentage": tk.BooleanVar(),
            # Nuevos campos de resumen visual
            "display_adelanto": tk.StringVar(),
            "display_descuento": tk.StringVar()
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
                        property_data = self.property_map[selected]
                        # Valor por Día (asumiendo índice 7)
                        valor = property_data[7]
                        client_fields["valor_dia"].set(f"${valor:,.2f}")
                        
                        # Capacidad de personas (asumiendo índice 2)
                        capacidad = property_data[2]
                        client_fields["cantidad_personas"].set(str(capacidad))
                        
                        self.update_cost_total(client_fields)  # <-- Aquí se llama a la función de actualización

                entry.bind("<<ComboboxSelected>>", on_inmueble_select)
            elif field[1] == "cantidad_personas":
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field[1] == "valor_dia":
                # Contenedor para el símbolo $ y el campo de entrada
                currency_frame = ttk.Frame(row)
                currency_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Etiqueta del símbolo $
                ttk.Label(currency_frame, text="$", width=3, anchor="n").pack(side=tk.LEFT)
                
                # Campo de entrada
                entry = ttk.Entry(currency_frame, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Bindings actualizados: KeyRelease para formato, Return para cálculo
                entry.bind("<KeyRelease>", lambda event: self.format_discount_input(event, client_fields))
                entry.bind("<Return>", lambda event: self.update_cost_total(client_fields))
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
            elif field[1] == "descuento":
                currency_frame = ttk.Frame(row)
                currency_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

                symbol_label = ttk.Label(currency_frame, text="$", width=3, anchor="n")
                symbol_label.pack(side=tk.LEFT)

                entry = ttk.Entry(currency_frame, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                def toggle_discount_mode():
                    if client_fields["discount_is_percentage"].get():
                        symbol_label.config(text="%")
                    else:
                        symbol_label.config(text="$")
                    client_fields["descuento"].set("")
                    self.update_cost_total(client_fields)

                ttk.Checkbutton(
                    row,
                    text="Porcentaje",
                    variable=client_fields["discount_is_percentage"],
                    command=toggle_discount_mode
                ).pack(side=tk.LEFT, padx=5)

                entry.bind("<KeyRelease>", lambda event: self.format_discount_input(event, client_fields))
                entry.bind("<Return>", lambda event: self.update_cost_total(client_fields))
            elif field[1] == "adelanto":
                # Contenedor para el símbolo $ y el campo de entrada
                currency_frame = ttk.Frame(row)
                currency_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Etiqueta del símbolo $
                ttk.Label(currency_frame, text="$", width=3, anchor="n").pack(side=tk.LEFT)
                
                # Campo de entrada
                entry = ttk.Entry(currency_frame, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Binding actualizado para incluir formato
                entry.bind("<KeyRelease>", lambda event: self.format_down_payment_input(event, client_fields))
            elif field[1] == "pago_pendiente":
                # Este campo es de solo lectura, pero necesita un widget para mostrar el valor
                entry = ttk.Label(row, textvariable=client_fields[field[1]], foreground="blue", font=('Arial', 10, 'bold'))
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field[1] == "noches":
                entry = ttk.Entry(row, textvariable=client_fields[field[1]])
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field[1] == "costo_total":
                # Contenedor para el símbolo $ y el campo de entrada (solo lectura)
                currency_frame = ttk.Frame(row)
                currency_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Etiqueta del símbolo $
                ttk.Label(currency_frame, text="$", width=3, anchor="n").pack(side=tk.LEFT)
                
                # Campo de entrada (solo lectura)
                entry = ttk.Entry(currency_frame, textvariable=client_fields[field[1]], state='readonly')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif field[1] == "costo_con_descuento":
                # Contenedor para el símbolo $ y el campo de entrada (solo lectura)
                currency_frame = ttk.Frame(row)
                currency_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Etiqueta del símbolo $
                ttk.Label(currency_frame, text="$", width=3, anchor="n").pack(side=tk.LEFT)
                
                # Campo de entrada (solo lectura)
                entry = ttk.Entry(currency_frame, textvariable=client_fields[field[1]], state='readonly')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif field[1] == "display_adelanto":
                # Nuevo resumen visual para el adelanto
                ttk.Label(row, text="Adelanto:", width=15, anchor="e").pack(side=tk.LEFT, padx=(20, 5))
                ttk.Label(row, textvariable=client_fields["display_adelanto"], foreground="green", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            elif field[1] == "display_descuento":
                # Nuevo resumen visual para el descuento
                ttk.Label(row, text="Descuento:", width=15, anchor="e").pack(side=tk.LEFT, padx=(20, 5))
                ttk.Label(row, textvariable=client_fields["display_descuento"], foreground="red", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
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
        def update_date_field(selected_date):
            client_fields[field_name].set(selected_date)
            self.update_cost_total(client_fields)

        id_inmueble = None
        nombre = client_fields["inmueble"].get()
        if nombre and hasattr(self, "property_map") and nombre in self.property_map:
            id_inmueble = self.property_map[nombre][0]

        ranges = self.db.get_reserved_ranges(id_inmueble=id_inmueble)
        CalendarDialog(parent, update_date_field, reserved_ranges=ranges)

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

        # Recalcular costos después de autocompletar
        self.update_cost_total(client_fields)

    def update_cost_total(self, client_fields):
        # Obtener valores del formulario
        fecha_ingreso_str = client_fields["fecha_ingreso"].get()
        fecha_egreso_str = client_fields["fecha_egreso"].get()
        valor_dia_str = client_fields["valor_dia"].get()
        descuento_str = client_fields["descuento"].get()
        adelanto_str = client_fields["adelanto"].get()
        
        if not (fecha_ingreso_str and fecha_egreso_str and valor_dia_str):
            # Limpiar campos de costo si faltan datos básicos
            client_fields["noches"].set("")
            client_fields["costo_total"].set("0.00")
            client_fields["costo_con_descuento"].set("0.00")
            client_fields["pago_pendiente"].set("0.00")
            # Actualizar resúmenes visuales
            client_fields["display_adelanto"].set("0.00")
            client_fields["display_descuento"].set("0.00")
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
            
            # Calcular costo con descuento si el campo no está vacío
            if descuento_str:
                descuento_val = float(descuento_str.replace('$', '').replace(',', ''))
                if client_fields["discount_is_percentage"].get():
                    descuento = costo_total * (descuento_val / 100.0)
                else:
                    descuento = descuento_val
                costo_con_descuento = costo_total - descuento
            else:
                descuento = 0
                costo_con_descuento = costo_total
            
            # Calcular pago pendiente
            adelanto = 0.0
            if adelanto_str:
                adelanto = float(adelanto_str.replace('$', '').replace(',', ''))
            
            pago_pendiente = costo_con_descuento - adelanto
            
            # Actualizar campo de costo total
            client_fields["costo_total"].set(f"{costo_total:,.2f}")
            
            # Actualizar campo de cantidad de noches
            client_fields["noches"].set(str(noches))
            
            # Actualizar campo de costo con descuento
            client_fields["costo_con_descuento"].set(f"{costo_con_descuento:,.2f}")
            
            # Actualizar campo de pago pendiente
            client_fields["pago_pendiente"].set(f"{pago_pendiente:,.2f}")
            
            # *** ACTUALIZACIÓN DE RESUMEN VISUAL ***
            client_fields["display_adelanto"].set(f"{adelanto:,.2f}")
            client_fields["display_descuento"].set(f"{descuento:,.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha o moneda inválido: {str(e)}", parent=self.master)
            # Limpiar campos de costo en caso de error
            client_fields["costo_total"].set("0.00")
            client_fields["noches"].set("")
            client_fields["costo_con_descuento"].set("0.00")
            client_fields["pago_pendiente"].set("0.00")
            # Limpiar resúmenes visuales en caso de error
            client_fields["display_adelanto"].set("0.00")
            client_fields["display_descuento"].set("0.00")


    def save_reservation(self, reservation_window, client_fields):
        # Obtener valores del formulario
        fecha_ingreso_str = client_fields["fecha_ingreso"].get()
        fecha_egreso_str = client_fields["fecha_egreso"].get()
        valor_dia_str = client_fields["valor_dia"].get()
        descuento_str = client_fields["descuento"].get()
        adelanto_str = client_fields["adelanto"].get()
        pago_pendiente_str = client_fields["pago_pendiente"].get()
        noches_str = client_fields["noches"].get()
        costo_total_str = client_fields["costo_total"].get()
        costo_con_descuento_str = client_fields["costo_con_descuento"].get()
        
        # Validar campos obligatorios
        if not (fecha_ingreso_str and fecha_egreso_str and valor_dia_str and noches_str):
            messagebox.showerror("Error", "Por favor complete todos los campos obligatorios (Fechas, Valor por Día)", parent=reservation_window)
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
            
            # Calcular costo con descuento si el campo no está vacío
            if descuento_str:
                descuento_val = float(descuento_str.replace('$', '').replace(',', ''))
                if client_fields["discount_is_percentage"].get():
                    descuento = costo_total * (descuento_val / 100.0)
                else:
                    descuento = descuento_val
                costo_con_descuento = costo_total - descuento
            else:
                descuento = 0
                costo_con_descuento = costo_total
            
            # Calcular pago pendiente
            adelanto = 0.0
            if adelanto_str:
                adelanto = float(adelanto_str.replace('$', '').replace(',', ''))
            
            pago_pendiente = costo_con_descuento - adelanto
            
            # Guardar la reserva en la base de datos
            id_cliente = client_fields["id_clientes"].get()
            inmueble_nombre = client_fields["inmueble"].get()
            id_inmueble = self.property_map.get(inmueble_nombre, [None])[0]

            if not id_cliente or not id_inmueble:
                messagebox.showerror("Error", "Debe seleccionar un cliente y un inmueble", parent=reservation_window)
                return

            reservation_data = {
                "id_cliente": int(id_cliente),
                "id_inmueble": id_inmueble,
                "fecha_ingreso": fecha_ingreso,
                "fecha_egreso": fecha_egreso,
                "valor_dia": valor_dia,
                "noches": noches,
                "costo_total": costo_total,
                "costo_con_descuento": costo_con_descuento,
                "adelanto": adelanto,
                "pago_pendiente": pago_pendiente,
                "provincia": client_fields["provincia"].get()
            }
            
            self.db.insert_reservation(reservation_data)

            client_email = client_fields["email"].get()
            client_name = f"{client_fields['nombre'].get()} {client_fields['apellido'].get()}"
            email_data = {
                "inmueble": inmueble_nombre,
                "fecha_ingreso": fecha_ingreso.strftime("%d/%m/%Y"),
                "fecha_egreso": fecha_egreso.strftime("%d/%m/%Y"),
                "noches": noches,
                "valor_dia": valor_dia,
                "costo_total": costo_total,
                "costo_con_descuento": costo_con_descuento,
                "adelanto": adelanto,
                "pago_pendiente": pago_pendiente,
            }
            send_reservation_email(client_email, client_name, email_data)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Reserva guardada correctamente", parent=reservation_window)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha o moneda inválido: {str(e)}", parent=reservation_window)
