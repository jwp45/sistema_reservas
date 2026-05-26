import os
from controllers.database import Database
from utils.email_sender import send_reservation_email
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from PIL import Image, ImageTk

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
    
    def _format_currency(self, value):
        """Formatea un valor numérico como moneda ($1.234,56)."""
        try:
            if isinstance(value, str):
                # Limpiar la cadena antes de convertir
                value = value.replace('$', '').replace('.', '').replace(',', '.')
                value = float(value)
            
            # Formatear con estándar US primero para obtener comas y puntos
            formatted = f"{value:,.2f}"
            # Intercambiar comas y puntos para formato ES/AR
            # 1,234.56 -> 1.234,56
            # Primero cambiamos el punto decimal por un marcador temporal
            main_part, decimal_part = formatted.split('.')
            main_part = main_part.replace(',', '.')
            return f"${main_part},{decimal_part}"
        except (ValueError, TypeError):
            return "$0,00"

    def _parse_currency(self, value_str):
        """Convierte una cadena de moneda ($1.234,56) a float."""
        if not value_str:
            return 0.0
        try:
            # Eliminar $, luego eliminar puntos de miles, luego cambiar coma decimal por punto
            clean = value_str.replace('$', '').replace('.', '').replace(',', '.')
            return float(clean)
        except ValueError:
            return 0.0

    def format_discount_input(self, event, client_fields):
        text = client_fields["descuento"].get()
        if client_fields["discount_is_percentage"].get():
            cleaned_text = ''.join(filter(lambda char: char.isdigit() or char == '.', text))
            client_fields["descuento"].set(cleaned_text)
        else:
            cleaned_text = ''.join(filter(lambda char: char.isdigit(), text))
            if cleaned_text:
                val = float(cleaned_text)
                formatted = f"{val:,.0f}".replace(',', '.')
                client_fields["descuento"].set(f"${formatted}")
            else:
                client_fields["descuento"].set("")

        self.update_cost_total(client_fields)

    def format_down_payment_input(self, event, client_fields):
        """Formatea el campo de adelanto con símbolo $ y puntos de miles."""
        text = client_fields["adelanto"].get()
        cleaned_text = ''.join(filter(lambda char: char.isdigit(), text))
        
        if cleaned_text:
            val = float(cleaned_text)
            formatted = f"{val:,.0f}".replace(',', '.')
            client_fields["adelanto"].set(f"${formatted}")
        else:
            client_fields["adelanto"].set("")
        
        self.update_cost_total(client_fields)


    def create_reservation(self):
        print("Crear Reserva")

        reservation_window = tk.Toplevel(self.master)
        reservation_window.title("Nueva Reserva")
        reservation_window.geometry("850x850")
        reservation_window.configure(bg="#f8f9fa")

        # Configurar estilos locales
        style = ttk.Style(reservation_window)
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")
        style.configure("Section.TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_scroll_container = ttk.Frame(reservation_window)
        main_scroll_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_scroll_container, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Centrar el contenido
        form_frame = ttk.Frame(scrollable_frame, padding="20 10 20 20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Formulario de Nueva Reserva", style="Header.TLabel").pack(pady=(0, 20))

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
            "discount_is_percentage": tk.BooleanVar(),
            "display_adelanto": tk.StringVar(),
            "display_descuento": tk.StringVar()
        }

        client_fields["fecha_registro"].set(date.today().strftime("%d/%m/%Y"))
        client_fields["provincia"].set("Buenos Aires")

        # Autocompletar con el próximo ID disponible
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
        next_id = self.db.get_next_available_client_id()
        client_fields["id_clientes"].set(str(next_id))

        provincias = [
            "Buenos Aires", "Catamarca", "Chaco", "Chubut", "CABA",
            "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
            "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén",
            "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz",
            "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"
        ]

        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
        properties = self.db.get_all_properties()
        self.property_map = {p[1]: p for p in properties}
        property_names = list(self.property_map.keys())

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

        # ─── SECCIÓN 1: DATOS DEL CLIENTE ────────────────────────────
        sec1 = ttk.LabelFrame(form_frame, text=" Información del Cliente ", padding=15, style="Section.TLabelframe")
        sec1.pack(fill=tk.X, pady=10)
        sec1.columnconfigure(1, weight=1)
        sec1.columnconfigure(3, weight=1)

        # Fila 0
        ttk.Label(sec1, text="ID Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        entry_id = ttk.Entry(sec1, textvariable=client_fields["id_clientes"])
        entry_id.grid(row=0, column=1, sticky=tk.EW, pady=5)
        entry_id.bind("<Return>", lambda event: self.autofill_client_data(client_fields))
        ttk.Button(sec1, text="Buscar", width=10, command=lambda: self.autofill_client_data(client_fields)).grid(row=0, column=2, sticky=tk.W, padx=5)

        ttk.Label(sec1, text="Fecha Registro:").grid(row=0, column=3, sticky=tk.E, pady=5, padx=10)
        ttk.Entry(sec1, textvariable=client_fields["fecha_registro"], state="readonly", width=15).grid(row=0, column=4, sticky=tk.E, pady=5)

        # Fila 1
        ttk.Label(sec1, text="Nombre:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Entry(sec1, textvariable=client_fields["nombre"]).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(sec1, text="Apellido:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=10)
        ttk.Entry(sec1, textvariable=client_fields["apellido"]).grid(row=1, column=3, columnspan=2, sticky=tk.EW, pady=5)

        # Fila 2
        ttk.Label(sec1, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Entry(sec1, textvariable=client_fields["email"]).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(sec1, text="Teléfono:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=10)
        ttk.Entry(sec1, textvariable=client_fields["telefono"]).grid(row=2, column=3, columnspan=2, sticky=tk.EW, pady=5)

        # Fila 3
        ttk.Label(sec1, text="Provincia:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        var_prov = client_fields["provincia"]
        combo_prov = ttk.Combobox(sec1, textvariable=var_prov, values=provincias)
        combo_prov.grid(row=3, column=1, sticky=tk.EW, pady=5)
        combo_prov.bind("<KeyRelease>", filtrar_provincias(combo_prov, var_prov))

        # ─── SECCIÓN 2: DATOS DE LA RESERVA ──────────────────────────
        sec2 = ttk.LabelFrame(form_frame, text=" Detalles de la Reserva ", padding=15, style="Section.TLabelframe")
        sec2.pack(fill=tk.X, pady=10)
        sec2.columnconfigure(1, weight=1)

        # Izquierda: Campos, Derecha: Foto
        left_grid = ttk.Frame(sec2)
        left_grid.grid(row=0, column=0, sticky=tk.NSEW)
        left_grid.columnconfigure(1, weight=1)

        ttk.Label(left_grid, text="Inmueble:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        combo_inmueble = ttk.Combobox(left_grid, textvariable=client_fields["inmueble"], values=property_names, state="readonly")
        combo_inmueble.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(left_grid, text="Cant. Personas:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Entry(left_grid, textvariable=client_fields["cantidad_personas"]).grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(left_grid, text="Valor por Día:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        val_frame = ttk.Frame(left_grid)
        val_frame.grid(row=2, column=1, sticky=tk.EW, pady=5)
        entry_val = ttk.Entry(val_frame, textvariable=client_fields["valor_dia"])
        entry_val.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_val.bind("<KeyRelease>", lambda e: self.format_discount_input(e, client_fields))
        entry_val.bind("<Return>", lambda e: self.update_cost_total(client_fields))

        ttk.Label(left_grid, text="Fecha Ingreso:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        fi_frame = ttk.Frame(left_grid)
        fi_frame.grid(row=3, column=1, sticky=tk.EW, pady=5)
        ttk.Entry(fi_frame, textvariable=client_fields["fecha_ingreso"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(fi_frame, text="📅", width=3, command=lambda: self.select_date("fecha_ingreso", client_fields, reservation_window)).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(left_grid, text="Fecha Egreso:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        fe_frame = ttk.Frame(left_grid)
        fe_frame.grid(row=4, column=1, sticky=tk.EW, pady=5)
        ttk.Entry(fe_frame, textvariable=client_fields["fecha_egreso"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(fe_frame, text="📅", width=3, command=lambda: self.select_date("fecha_egreso", client_fields, reservation_window)).pack(side=tk.RIGHT, padx=(5, 0))

        # Foto Frame
        right_grid = ttk.Frame(sec2, padding=(20, 0, 0, 0))
        right_grid.grid(row=0, column=1, sticky=tk.NE)
        
        img_lf = ttk.LabelFrame(right_grid, text=" Vista Previa ", padding=5)
        img_lf.pack()
        
        self.img_container = tk.Frame(img_lf, width=200, height=150, bg="#ecf0f1", bd=1, relief=tk.RIDGE)
        self.img_container.pack_propagate(False)
        self.img_container.pack()
        
        self.inmueble_preview = tk.Label(self.img_container, text="Seleccione un inmueble", fg="#7f8c8d",
                                         font=('Arial', 9, 'italic'), bg="#ecf0f1")
        self.inmueble_preview.pack(fill=tk.BOTH, expand=True)

        def on_inmueble_select(event):
            selected = client_fields["inmueble"].get()
            if selected in self.property_map:
                pd = self.property_map[selected]
                client_fields["valor_dia"].set(self._format_currency(pd[7]))
                client_fields["cantidad_personas"].set(str(pd[2]))
                self.update_cost_total(client_fields)
                img_path = pd[8]
                if img_path and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        # Mantener relación de aspecto si es posible, o simplemente redimensionar
                        img.thumbnail((198, 148), Image.LANCZOS)
                        tk_img = ImageTk.PhotoImage(img)
                        self.inmueble_preview.config(image=tk_img, text="")
                        self.inmueble_preview.image = tk_img
                    except Exception:
                        self.inmueble_preview.config(image="", text="Error al cargar imagen")
                else:
                    self.inmueble_preview.config(image="", text="Sin imagen disponible")
        combo_inmueble.bind("<<ComboboxSelected>>", on_inmueble_select)

        # ─── SECCIÓN 3: COSTOS Y PAGOS ───────────────────────────────
        sec3 = ttk.LabelFrame(form_frame, text=" Resumen de Costos ", padding=15, style="Section.TLabelframe")
        sec3.pack(fill=tk.X, pady=10)
        sec3.columnconfigure(1, weight=1)
        sec3.columnconfigure(3, weight=1)

        # Fila 0: Adelanto y Descuento
        ttk.Label(sec3, text="Adelanto:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ade_f = ttk.Frame(sec3)
        ade_f.grid(row=0, column=1, sticky=tk.EW, pady=5)
        entry_ade = ttk.Entry(ade_f, textvariable=client_fields["adelanto"])
        entry_ade.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry_ade.bind("<KeyRelease>", lambda e: self.format_down_payment_input(e, client_fields))

        ttk.Label(sec3, text="Descuento:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        des_f = ttk.Frame(sec3)
        des_f.grid(row=0, column=3, sticky=tk.EW, pady=5)
        symbol_label = ttk.Label(des_f, text="$", width=2)
        entry_des = ttk.Entry(des_f, textvariable=client_fields["descuento"])
        entry_des.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        chk_perc = ttk.Checkbutton(sec3, text="Es %", variable=client_fields["discount_is_percentage"],
                                   command=lambda: self._toggle_discount_symbol(symbol_label, client_fields))
        chk_perc.grid(row=0, column=4, sticky=tk.W, padx=5)
        entry_des.bind("<KeyRelease>", lambda e: self.format_discount_input(e, client_fields))

        # Fila 1: Noches y Costo Total
        ttk.Label(sec3, text="Noches:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        ttk.Entry(sec3, textvariable=client_fields["noches"], width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(sec3, text="Costo Base:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=10)
        base_f = ttk.Frame(sec3)
        base_f.grid(row=1, column=3, columnspan=2, sticky=tk.EW, pady=5)
        ttk.Entry(base_f, textvariable=client_fields["costo_total"], state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Fila 2: Costo Final y Pago Pendiente
        ttk.Label(sec3, text="Costo Final:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        final_f = ttk.Frame(sec3)
        final_f.grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Entry(final_f, textvariable=client_fields["costo_con_descuento"], state="readonly", 
                  font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(sec3, text="Pago Pendiente:", font=("Segoe UI", 10, "bold")).grid(row=2, column=2, sticky=tk.W, pady=5, padx=10)
        pend_f = ttk.Frame(sec3)
        pend_f.grid(row=2, column=3, columnspan=2, sticky=tk.EW, pady=5)
        ttk.Label(pend_f, textvariable=client_fields["pago_pendiente"], foreground="#e74c3c", 
                  font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── BOTONES DE ACCIÓN ───────────────────────────────────────
        btn_frame = ttk.Frame(form_frame, padding=(0, 20, 0, 0))
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="CANCELAR", width=20, command=reservation_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="CONFIRMAR RESERVA", style="Action.TButton", width=30,
                   command=lambda: self.save_reservation(reservation_window, client_fields)).pack(side=tk.RIGHT, padx=5)

    def _toggle_discount_symbol(self, label, fields):
        if fields["discount_is_percentage"].get():
            label.config(text="%")
        else:
            label.config(text="$")
        fields["descuento"].set("")
        self.update_cost_total(fields)

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
            client_fields["costo_total"].set("$0,00")
            client_fields["costo_con_descuento"].set("$0,00")
            client_fields["pago_pendiente"].set("$0,00")
            # Actualizar resúmenes visuales
            client_fields["display_adelanto"].set("$0,00")
            client_fields["display_descuento"].set("$0,00")
            return

        try:
            # Convertir fechas a objetos date
            fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%d/%m/%Y").date()
            fecha_egreso = datetime.strptime(fecha_egreso_str, "%d/%m/%Y").date()
            
            # Calcular número de noches
            delta = fecha_egreso - fecha_ingreso
            noches = delta.days
            
            # Convertir valor por día a número usando el nuevo parser
            valor_dia = self._parse_currency(valor_dia_str)
            
            # Calcular costo total
            costo_total = noches * valor_dia
            
            # Calcular costo con descuento si el campo no está vacío
            if descuento_str:
                if client_fields["discount_is_percentage"].get():
                    # Para el porcentaje, seguimos permitiendo el punto decimal
                    descuento_val = float(descuento_str.replace('%', '').strip())
                    descuento = costo_total * (descuento_val / 100.0)
                else:
                    descuento = self._parse_currency(descuento_str)
                costo_con_descuento = costo_total - descuento
            else:
                descuento = 0
                costo_con_descuento = costo_total
            
            # Calcular pago pendiente
            adelanto = self._parse_currency(adelanto_str)
            pago_pendiente = costo_con_descuento - adelanto
            
            # Actualizar campos con el nuevo formato
            client_fields["noches"].set(str(noches))
            client_fields["costo_total"].set(self._format_currency(costo_total))
            client_fields["costo_con_descuento"].set(self._format_currency(costo_con_descuento))
            client_fields["pago_pendiente"].set(self._format_currency(pago_pendiente))
            
            # *** ACTUALIZACIÓN DE RESUMEN VISUAL ***
            client_fields["display_adelanto"].set(self._format_currency(adelanto))
            client_fields["display_descuento"].set(self._format_currency(descuento))
            
        except Exception as e:
            # En caso de error, no mostrar mensaje molesto mientras se escribe, solo log
            print(f"Error en update_cost_total: {e}")
            client_fields["costo_total"].set("$0,00")
            client_fields["noches"].set("")
            client_fields["costo_con_descuento"].set("$0,00")
            client_fields["pago_pendiente"].set("$0,00")


    def save_reservation(self, reservation_window, client_fields):
        # Obtener valores del formulario
        fecha_ingreso_str = client_fields["fecha_ingreso"].get()
        fecha_egreso_str = client_fields["fecha_egreso"].get()
        valor_dia_str = client_fields["valor_dia"].get()
        descuento_str = client_fields["descuento"].get()
        adelanto_str = client_fields["adelanto"].get()
        noches_str = client_fields["noches"].get()
        
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
            
            # Usar los parsers para obtener los valores reales
            valor_dia = self._parse_currency(valor_dia_str)
            costo_total = noches * valor_dia
            
            if descuento_str:
                if client_fields["discount_is_percentage"].get():
                    descuento_val = float(descuento_str.replace('%', '').strip())
                    descuento = costo_total * (descuento_val / 100.0)
                else:
                    descuento = self._parse_currency(descuento_str)
                costo_con_descuento = costo_total - descuento
            else:
                descuento = 0
                costo_con_descuento = costo_total
            
            adelanto = self._parse_currency(adelanto_str)
            pago_pendiente = costo_con_descuento - adelanto
            
            # Verificar si el cliente existe, si no, crearlo
            id_cliente = client_fields["id_clientes"].get()
            if not id_cliente:
                messagebox.showerror("Error", "Debe ingresar un ID de cliente", parent=reservation_window)
                return
            
            existing_client = self.db.get_client_by_id(id_cliente)
            if not existing_client:
                # Validar datos mínimos para nuevo cliente
                nombre = client_fields["nombre"].get()
                apellido = client_fields["apellido"].get()
                if not (nombre and apellido):
                    messagebox.showerror("Error", "Para crear un nuevo cliente debe ingresar al menos Nombre y Apellido", parent=reservation_window)
                    return
                
                new_client_data = (
                    int(id_cliente),
                    nombre,
                    apellido,
                    client_fields["email"].get(),
                    client_fields["telefono"].get()
                )
                if self.db.insert_client(new_client_data):
                    messagebox.showinfo("Nuevo Cliente", f"Se ha creado automáticamente el nuevo cliente: {nombre} {apellido} (ID: {id_cliente})", parent=reservation_window)
                else:
                    messagebox.showerror("Error", "No se pudo crear el nuevo cliente", parent=reservation_window)
                    return

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
            reservation_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar reserva: {str(e)}", parent=reservation_window)
