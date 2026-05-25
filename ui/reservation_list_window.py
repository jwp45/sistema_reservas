import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from controllers.database import Database
from controllers.reservation_controller import CalendarDialog


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
        self.window.geometry("500x400")
        self.window.transient(master)

        raw = self.db.get_reservation_by_id(reservation_id)
        if not raw:
            messagebox.showerror("Error", "No se encontró la reserva")
            self.window.destroy()
            return

        # raw: id_cliente, id_inmueble, fecha_ingreso, fecha_egreso,
        #      valor_dia, noches, costo_total, costo_con_descuento,
        #      adelanto, pago_pendiente
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
        properties = self.db.get_all_properties()  # (id, nombre, ..., valor_dia)
        self.property_map = {p[1]: p for p in properties}
        property_names = list(self.property_map.keys())
        current_property_name = None
        for name, p in self.property_map.items():
            if p[0] == self.original["id_inmueble"]:
                current_property_name = name
                break

        self.fields = {}
        form_frame = ttk.Frame(self.window)
        form_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Fila: Cliente (solo lectura)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Cliente ID:", width=18).pack(side=tk.LEFT)
        ttk.Label(row, text=str(self.original["id_cliente"])).pack(side=tk.LEFT, padx=5)

        # Fila: Inmueble (editable)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Inmueble:", width=18).pack(side=tk.LEFT)
        self.fields["inmueble"] = tk.StringVar(value=current_property_name or "")
        inmueble_combo = ttk.Combobox(row, textvariable=self.fields["inmueble"], values=property_names, state="readonly")
        inmueble_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        inmueble_combo.bind("<<ComboboxSelected>>", self._on_inmueble_change)

        # Fila: Valor por Día (solo lectura)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Valor por Día:", width=18).pack(side=tk.LEFT)
        self.var_valor_dia = tk.StringVar(value=f"${self.original['valor_dia']:,.2f}")
        ttk.Label(row, textvariable=self.var_valor_dia).pack(side=tk.LEFT, padx=5)

        # Fila: Adelanto (solo lectura)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Adelanto:", width=18).pack(side=tk.LEFT)
        ttk.Label(row, text=f"${self.original['adelanto']:,.2f}").pack(side=tk.LEFT, padx=5)

        # Fila: Provincia (solo lectura)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Provincia:", width=18).pack(side=tk.LEFT)
        ttk.Label(row, text=self.original["provincia"]).pack(side=tk.LEFT, padx=5)

        # Fecha Ingreso
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Fecha Ingreso:", width=18).pack(side=tk.LEFT)
        self.fields["fecha_ingreso"] = tk.StringVar(value=self._fmt_date(self.original["fecha_ingreso"]))
        entry = ttk.Entry(row, textvariable=self.fields["fecha_ingreso"])
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(row, text="📅", width=3,
                   command=lambda: self._pick_date("fecha_ingreso")).pack(side=tk.RIGHT, padx=5)

        # Fecha Egreso
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Fecha Egreso:", width=18).pack(side=tk.LEFT)
        self.fields["fecha_egreso"] = tk.StringVar(value=self._fmt_date(self.original["fecha_egreso"]))
        entry = ttk.Entry(row, textvariable=self.fields["fecha_egreso"])
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(row, text="📅", width=3,
                   command=lambda: self._pick_date("fecha_egreso")).pack(side=tk.RIGHT, padx=5)

        # Resultados calculados (solo lectura)
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Noches:", width=18).pack(side=tk.LEFT)
        self.fields["noches"] = tk.StringVar()
        ttk.Label(row, textvariable=self.fields["noches"]).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Costo Total:", width=18).pack(side=tk.LEFT)
        self.fields["costo_total"] = tk.StringVar()
        ttk.Label(row, textvariable=self.fields["costo_total"]).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Costo c/Descuento:", width=18).pack(side=tk.LEFT)
        self.fields["costo_con_descuento"] = tk.StringVar()
        ttk.Label(row, textvariable=self.fields["costo_con_descuento"]).pack(side=tk.LEFT, padx=5)

        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Pago Pendiente:", width=18).pack(side=tk.LEFT)
        self.fields["pago_pendiente"] = tk.StringVar()
        ttk.Label(row, textvariable=self.fields["pago_pendiente"]).pack(side=tk.LEFT, padx=5)

        # Bindings para recalcular al cambiar fechas
        self.fields["fecha_ingreso"].trace_add("write", lambda *_: self.recalculate())
        self.fields["fecha_egreso"].trace_add("write", lambda *_: self.recalculate())

        self.recalculate()

        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Guardar Cambios", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

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

    def _on_inmueble_change(self, event=None):
        valor = self._get_valor_dia()
        self.var_valor_dia.set(f"${valor:,.2f}")
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
            self.fields["costo_total"].set(f"${costo_total:,.2f}")
            self.fields["costo_con_descuento"].set(f"${costo_con_desc:,.2f}")
            self.fields["pago_pendiente"].set(f"${pago_pendiente:,.2f}")
        except Exception:
            pass

    def save(self):
        try:
            ingreso = self._parse_date(self.fields["fecha_ingreso"].get())
            egreso = self._parse_date(self.fields["fecha_egreso"].get())
            noches = (egreso - ingreso).days
            if noches <= 0:
                messagebox.showerror("Error", "La fecha de egreso debe ser posterior a la de ingreso")
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
                messagebox.showinfo("Éxito", "Reserva actualizada correctamente")
                self.window.destroy()
                self.refresh_callback()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la reserva")
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")


class ReservationListWindow:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(master)
        self.window.title("Mis Reservas")
        self.window.geometry("1000x550")

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        columns = (
            "ID", "Cliente", "Teléfono", "Inmueble",
            "Ingreso", "Egreso", "Noches", "Valor/día",
            "Total", "C/Desc", "Adelanto", "Pendiente"
        )
        self.table = ttk.Treeview(main_frame, columns=columns, show="headings")

        col_widths = [40, 150, 100, 120, 90, 90, 60, 80, 90, 90, 90, 90]
        for col, w in zip(columns, col_widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=w)

        self.table.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.table, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Modificar Reserva", command=self.modify_reservation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar Reserva", command=self.delete_reservation).pack(side=tk.LEFT, padx=5)

        self.load_reservations()

    def get_selected_id(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una reserva")
            return None
        return int(self.table.item(selected[0])['values'][0])

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.load_reservations()

    def load_reservations(self):
        from datetime import datetime
        meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        db = Database()
        if db.connect():
            rows = db.get_all_reservations()
            for row in rows:
                vals = list(row)
                for i in (7, 8, 9, 10, 11):
                    try:
                        vals[i] = f"{float(vals[i]):,.2f}"
                    except (ValueError, TypeError, IndexError):
                        pass
                for i in (4, 5):
                    try:
                        d = datetime.strptime(str(vals[i]), "%Y-%m-%d")
                        vals[i] = f"{d.day} {meses[d.month]} {d.year}"
                    except (ValueError, TypeError, IndexError):
                        pass
                self.table.insert("", "end", values=tuple(vals))
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def delete_reservation(self):
        rid = self.get_selected_id()
        if rid is None:
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta reserva?"):
            db = Database()
            if db.connect():
                if db.delete_reservation(rid):
                    messagebox.showinfo("Éxito", "Reserva eliminada correctamente")
                    self.refresh_table()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la reserva")

    def modify_reservation(self):
        rid = self.get_selected_id()
        if rid is None:
            return
        EditReservationWindow(self.master, rid, self.refresh_table)
