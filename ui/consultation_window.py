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
        self.window.geometry("1000x900")
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
        
        self.setup_ui()
        self.load_properties()

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
        
        # Selección de Inmueble (con filtros)
        sel_card = tk.LabelFrame(left_panel, text=" 🏠 BÚSQUEDA Y FILTROS ", font=("Segoe UI", 9, "bold"), 
                                bg="white", padx=15, pady=15, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        sel_card.pack(fill=tk.X, pady=(0, 20))

        # Filtro: Provincia
        tk.Label(sel_card, text="PROVINCIA:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        self.prov_var = tk.StringVar(value="Todas")
        self.combo_prov = ttk.Combobox(sel_card, textvariable=self.prov_var, state="readonly", font=("Segoe UI", 9))
        self.combo_prov.pack(fill=tk.X, pady=(2, 8))
        self.combo_prov.bind("<<ComboboxSelected>>", self.apply_filters)

        # Filtro: Localidad
        tk.Label(sel_card, text="LOCALIDAD:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        self.loc_var = tk.StringVar(value="Todas")
        self.combo_loc = ttk.Combobox(sel_card, textvariable=self.loc_var, state="readonly", font=("Segoe UI", 9))
        self.combo_loc.pack(fill=tk.X, pady=(2, 8))
        self.combo_loc.bind("<<ComboboxSelected>>", self.apply_filters)

        # Filtro: Tipo
        tk.Label(sel_card, text="TIPO:", font=("Segoe UI", 8, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w")
        self.tipo_var = tk.StringVar(value="Todos")
        self.combo_tipo = ttk.Combobox(sel_card, textvariable=self.tipo_var, state="readonly", font=("Segoe UI", 9))
        self.combo_tipo.pack(fill=tk.X, pady=(2, 8))
        self.combo_tipo.bind("<<ComboboxSelected>>", self.apply_filters)

        # Selector Final de Inmueble
        tk.Label(sel_card, text="SELECCIONAR INMUEBLE:", font=("Segoe UI", 8, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=(5, 0))
        self.prop_var = tk.StringVar()
        self.combo_prop = ttk.Combobox(sel_card, textvariable=self.prop_var, state="readonly", font=("Segoe UI", 10, "bold"))
        self.combo_prop.pack(fill=tk.X, pady=5)
        self.combo_prop.bind("<<ComboboxSelected>>", self.on_property_selected)
        
        # Resumen del Inmueble
        self.info_card = tk.LabelFrame(left_panel, text=" 📝 DETALLES ", font=("Segoe UI", 9, "bold"), 
                                     bg="white", padx=15, pady=15, relief=tk.FLAT, highlightbackground="#e0e0e0", highlightthickness=1)
        self.info_card.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_capacidad = tk.Label(self.info_card, text="Capacidad: —", bg="white", font=("Segoe UI", 10), anchor="w")
        self.lbl_capacidad.pack(fill=tk.X, pady=5)
        self.lbl_precio = tk.Label(self.info_card, text="Precio/Noche: —", bg="white", font=("Segoe UI", 10), anchor="w")
        self.lbl_precio.pack(fill=tk.X, pady=5)
        self.lbl_ubicacion = tk.Label(self.info_card, text="Ubicación: —", bg="white", font=("Segoe UI", 9), fg="#7f8c8d", anchor="w", wraplength=280)
        self.lbl_ubicacion.pack(fill=tk.X, pady=5)

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
        
        self.btn_reservar = ttk.Button(left_panel, text="🚀 RESERVAR AHORA", state=tk.DISABLED, command=self.go_to_reservation)
        self.btn_reservar.pack(fill=tk.X, pady=10)
        
        ttk.Button(left_panel, text="LIMPIAR SELECCIÓN", command=self.reset_selection).pack(fill=tk.X)

        # Panel Derecho: Calendario
        right_panel = tk.Frame(main_frame, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        self._create_legend(legend_frame, "#e74c3c", "Ocupado")
        self._create_legend(legend_frame, "#3498db", "Tu Selección")

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

    def on_property_selected(self, event=None):
        name = self.prop_var.get()
        if name in self.property_map:
            p = self.property_map[name]
            self.selected_property = p
            self.lbl_capacidad.config(text=f"Capacidad: {p[2]} personas")
            self.lbl_precio.config(text=f"Precio/Noche: {self._format_currency(p[7])}")
            self.lbl_ubicacion.config(text=f"Ubicación: {p[3]}, {p[4]} ({p[5]})")
            
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
                is_reserved = self._is_reserved(d)
                is_selected = self._is_selected(d)
                is_past = d < self.now
                
                color = "white"
                fg = "black"
                if is_past:
                    fg = "#d1d8e0"
                elif is_reserved:
                    color = "#e74c3c"
                    fg = "white"
                elif is_selected:
                    color = "#3498db"
                    fg = "white"
                else:
                    color = "#27ae60"
                    fg = "white"
                
                btn = tk.Button(self.days_frame, text=str(day), font=("Segoe UI", 10, "bold"),
                               bg=color, fg=fg, relief=tk.FLAT, bd=0,
                               command=lambda dd=d: self.on_day_click(dd))
                
                if is_past or (is_reserved and not is_selected):
                     btn.config(state=tk.DISABLED if is_past or is_reserved else tk.NORMAL)
                
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

        for i in range(7):
            self.days_frame.columnconfigure(i, weight=1)
        for i in range(len(cal)):
            self.days_frame.rowconfigure(i, weight=1)

    def _is_reserved(self, d):
        for ingreso, egreso in self.reserved_ranges:
            if isinstance(ingreso, str):
                ingreso = datetime.strptime(ingreso, "%Y-%m-%d").date()
            if isinstance(egreso, str):
                egreso = datetime.strptime(egreso, "%Y-%m-%d").date()
            if ingreso <= d < egreso:
                return True
        return False

    def _is_selected(self, d):
        if self.start_date and self.end_date:
            return self.start_date <= d < self.end_date
        if self.start_date:
            return d == self.start_date
        return False

    def on_day_click(self, d):
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
            if self.selected_property:
                precio_noche = float(self.selected_property[7])
                costo_total = noches * precio_noche
                self.lbl_costo_total.config(text=f"Costo Total: {self._format_currency(costo_total)}")
            
            self.btn_reservar.config(state=tk.NORMAL)
        else:
            self.lbl_hasta.config(text="Hasta: No seleccionada")
            self.lbl_noches.config(text="Noches: 0")
            self.lbl_costo_total.config(text="Costo Total: $0,00")
            self.btn_reservar.config(state=tk.DISABLED)

    def reset_selection(self):
        self.start_date = None
        self.end_date = None
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
            
        initial_data = {
            "inmueble": self.selected_property[1],
            "fecha_ingreso": self.start_date.strftime("%d/%m/%Y"),
            "fecha_egreso": self.end_date.strftime("%d/%m/%Y"),
            "cantidad_personas": self.selected_property[2],
            "imagen": self.selected_property[8] if len(self.selected_property) > 8 else None
        }
        
        self.window.destroy()
        self.controller.create_reservation(initial_data=initial_data)
