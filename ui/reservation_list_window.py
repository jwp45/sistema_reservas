import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from controllers.database import Database
from controllers.reservation_controller import CalendarDialog
from ui.payment_window import PaymentWindow


class EditReservationWindow:
    def __init__(self, master, reservation_id, refresh_callback):
        self.master = master
        self.reservation_id = reservation_id
        self.refresh_callback = refresh_callback
        self.db = Database()
        self.db.connect()
        self.meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                      "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

        self.window = tk.Toplevel(master)
        self.window.title("Modificar Reserva")
        self.window.geometry("600x650")
        self.window.configure(bg="#f8f9fa")
        self.window.transient(master)

        raw = self.db.get_reservation_by_id(reservation_id)
        if not raw:
            messagebox.showerror("Error", "No se encontró la reserva", parent=self.window)
            self.window.destroy()
            return

        # self.original mapping...
        self.original = {
            "id_cliente": raw[0],
            "id_inmueble": raw[1],
            "fecha_ingreso": raw[2],
            "fecha_egreso": raw[3],
            "valor_dia": float(raw[4]),
            "noches": int(raw[5]),
            "costo_total": float(raw[6]),
            "costo_con_descuento": float(raw[7]),
            "adelanto": float(raw[8]),
            "pago_pendiente": float(raw[9]),
            "provincia": raw[10],
        }
        self.descuento_amount = self.original["costo_total"] - self.original["costo_con_descuento"]

        # Cargar inmuebles
        properties = self.db.get_all_properties()
        self.property_map = {p[1]: p for p in properties}
        property_names = list(self.property_map.keys())
        current_property_name = None
        for name, p in self.property_map.items():
            if p[0] == self.original["id_inmueble"]:
                current_property_name = name
                break

        self.fields = {}
        
        # Estilos locales
        style = ttk.Style(self.window)
        style.configure("EditHeader.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2c3e50")
        style.configure("EditSection.TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"Modificando Reserva #{reservation_id}", style="EditHeader.TLabel").pack(pady=(0, 20))

        # ─── SECCIÓN: DATOS GENERALES ────────────────────────────
        sec_gen = ttk.LabelFrame(main_frame, text=" Información General ", padding=15, style="EditSection.TLabelframe")
        sec_gen.pack(fill=tk.X, pady=10)
        sec_gen.columnconfigure(1, weight=1)

        ttk.Label(sec_gen, text="Cliente ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(sec_gen, text=str(self.original["id_cliente"]), font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=10)

        ttk.Label(sec_gen, text="Inmueble:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fields["inmueble"] = tk.StringVar(value=current_property_name or "")
        combo_inmueble = ttk.Combobox(sec_gen, textvariable=self.fields["inmueble"], values=property_names, state="readonly")
        combo_inmueble.grid(row=1, column=1, sticky=tk.EW, padx=10)
        combo_inmueble.bind("<<ComboboxSelected>>", self._on_inmueble_change)

        # Fila: Valor por Día (solo lectura)
        row = ttk.Frame(sec_gen)
        row.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(row, text="Valor por Día:").pack(side=tk.LEFT)
        self.var_valor_dia = tk.StringVar(value=self._format_currency(self.original['valor_dia']))
        ttk.Label(row, textvariable=self.var_valor_dia, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=10)

        # ─── SECCIÓN: FECHAS ────────────────────────────
        sec_date = ttk.LabelFrame(main_frame, text=" Estadía ", padding=15, style="EditSection.TLabelframe")
        sec_date.pack(fill=tk.X, pady=10)
        sec_date.columnconfigure(1, weight=1)

        ttk.Label(sec_date, text="Fecha Ingreso:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fields["fecha_ingreso"] = tk.StringVar(value=self._fmt_date(self.original["fecha_ingreso"]))
        fi_f = ttk.Frame(sec_date)
        fi_f.grid(row=0, column=1, sticky=tk.EW, padx=10)
        ttk.Entry(fi_f, textvariable=self.fields["fecha_ingreso"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(fi_f, text="📅", width=3, command=lambda: self._pick_date("fecha_ingreso")).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(sec_date, text="Fecha Egreso:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fields["fecha_egreso"] = tk.StringVar(value=self._fmt_date(self.original["fecha_egreso"]))
        fe_f = ttk.Frame(sec_date)
        fe_f.grid(row=1, column=1, sticky=tk.EW, padx=10)
        ttk.Entry(fe_f, textvariable=self.fields["fecha_egreso"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(fe_f, text="📅", width=3, command=lambda: self._pick_date("fecha_egreso")).pack(side=tk.RIGHT, padx=(5, 0))

        # ─── SECCIÓN: RESUMEN FINANCIERO ────────────────────────────
        sec_fin = ttk.LabelFrame(main_frame, text=" Resumen Financiero ", padding=15, style="EditSection.TLabelframe")
        sec_fin.pack(fill=tk.X, pady=10)
        sec_fin.columnconfigure(1, weight=1)
        sec_fin.columnconfigure(3, weight=1)

        ttk.Label(sec_fin, text="Noches:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fields["noches"] = tk.StringVar()
        ttk.Label(sec_fin, textvariable=self.fields["noches"], font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=10)

        ttk.Label(sec_fin, text="Costo Total:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.fields["costo_total"] = tk.StringVar()
        ttk.Label(sec_fin, textvariable=self.fields["costo_total"]).grid(row=0, column=3, sticky=tk.W, padx=10)

        ttk.Label(sec_fin, text="Con Descuento:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fields["costo_con_descuento"] = tk.StringVar()
        ttk.Label(sec_fin, textvariable=self.fields["costo_con_descuento"], foreground="#27ae60", font=("Segoe UI", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=10)

        ttk.Label(sec_fin, text="Pago Pendiente:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.fields["pago_pendiente"] = tk.StringVar()
        ttk.Label(sec_fin, textvariable=self.fields["pago_pendiente"], foreground="#e74c3c", font=("Segoe UI", 10, "bold")).grid(row=1, column=3, sticky=tk.W, padx=10)

        # Bindings
        self.fields["fecha_ingreso"].trace_add("write", lambda *_: self.recalculate())
        self.fields["fecha_egreso"].trace_add("write", lambda *_: self.recalculate())

        self.recalculate()

        # Botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 20, 0, 0))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Guardar Cambios", style="Action.TButton", command=self.save).pack(side=tk.RIGHT, padx=5)

    def _fmt_date(self, d):
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d").date()
        return f"{d.day} {self.meses[d.month]} {d.year}"

    def _parse_date(self, s):
        parts = s.strip().split()
        dia, mes_str, anio = int(parts[0]), parts[1].lower(), int(parts[2])
        meses_inv = {m: i for i, m in enumerate(self.meses)}
        return date(anio, meses_inv[mes_str], dia)

    def _pick_date(self, field_name):
        def callback(date_str):
            d = datetime.strptime(date_str, "%d/%m/%Y").date()
            self.fields[field_name].set(self._fmt_date(d))

        id_inmueble = self._get_id_inmueble()
        ranges = self.db.get_reserved_ranges(id_inmueble=id_inmueble, exclude_id=self.reservation_id)
        CalendarDialog(self.window, callback, reserved_ranges=ranges)

    def _get_valor_dia(self):
        name = self.fields["inmueble"].get()
        if name in self.property_map:
            return float(self.property_map[name][7])
        return self.original["valor_dia"]

    def _get_id_inmueble(self):
        name = self.fields["inmueble"].get()
        if name in self.property_map:
            return self.property_map[name][0]
        return self.original["id_inmueble"]

    def _format_currency(self, value):
        """Formatea un valor numérico como moneda ($1.234,56)."""
        try:
            if isinstance(value, str):
                value = value.replace('$', '').replace('.', '').replace(',', '.')
                value = float(value)
            formatted = f"{value:,.2f}"
            main_part, decimal_part = formatted.split('.')
            main_part = main_part.replace(',', '.')
            return f"${main_part},{decimal_part}"
        except (ValueError, TypeError):
            return "$0,00"

    def _on_inmueble_change(self, event=None):
        valor = self._get_valor_dia()
        self.var_valor_dia.set(self._format_currency(valor))
        self.recalculate()

    def recalculate(self):
        try:
            ingreso = self._parse_date(self.fields["fecha_ingreso"].get())
            egreso = self._parse_date(self.fields["fecha_egreso"].get())
            noches = (egreso - ingreso).days
            if noches < 0:
                noches = 0
            valor_dia = self._get_valor_dia()
            costo_total = noches * valor_dia
            costo_con_desc = max(costo_total - self.descuento_amount, 0)
            pago_pendiente = costo_con_desc - self.original["adelanto"]

            self.fields["noches"].set(str(noches))
            self.fields["costo_total"].set(self._format_currency(costo_total))
            self.fields["costo_con_descuento"].set(self._format_currency(costo_con_desc))
            self.fields["pago_pendiente"].set(self._format_currency(pago_pendiente))
        except Exception:
            pass

    def save(self):
        try:
            ingreso = self._parse_date(self.fields["fecha_ingreso"].get())
            egreso = self._parse_date(self.fields["fecha_egreso"].get())
            noches = (egreso - ingreso).days
            if noches <= 0:
                messagebox.showerror("Error", "La fecha de egreso debe ser posterior a la de ingreso", parent=self.window)
                return
            valor_dia = self._get_valor_dia()
            costo_total = noches * valor_dia
            costo_con_desc = max(costo_total - self.descuento_amount, 0)
            pago_pendiente = costo_con_desc - self.original["adelanto"]

            data = {
                "id_cliente": self.original["id_cliente"],
                "id_inmueble": self._get_id_inmueble(),
                "fecha_ingreso": ingreso.isoformat(),
                "fecha_egreso": egreso.isoformat(),
                "valor_dia": valor_dia,
                "noches": noches,
                "costo_total": costo_total,
                "costo_con_descuento": costo_con_desc,
                "adelanto": self.original["adelanto"],
                "pago_pendiente": pago_pendiente,
                "provincia": self.original["provincia"],
            }
            if self.db.update_reservation(self.reservation_id, data):
                messagebox.showinfo("Éxito", "Reserva actualizada correctamente", parent=self.window)
                self.window.destroy()
                self.refresh_callback()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la reserva", parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}", parent=self.window)


class ReservationListWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Historial de Reservas")
        self.window.geometry("1200x700")
        self.window.configure(bg="#f8f9fa")

        # Estilos locales
        style = ttk.Style(self.window)
        style.configure("Res.TFrame", background="#f8f9fa")
        style.configure("Card.TFrame", background="white", relief="ridge", borderwidth=1)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("Stat.TLabel", font=("Segoe UI", 10), foreground="#7f8c8d", background="#f8f9fa")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_container = ttk.Frame(self.window, padding=25, style="Res.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- CABECERA ---
        header_frame = ttk.Frame(main_container, style="Res.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text="Gestión de Reservas", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.lbl_stats = ttk.Label(header_frame, text="Cargando datos...", style="Stat.TLabel")
        self.lbl_stats.pack(side=tk.LEFT, padx=25, pady=(12, 0))

        # --- BARRA DE FILTROS ---
        filter_card = ttk.Frame(main_container, padding=15, style="Card.TFrame")
        filter_card.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(filter_card, text="BUSCAR:", font=("Segoe UI", 9, "bold"), background="white").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_card, textvariable=self.search_var, font=("Segoe UI", 10), width=40)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.filter_reservations())

        ttk.Button(filter_card, text="Refrescar Lista", command=self.refresh_table).pack(side=tk.RIGHT, padx=5)

        # --- TABLA DE RESERVAS ---
        table_frame = ttk.Frame(main_container, style="Card.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = (
            "ID", "Cliente", "Teléfono", "Inmueble",
            "Ingreso", "Egreso", "Noches", "Valor/día",
            "Total", "C/Desc", "Adelanto", "Pendiente"
        )
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                 yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set,
                                 selectmode="browse")
        
        y_scroll.config(command=self.table.yview)
        x_scroll.config(command=self.table.xview)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.pack(fill=tk.BOTH, expand=True)

        # Configuración de columnas
        col_widths = [40, 160, 110, 140, 120, 120, 60, 90, 100, 100, 100, 110]
        for col, w in zip(columns, col_widths):
            self.table.heading(col, text=col.upper(), anchor=tk.CENTER)
            self.table.column(col, width=w, anchor=tk.CENTER if col in ["ID", "Noches"] else tk.W)

        # --- ACCIONES ---
        btn_frame = ttk.Frame(main_container, style="Res.TFrame")
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="ELIMINAR RESERVA", command=self.delete_reservation).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="VER PAGOS / ABONAR", command=self.open_payment_window).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="MODIFICAR DETALLES", style="Action.TButton", command=self.modify_reservation).pack(side=tk.RIGHT)

        self.load_reservations()

    def _parse_currency(self, value_str):
        """Convierte una cadena de moneda ($1.234,56) a float de forma robusta."""
        try:
            # Eliminar $, espacios y puntos de miles, luego cambiar coma decimal por punto
            clean = str(value_str).replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except (ValueError, TypeError):
            return 0.0

    def open_payment_window(self):
        """Abre la ventana para consultar historial o registrar un abono."""
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para consultar pagos.", parent=self.window)
            return
        
        vals = self.table.item(selected[0])['values']
        # vals: 0:ID, 1:Cliente, ..., 11:Pendiente
        try:
            rid = vals[0]
            client = vals[1]
            pending = self._parse_currency(vals[11])
            
            # Abrimos la ventana siempre, el PaymentWindow manejará si permite abonar o no
            PaymentWindow(self.window, rid, client, pending, self.load_reservations)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar la información de pagos: {str(e)}", parent=self.window)

    def load_reservations(self):
        from datetime import datetime
        meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        for item in self.table.get_children():
            self.table.delete(item)
            
        db = Database()
        if db.connect():
            rows = db.get_all_reservations()
            total_pending = 0.0
            
            for row in rows:
                vals = list(row)
                
                # Formatear montos
                for i in (7, 8, 9, 10, 11):
                    try:
                        val = float(vals[i])
                        if i == 11: total_pending += val # Acumular pendiente
                        formatted = f"{val:,.2f}"
                        m, d_part = formatted.split('.')
                        m = m.replace(',', '.')
                        vals[i] = f"${m},{d_part}"
                    except: pass
                
                # Formatear fechas
                for i in (4, 5):
                    try:
                        d = datetime.strptime(str(vals[i]), "%Y-%m-%d")
                        vals[i] = f"{d.day} {meses[d.month]} {d.year}"
                    except: pass
                
                self.table.insert("", "end", values=tuple(vals))
            
            # Actualizar estadísticas
            self.lbl_stats.config(text=f"Total: {len(rows)} reservas | Cobro Pendiente: ${total_pending:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)

    def filter_reservations(self):
        query = self.search_var.get().lower()
        # Para filtrar Treeview en tiempo real, solemos recargar.
        # Una alternativa más eficiente es ocultar items, pero recargar es más seguro con la BD.
        # Aquí implementaremos un filtrado local sobre los datos cargados si fuera posible, 
        # pero por simplicidad y consistencia refrescaremos con lógica local.
        
        for item in self.table.get_children():
            values = self.table.item(item, 'values')
            # Buscar en Cliente, Inmueble e ID
            search_text = f"{values[0]} {values[1]} {values[3]}".lower()
            if query in search_text:
                pass # Mantener
            else:
                self.table.detach(item) # Ocultar temporalmente

    def refresh_table(self):
        self.search_var.set("")
        self.load_reservations()

    def get_selected_id(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una reserva de la lista", parent=self.window)
            return None
        return int(self.table.item(selected[0])['values'][0])

    def delete_reservation(self):
        rid = self.get_selected_id()
        if rid is None: return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la reserva #{rid}?", parent=self.window):
            db = Database()
            if db.connect():
                if db.delete_reservation(rid):
                    messagebox.showinfo("Éxito", "Reserva eliminada correctamente", parent=self.window)
                    self.load_reservations()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la reserva", parent=self.window)

    def modify_reservation(self):
        rid = self.get_selected_id()
        if rid is None: return
        EditReservationWindow(self.master, rid, self.load_reservations)
