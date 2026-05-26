import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers.database import Database

class QuotationListWindow:
    def __init__(self, master, reservation_controller):
        self.master = master
        self.controller = reservation_controller
        self.db = Database()
        self.db.connect()

        self.window = tk.Toplevel(master)
        self.window.title("Historial de Cotizaciones Enviadas")
        self.window.geometry("1100x700")
        self.window.configure(bg="#f0f2f5")

        # --- ESTILOS LOCALES ---
        style = ttk.Style(self.window)
        style.configure("Quot.TFrame", background="#f0f2f5")
        style.configure("QuotAction.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        # --- ENCABEZADO ---
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📑 HISTORIAL DE COTIZACIONES", font=("Segoe UI", 16, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=30, pady=20)

        main_container = ttk.Frame(self.window, padding=30, style="Quot.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- TABLA DE COTIZACIONES ---
        table_container = tk.Frame(main_container, bg="white", highlightbackground="#e0e0e0", highlightthickness=1, padx=2, pady=2)
        table_container.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(table_container)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.quot_table = ttk.Treeview(table_container, columns=("ID", "Cliente", "Inmueble", "Desde", "Hasta", "Noches", "Precio Final", "Fecha"), 
                                        show="headings", yscrollcommand=tree_scroll.set, selectmode="browse")
        self.quot_table.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.quot_table.yview)

        # Cabeceras
        headers = [("ID", 50), ("Cliente", 150), ("Inmueble", 150), ("Desde", 100), ("Hasta", 100), ("Noches", 70), ("Precio Final", 120), ("Fecha", 150)]
        for h, w in headers:
            self.quot_table.heading(h, text=h.upper())
            self.quot_table.column(h, width=w, anchor=tk.CENTER if h in ["Noches", "ID", "Desde", "Hasta"] else tk.W)

        # --- BARRA DE ACCIONES ---
        btn_frame = ttk.Frame(main_container, style="Quot.TFrame")
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="🗑️ ELIMINAR", command=self.delete_quotation).pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="🚀 CONVERTIR EN RESERVA", style="QuotAction.TButton", 
                   command=self.convert_to_reservation).pack(side=tk.RIGHT)

        self.load_quotations()

    def load_quotations(self):
        """Carga las cotizaciones desde la DB."""
        for item in self.quot_table.get_children():
            self.quot_table.delete(item)
            
        quotations = self.db.get_all_quotations()
        for q in quotations:
            # q = (0:id, 1:cliente, 2:inmueble, 3:f_ing, 4:f_eg, 5:noches, 6:final, 7:f_cot, ...)
            
            # Formatear fechas de ingreso/egreso
            f_ing = q[3]
            if hasattr(f_ing, 'strftime'):
                f_ing = f_ing.strftime("%d/%m/%Y")
                
            f_eg = q[4]
            if hasattr(f_eg, 'strftime'):
                f_eg = f_eg.strftime("%d/%m/%Y")
            
            # Formatear fecha de creación de cotización
            f_cot = q[7]
            if hasattr(f_cot, 'strftime'):
                f_cot = f_cot.strftime("%d/%m/%Y %H:%M")

            # Asegurar que el precio final (Decimal o Float) se convierta a float para formateo
            try:
                precio_final = float(q[6])
            except:
                precio_final = 0.0
            
            display_values = (q[0], q[1], q[2], f_ing, f_eg, q[5], self._format_currency(precio_final), f_cot)
            self.quot_table.insert("", "end", values=display_values)

    def _format_currency(self, value):
        try:
            val = float(value)
            formatted = f"{val:,.2f}"
            m, d = formatted.split('.')
            return f"${m.replace(',', '.')},{d}"
        except: return str(value)

    def delete_quotation(self):
        selected = self.quot_table.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione una cotización para eliminar.")
            return
            
        quot_id = self.quot_table.item(selected)['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar la cotización #{quot_id}?"):
            if self.db.delete_quotation(quot_id):
                self.load_quotations()

    def convert_to_reservation(self):
        """Toma los datos de la cotización y abre el formulario de reserva."""
        selected = self.quot_table.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione una cotización para convertir.")
            return
            
        quot_id = self.quot_table.item(selected)['values'][0]
        
        # Obtener datos completos de la DB
        all_q = self.db.get_all_quotations()
        q_data = next((x for x in all_q if x[0] == quot_id), None)
        
        if not q_data: return

        # q_data index mapping:
        # 0:id, 1:cliente_nombre, 2:inmueble_nombre, 3:f_ing, 4:f_eg, 
        # 5:noches, 6:final, 7:f_cot, 8:id_cliente, 9:id_inmueble, 10:val_d, 11:total, 12:desc, 13:capacidad
        
        initial_data = {
            "id_cliente": q_data[8],
            "inmueble": q_data[2],
            "fecha_ingreso": q_data[3].strftime("%d/%m/%Y") if hasattr(q_data[3], 'strftime') else q_data[3],
            "fecha_egreso": q_data[4].strftime("%d/%m/%Y") if hasattr(q_data[4], 'strftime') else q_data[4],
            "descuento": str(int(q_data[12])),
            "discount_is_percentage": False, # Siempre pasamos el monto fijo calculado
            "cantidad_personas": q_data[13]
        }
        
        if messagebox.askyesno("Convertir", f"¿Desea crear la reserva para {q_data[1]} basada en esta cotización?"):
            self.window.destroy()
            self.controller.create_reservation(initial_data=initial_data)
