import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import date, datetime, timedelta
from controllers.database import Database

class ConsultationWindow:
    def __init__(self, master, reservation_controller):
        self.master = master
        self.controller = reservation_controller
        self.db = Database()
        self.db.connect()
        
        self.window = tk.Toplevel(master)
        self.window.title("Consulta de Disponibilidad Interactiva")
        self.window.geometry("1200x900")
        self.window.configure(bg="#f0f2f5")
        self.window.transient(master)
        self.window.grab_set()

        self.selected_property = None
        self.reserved_ranges = []
        self.start_date = None
        self.end_date = None
        
        self.now = date.today()
        self.year = self.now.year
        self.month = self.now.month
        
        # Campos para captación de leads
        self.lead_fields = {
            "nombre": tk.StringVar(),
            "telefono": tk.StringVar(),
            "email": tk.StringVar()
        }
        
        self.setup_ui()
        self.load_properties()

    def send_quotation(self):
        """Registra al cliente (si no existe) y envía el presupuesto por mail."""
        nombre = self.lead_fields["nombre"].get()
        email = self.lead_fields["email"].get()
        tel = self.lead_fields["telefono"].get()
        
        if not (nombre and email and tel):
            messagebox.showerror("Error", "Por favor completa Nombre, Email y Teléfono para enviar la cotización.", parent=self.window)
            return
            
        if not self.start_date or not self.end_date or not self.selected_property:
            messagebox.showwarning("Atención", "Selecciona fechas e inmueble antes de enviar una cotización.", parent=self.window)
            return

        # 1. Registrar cliente si no existe
        db = Database()
        db.connect()
        # Intentamos buscar si ya existe (por email o teléfono)
        all_clients = db.get_all_clients()
        client_id = None
        for c in all_clients:
            if c[4] == email or c[5] == tel:
                client_id = c[0]
                break
        
        if not client_id:
            # Crear nuevo cliente básico
            next_id = db.get_next_available_client_id()
            # client_data = (id, documento, nombre, apellido, email, telefono)
            # Usamos el nombre completo en 'nombre' y dejamos apellido vacío o lo spliteamos
            parts = nombre.split(" ", 1)
            nom = parts[0]
            ape = parts[1] if len(parts) > 1 else "—"
            db.insert_client((next_id, "S/D", nom, ape, email, tel))
            client_id = next_id

        # 2. Enviar Correo
        from utils.email_sender import send_quotation_email
        
        data = {
            "inmueble": self.selected_property[1],
            "fecha_ingreso": self.start_date.strftime("%d/%m/%Y"),
            "fecha_egreso": self.end_date.strftime("%d/%m/%Y"),
            "noches": (self.end_date - self.start_date).days,
            "ubicacion": f"{self.selected_property[4]}, {self.selected_property[5]}",
            "costo_total": self.lbl_costo_total.cget("text").replace("Costo Total: ", ""),
            "final_price": self.lbl_final_price.cget("text").replace("Precio Final: ", ""),
            "final_per_night": self.lbl_final_per_night.cget("text").replace("P/Noche Final: ", "")
        }
        
        if send_quotation_email(email, nombre, data):
            messagebox.showinfo("Éxito", f"Cotización enviada correctamente a {email}.\nCliente registrado en el directorio.", parent=self.window)
            # Limpiar campos de lead
            for var in self.lead_fields.values(): var.set("")
        else:
            messagebox.showerror("Error", "No se pudo enviar el correo. Verifica la configuración SMTP.", parent=self.window)

    def setup_ui(self):
        # --- ESTILOS ---
        style = ttk.Style(self.window)
        style.configure("Cons.TFrame", background="#f0f2f5")
        style.configure("ConsCard.TFrame", background="white", relief="flat")
        style.configure("ConsHeader.TLabel", font=("Segoe UI", 18, "bold"), foreground="white", background="#2c3e50")
        style.configure("Day.TButton", font=("Segoe UI", 10), width=4)
        style.configure("Selected.TButton", background="#3498db", foreground="white")
        style.configure("Reserved.TButton", background="#e74c3c", foreground="white")

        # --- ENCABEZADO ---
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔍 CONSULTA DE DISPONIBILIDAD", font=("Segoe UI", 16, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=30, pady=20)

        # --- CONTENIDO PRINCIPAL ---
        main_frame = ttk.Frame(self.window, padding=20, style="Cons.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel Izquierdo: Selección y Resumen
        left_panel = ttk.Frame(main_frame, width=350, style="Cons.TFrame")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Selección de Rango
        self.range_card = tk.LabelFrame(left_panel, text=" 📅 ESTADÍA SELECCIONADA ", font=("Segoe UI", 9, "bold"), 
                                      bg="white", padx=15, pady=15, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        self.range_card.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_desde = tk.Label(self.range_card, text="Desde: No seleccionada", bg="white", font=("Segoe UI", 9), anchor="w")
        self.lbl_desde.pack(fill=tk.X, pady=2)
        self.lbl_hasta = tk.Label(self.range_card, text="Hasta: No seleccionada", bg="white", font=("Segoe UI", 9), anchor="w")
        self.lbl_hasta.pack(fill=tk.X, pady=2)
        self.lbl_noches = tk.Label(self.range_card, text="Noches: 0", bg="white", font=("Segoe UI", 10, "bold"), fg="#2980b9", anchor="w")
        self.lbl_noches.pack(fill=tk.X, pady=2)
        
        self.lbl_costo_total = tk.Label(self.range_card, text="Costo Total: $0,00", bg="white", font=("Segoe UI", 12, "bold"), fg="#27ae60", anchor="w")
        self.lbl_costo_total.pack(fill=tk.X, pady=(5, 10))

        # --- SECCIÓN DE NEGOCIACIÓN (En el panel izquierdo, debajo de estadía) ---
        self.discount_card = tk.LabelFrame(left_panel, text=" 💰 NEGOCIACIÓN / DESCUENTO ", font=("Segoe UI", 9, "bold"), 
                                         bg="white", padx=15, pady=15, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        self.discount_card.pack(fill=tk.X, pady=(0, 20))

        self.discount_is_percentage = tk.BooleanVar(value=True)
        disc_type_frame = tk.Frame(self.discount_card, bg="white")
        disc_type_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(disc_type_frame, text="%", variable=self.discount_is_percentage, value=True, 
                       bg="white", command=self.update_selection_display).pack(side=tk.LEFT)
        tk.Radiobutton(disc_type_frame, text="$", variable=self.discount_is_percentage, value=False, 
                       bg="white", command=self.update_selection_display).pack(side=tk.LEFT, padx=10)

        self.discount_var = tk.StringVar(value="0")
        self.ent_discount = ttk.Entry(self.discount_card, textvariable=self.discount_var, font=("Segoe UI", 10))
        self.ent_discount.pack(fill=tk.X, pady=5)
        self.ent_discount.bind("<KeyRelease>", self.on_discount_change)

        self.lbl_final_price = tk.Label(self.discount_card, text="Precio Final: $0,00", bg="white", 
                                        font=("Segoe UI", 12, "bold"), fg="#e67e22", anchor="w")
        self.lbl_final_price.pack(fill=tk.X, pady=(5, 0))

        self.lbl_final_per_night = tk.Label(self.discount_card, text="P/Noche Final: $0,00", bg="white", 
                                            font=("Segoe UI", 9, "italic"), fg="#7f8c8d", anchor="w")
        self.lbl_final_per_night.pack(fill=tk.X, pady=2)

        # --- SECCIÓN DE CAPTACIÓN DE CLIENTE ---
        self.lead_card = tk.LabelFrame(left_panel, text=" 📋 COTIZACIÓN / CAPTACIÓN ", font=("Segoe UI", 9, "bold"), 
                                      bg="white", padx=15, pady=15, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        self.lead_card.pack(fill=tk.X, pady=(0, 20))

        tk.Label(self.lead_card, text="NOMBRE COMPLETO:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        ttk.Entry(self.lead_card, textvariable=self.lead_fields["nombre"], font=("Segoe UI", 9)).pack(fill=tk.X, pady=(2, 8))

        tk.Label(self.lead_card, text="TELÉFONO:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        ttk.Entry(self.lead_card, textvariable=self.lead_fields["telefono"], font=("Segoe UI", 9)).pack(fill=tk.X, pady=(2, 8))

        tk.Label(self.lead_card, text="EMAIL:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        ttk.Entry(self.lead_card, textvariable=self.lead_fields["email"], font=("Segoe UI", 9)).pack(fill=tk.X, pady=(2, 8))

        ttk.Button(self.lead_card, text="📧 ENVIAR COTIZACIÓN", command=self.send_quotation).pack(fill=tk.X, pady=(5, 0))

        self.btn_reservar = ttk.Button(left_panel, text="🚀 RESERVAR AHORA", state=tk.DISABLED, command=self.go_to_reservation)
        self.btn_reservar.pack(fill=tk.X, pady=10)
        
        ttk.Button(left_panel, text="LIMPIAR SELECCIÓN", command=self.reset_selection).pack(fill=tk.X)

        # Panel Derecho: Calendario
        right_panel = tk.Frame(main_frame, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- SECCIÓN DE BÚSQUEDA Y FILTROS (Horizontal con Plegado) ---
        sel_card = tk.Frame(right_panel, bg="white", padx=20, pady=10, highlightbackground="#e0e0e0", highlightthickness=1)
        sel_card.pack(fill=tk.X)

        # Botón para mostrar/ocultar ubicación
        self.geo_visible = False
        self.btn_toggle_geo = ttk.Button(sel_card, text="📍 UBICACIÓN ▼", width=14, command=self.toggle_geo_filters)
        self.btn_toggle_geo.pack(side=tk.LEFT, padx=(0, 15))

        # Frame para filtros de ubicación (Prov/Loc) - Se packea dinámicamente
        self.geo_frame = tk.Frame(sel_card, bg="white")
        
        # Filtro: Provincia (dentro de geo_frame)
        tk.Label(self.geo_frame, text="Prov:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(side=tk.LEFT)
        self.prov_var = tk.StringVar(value="Todas")
        self.combo_prov = ttk.Combobox(self.geo_frame, textvariable=self.prov_var, state="readonly", font=("Segoe UI", 9), width=12)
        self.combo_prov.pack(side=tk.LEFT, padx=5)
        self.combo_prov.bind("<<ComboboxSelected>>", self.apply_filters)

        # Filtro: Localidad (dentro de geo_frame)
        tk.Label(self.geo_frame, text="Loc:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(side=tk.LEFT, padx=(5, 0))
        self.loc_var = tk.StringVar(value="Todas")
        self.combo_loc = ttk.Combobox(self.geo_frame, textvariable=self.loc_var, state="readonly", font=("Segoe UI", 9), width=15)
        self.combo_loc.pack(side=tk.LEFT, padx=5)
        self.combo_loc.bind("<<ComboboxSelected>>", self.apply_filters)

        # Separador visual sutil si está abierto
        self.geo_sep = tk.Label(self.geo_frame, text="|", fg="#e0e0e0", bg="white", padx=10)
        self.geo_sep.pack(side=tk.LEFT)

        # Filtros Fijos (Tipo y Selección)
        fixed_f = tk.Frame(sel_card, bg="white")
        fixed_f.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Filtro: Tipo
        tk.Label(fixed_f, text="Tipo:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value="Todos")
        self.combo_tipo = ttk.Combobox(fixed_f, textvariable=self.tipo_var, state="readonly", font=("Segoe UI", 9), width=12)
        self.combo_tipo.pack(side=tk.LEFT, padx=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.apply_filters)

        # Selector Final de Inmueble
        tk.Label(fixed_f, text="🏠 SELECCIONAR:", font=("Segoe UI", 8, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(15, 5))
        self.prop_var = tk.StringVar()
        self.combo_prop = ttk.Combobox(fixed_f, textvariable=self.prop_var, state="readonly", font=("Segoe UI", 9, "bold"), width=25)
        self.combo_prop.pack(side=tk.LEFT, padx=5)
        self.combo_prop.bind("<<ComboboxSelected>>", self.on_property_selected)

        # --- SECCIÓN DE DETALLES (Ahora arriba del calendario) ---
        self.info_card = tk.Frame(right_panel, bg="#f8f9fa", padx=20, pady=10, highlightbackground="#e0e0e0", highlightthickness=1)
        self.info_card.pack(fill=tk.X)

        tk.Label(self.info_card, text="🏠 DETALLES:", font=("Segoe UI", 9, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 10))
        
        self.lbl_capacidad = tk.Label(self.info_card, text="Capacidad: —", bg="#f8f9fa", font=("Segoe UI", 10))
        self.lbl_capacidad.pack(side=tk.LEFT, padx=15)
        self.lbl_precio = tk.Label(self.info_card, text="Precio/Noche: —", bg="#f8f9fa", font=("Segoe UI", 10, "bold"), fg="#27ae60")
        self.lbl_precio.pack(side=tk.LEFT, padx=15)

        # Contenedor para la marquesina de ubicación
        loc_container = tk.Frame(self.info_card, bg="#f8f9fa", width=300, height=25)
        loc_container.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        loc_container.pack_propagate(False)

        self.lbl_ubicacion = tk.Label(loc_container, text="Ubicación: —", bg="#f8f9fa", font=("Segoe UI", 9), fg="#7f8c8d", anchor="w")
        self.lbl_ubicacion.pack(fill=tk.BOTH, expand=True)

        # Variables para la marquesina
        self.marquee_text = ""
        self.marquee_running = False

        cal_header = tk.Frame(right_panel, bg="#f8f9fa", pady=15)
        cal_header.pack(fill=tk.X)
        
        ttk.Button(cal_header, text="<<", width=5, command=self.prev_month).pack(side=tk.LEFT, padx=20)
        self.lbl_month = tk.Label(cal_header, text="MES AÑO", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#2c3e50")
        self.lbl_month.pack(side=tk.LEFT, expand=True)
        ttk.Button(cal_header, text=">>", width=5, command=self.next_month).pack(side=tk.RIGHT, padx=20)
        
        days_header = tk.Frame(right_panel, bg="white")
        days_header.pack(fill=tk.X, padx=10)
        for d in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]:
            tk.Label(days_header, text=d, width=10, font=("Segoe UI", 9, "bold"), bg="white", fg="#95a5a6").pack(side=tk.LEFT, expand=True)
            
        self.days_frame = tk.Frame(right_panel, bg="white", padx=10, pady=10)
        self.days_frame.pack(fill=tk.BOTH, expand=True)
        
        # Leyenda
        legend_frame = tk.Frame(right_panel, bg="#f8f9fa", pady=10)
        legend_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self._create_legend(legend_frame, "#27ae60", "Disponible")
        self._create_legend(legend_frame, "#3498db", "Ingreso")
        self._create_legend(legend_frame, "#e74c3c", "Ocupado")
        self._create_legend(legend_frame, "#9b59b6", "Egreso")
        self._create_legend(legend_frame, "#f1c40f", "Transición")
        self._create_legend(legend_frame, "#2980b9", "Tu Selección")
        
        tk.Label(right_panel, text="* Click en fecha ocupada para ver quién reservó", 
                 font=("Segoe UI", 8, "italic"), bg="white", fg="#7f8c8d").pack(side=tk.BOTTOM, pady=(0, 5))

    def _scroll_address(self):
        """Mueve el texto de la ubicación como una marquesina."""
        if not self.marquee_running:
            return
            
        # Tomar el texto actual, rotarlo y actualizar el label
        current = self.marquee_text
        self.marquee_text = current[1:] + current[0]
        self.lbl_ubicacion.config(text=self.marquee_text)
        
        # Programar la siguiente actualización (cada 150ms)
        self.window.after(150, self._scroll_address)

    def _create_legend(self, parent, color, text):
        f = tk.Frame(parent, bg="#f8f9fa")
        f.pack(side=tk.LEFT, padx=20, expand=True)
        tk.Frame(f, bg=color, width=15, height=15).pack(side=tk.LEFT, padx=5)
        tk.Label(f, text=text, font=("Segoe UI", 9), bg="#f8f9fa").pack(side=tk.LEFT)

    def load_properties(self):
        """Carga inicial de todos los inmuebles y sus filtros."""
        self.all_properties = self.db.get_all_properties()
        
        # Obtener valores únicos para los filtros iniciales
        provincias = sorted(list(set(p[5] for p in self.all_properties)))
        tipos = sorted(list(set(p[6] for p in self.all_properties)))
        
        self.combo_prov['values'] = ["Todas"] + provincias
        self.combo_tipo['values'] = ["Todos"] + tipos
        
        # Cargar todas inicialmente en el selector de inmuebles
        self.apply_filters()

    def apply_filters(self, event=None):
        """Filtra la lista de inmuebles según los criterios seleccionados."""
        prov = self.prov_var.get()
        loc = self.loc_var.get()
        tipo = self.tipo_var.get()
        
        filtered = []
        localidades = set()
        
        for p in self.all_properties:
            # p = (id, nombre, cap, dir, loc, prov, tipo, val, img)
            p_loc = p[4]
            p_prov = p[5]
            p_tipo = p[6]
            
            match_prov = (prov == "Todas" or p_prov == prov)
            match_tipo = (tipo == "Todos" or p_tipo == tipo)
            
            # Recolectar localidades posibles según provincia seleccionada
            if match_prov:
                localidades.add(p_loc)
            
            # Aplicar filtro de localidad si no es "Todas"
            match_loc = (loc == "Todas" or p_loc == loc)
            
            if match_prov and match_loc and match_tipo:
                filtered.append(p)

        # Actualizar opciones de localidad dinámicamente
        current_locs = sorted(list(localidades))
        self.combo_loc['values'] = ["Todas"] + current_locs
        if loc not in self.combo_loc['values']:
            self.loc_var.set("Todas")

        # Actualizar selector de inmuebles
        self.property_map = {p[1]: p for p in filtered}
        self.combo_prop['values'] = sorted(list(self.property_map.keys()))
        
        # Limpiar selección actual si ya no está en la lista filtrada
        if self.prop_var.get() not in self.property_map:
            self.prop_var.set("")
            self.selected_property = None
            self.draw_calendar()

    def toggle_geo_filters(self):
        """Muestra u oculta los filtros de Provincia y Localidad."""
        if self.geo_visible:
            self.geo_frame.pack_forget()
            self.btn_toggle_geo.config(text="📍 UBICACIÓN ▼")
            self.geo_visible = False
        else:
            # Insertar antes del frame de filtros fijos
            self.geo_frame.pack(side=tk.LEFT, after=self.btn_toggle_geo)
            self.btn_toggle_geo.config(text="📍 UBICACIÓN ▲")
            self.geo_visible = True

    def on_property_selected(self, event=None):
        name = self.prop_var.get()
        if name in self.property_map:
            p = self.property_map[name]
            self.selected_property = p
            self.lbl_capacidad.config(text=f"Capacidad: {p[2]} personas")
            self.lbl_precio.config(text=f"Precio/Noche: {self._format_currency(p[7])}")
            
            # Configurar marquesina
            full_address = f"Ubicación: {p[3]}, {p[4]} ({p[5]})"
            self.marquee_text = full_address + "          " # Espacio de separación
            
            if not self.marquee_running:
                self.marquee_running = True
                self._scroll_address()
            
            # Cargar fechas reservadas
            self.reserved_ranges = self.db.get_reserved_ranges(id_inmueble=p[0])
            self.reset_selection()
            self.draw_calendar()

    def _format_currency(self, value):
        try:
            val = float(value)
            formatted = f"{val:,.2f}"
            m, d = formatted.split('.')
            return f"${m.replace(',', '.')},{d}"
        except: return str(value)

    def draw_calendar(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()
            
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        self.lbl_month.config(text=f"{meses[self.month].upper()} {self.year}")
        
        cal = calendar.monthcalendar(self.year, self.month)
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                d = date(self.year, self.month, day)
                day_info = self._get_day_info(d)
                is_selected = self._is_selected(d)
                is_past = d < self.now
                
                color = day_info["color"]
                fg = "white"
                
                if is_past:
                    fg = "#d1d8e0"
                    color = "white"
                elif is_selected:
                    color = "#3498db"
                    fg = "white"
                elif day_info["status"] == "disponible":
                    color = "#27ae60"
                    fg = "white"
                
                btn = tk.Button(self.days_frame, text=str(day), font=("Segoe UI", 14, "bold"),
                               bg=color, fg=fg, relief=tk.FLAT, bd=0,
                               command=lambda dd=d, info=day_info: self.on_day_click(dd, info))
                
                if is_past:
                     btn.config(state=tk.DISABLED)
                
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

        for i in range(7):
            self.days_frame.columnconfigure(i, weight=1)
        for i in range(len(cal)):
            self.days_frame.rowconfigure(i, weight=1)

    def _get_day_info(self, d):
        info = {
            "status": "disponible",
            "clients": [],
            "color": "#27ae60" # Verde por defecto
        }
        
        is_ingreso = False
        is_egreso = False
        is_occupied = False
        
        for ingreso, egreso, cliente in self.reserved_ranges:
            if isinstance(ingreso, str):
                ingreso = datetime.strptime(ingreso, "%Y-%m-%d").date()
            if isinstance(egreso, str):
                egreso = datetime.strptime(egreso, "%Y-%m-%d").date()
            
            if d == ingreso:
                is_ingreso = True
                info["clients"].append(f"➡️ INGRESO: {cliente}")
            elif d == egreso:
                is_egreso = True
                info["clients"].append(f"⬅️ EGRESO: {cliente}")
            elif ingreso < d < egreso:
                is_occupied = True
                info["clients"].append(f"🔴 OCUPADO: {cliente}")

        if is_occupied:
            info["status"] = "ocupado"
            info["color"] = "#e74c3c" # Rojo
        elif is_ingreso and is_egreso:
            info["status"] = "transicion"
            info["color"] = "#f1c40f" # Amarillo (Transición)
        elif is_ingreso:
            info["status"] = "ingreso"
            info["color"] = "#3498db" # Azul (Ingreso)
        elif is_egreso:
            info["status"] = "egreso"
            info["color"] = "#9b59b6" # Púrpura (Egreso)
            
        return info

    def _is_reserved(self, d):
        # Mantenemos este método por compatibilidad interna si se usa en validaciones de rango
        for ingreso, egreso, cliente in self.reserved_ranges:
            if isinstance(ingreso, str):
                ingreso = datetime.strptime(ingreso, "%Y-%m-%d").date()
            if isinstance(egreso, str):
                egreso = datetime.strptime(egreso, "%Y-%m-%d").date()
            if ingreso <= d < egreso:
                return cliente
        return None

    def _is_selected(self, d):
        if self.start_date and self.end_date:
            return self.start_date <= d < self.end_date
        if self.start_date:
            return d == self.start_date
        return False

    def on_day_click(self, d, day_info=None):
        if day_info and day_info["status"] != "disponible" and day_info["status"] != "egreso":
            # Si es egreso, permitimos click para que pueda ser el inicio de una nueva reserva
            # Pero si hay otros estados (ocupado, ingreso, transicion), mostramos info
            msg = "\n".join(day_info["clients"])
            messagebox.showinfo("Información de Reserva", msg, parent=self.window)
            if day_info["status"] != "egreso" and day_info["status"] != "transicion":
                return

        if not self.selected_property:
            messagebox.showwarning("Atención", "Primero seleccione un inmueble", parent=self.window)
            return

        if not self.start_date or (self.start_date and self.end_date):
            # Primera selección o reinicio
            self.start_date = d
            self.end_date = None
        else:
            # Segunda selección (fecha de egreso)
            if d <= self.start_date:
                self.start_date = d
                self.end_date = None
            else:
                # Verificar que no haya reservas en el medio
                temp_date = self.start_date
                has_conflict = False
                while temp_date < d:
                    if self._is_reserved(temp_date):
                        has_conflict = True
                        break
                    temp_date += timedelta(days=1)
                
                if has_conflict:
                    messagebox.showerror("Conflicto", "El rango seleccionado incluye días ya reservados.", parent=self.window)
                    self.start_date = d
                    self.end_date = None
                else:
                    self.end_date = d
        
        self.update_selection_display()
        self.draw_calendar()

    def on_discount_change(self, event=None):
        """Maneja el formateo visual del descuento mientras se escribe."""
        text = self.discount_var.get()
        if self.discount_is_percentage.get():
            # Solo permitir números y un punto
            cleaned = "".join(c for c in text if c.isdigit() or c == ".")
            if cleaned != text:
                self.discount_var.set(cleaned)
        else:
            # Formato moneda para monto fijo
            cleaned = "".join(c for c in text if c.isdigit())
            if cleaned:
                val = float(cleaned)
                formatted = f"{val:,.0f}".replace(",", ".")
                self.discount_var.set(f"${formatted}")
            else:
                self.discount_var.set("")
        
        self.update_selection_display()

    def update_selection_display(self):
        if self.start_date:
            self.lbl_desde.config(text=f"Desde: {self.start_date.strftime('%d/%m/%Y')}")
        else:
            self.lbl_desde.config(text="Desde: No seleccionada")
            
        if self.end_date:
            self.lbl_hasta.config(text=f"Hasta: {self.end_date.strftime('%d/%m/%Y')}")
            noches = (self.end_date - self.start_date).days
            self.lbl_noches.config(text=f"Noches: {noches}")
            
            # Calcular costo total
            total_sin_desc = 0
            if self.selected_property:
                precio_noche = float(self.selected_property[7])
                total_sin_desc = noches * precio_noche
                self.lbl_costo_total.config(text=f"Costo Total: {self._format_currency(total_sin_desc)}")
            
            # Calcular Descuento
            final_price = total_sin_desc
            discount_val_str = self.discount_var.get()
            
            try:
                if self.discount_is_percentage.get():
                    # Porcentaje
                    perc = float(discount_val_str) if discount_val_str else 0.0
                    discount_amount = total_sin_desc * (perc / 100)
                    final_price = total_sin_desc - discount_amount
                else:
                    # Monto fijo
                    fixed = float(discount_val_str.replace("$", "").replace(".", "")) if discount_val_str else 0.0
                    final_price = total_sin_desc - fixed
            except:
                final_price = total_sin_desc

            self.lbl_final_price.config(text=f"Precio Final: {self._format_currency(max(0, final_price))}")
            
            # Calcular precio por noche final (guía para el dueño)
            if noches > 0:
                p_noche_final = max(0, final_price) / noches
                self.lbl_final_per_night.config(text=f"P/Noche Final: {self._format_currency(p_noche_final)}")
            else:
                self.lbl_final_per_night.config(text="P/Noche Final: $0,00")

            self.btn_reservar.config(state=tk.NORMAL)
        else:
            self.lbl_hasta.config(text="Hasta: No seleccionada")
            self.lbl_noches.config(text="Noches: 0")
            self.lbl_costo_total.config(text="Costo Total: $0,00")
            self.lbl_final_price.config(text="Precio Final: $0,00")
            self.lbl_final_per_night.config(text="P/Noche Final: $0,00")
            self.btn_reservar.config(state=tk.DISABLED)

    def reset_selection(self):
        self.start_date = None
        self.end_date = None
        self.discount_var.set("0")
        self.update_selection_display()
        self.draw_calendar()

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

    def go_to_reservation(self):
        if not self.start_date or not self.end_date or not self.selected_property:
            return
            
        # Preparar datos de descuento para el formulario de reserva
        discount_val = self.discount_var.get()
        if not self.discount_is_percentage.get():
            discount_val = discount_val.replace("$", "").replace(".", "")

        initial_data = {
            "inmueble": self.selected_property[1],
            "fecha_ingreso": self.start_date.strftime("%d/%m/%Y"),
            "fecha_egreso": self.end_date.strftime("%d/%m/%Y"),
            "cantidad_personas": self.selected_property[2],
            "imagen": self.selected_property[8] if len(self.selected_property) > 8 else None,
            "descuento": discount_val,
            "discount_is_percentage": self.discount_is_percentage.get()
        }
        
        self.window.destroy()
        self.controller.create_reservation(initial_data=initial_data)
