import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from controllers.database import Database

class QuotationListWindow:
    def __init__(self, master, reservation_controller):
        self.master = master
        self.controller = reservation_controller
        self.db = Database()
        self.db.connect()
        self.cards = []
        self.selected_id = None

        self.window = tk.Toplevel(master)
        self.window.title("Historial de Cotizaciones Enviadas")
        self.window.geometry("1100x800")
        self.window.configure(bg="#f0f2f5")

        # --- ESTILOS LOCALES ---
        style = ttk.Style(self.window)
        style.configure("Quot.TFrame", background="#f0f2f5")
        style.configure("QuotAction.TButton", font=("Segoe UI", 10, "bold"), padding=12)

        # --- ENCABEZADO ---
        header_frame = tk.Frame(self.window, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📑 HISTORIAL DE COTIZACIONES", font=("Segoe UI", 16, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=30, pady=20)

        self.lbl_stats = tk.Label(header_frame, text="Cargando...", font=("Segoe UI", 10), 
                                 bg="#2c3e50", fg="#95a5a6")
        self.lbl_stats.pack(side=tk.RIGHT, padx=30)

        main_container = ttk.Frame(self.window, padding=30, style="Quot.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- BARRA DE BÚSQUEDA ---
        search_card = tk.Frame(main_container, bg="white", highlightbackground="#e0e0e0", highlightthickness=1, padx=20, pady=15)
        search_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(search_card, text="🔎 BUSCAR COTIZACIÓN:", font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 15))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_card, textvariable=self.search_var, font=("Segoe UI", 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_cards())

        ttk.Button(search_card, text="🔄 REFRESCAR", command=self.load_quotations).pack(side=tk.RIGHT, padx=(15, 0))

        # --- LISTADO (SCROLL) ---
        canvas_frame = ttk.Frame(main_container, style="Quot.TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg="#f0f2f5")

        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw", width=1020)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- BARRA DE ACCIONES ---
        btn_frame = ttk.Frame(main_container, style="Quot.TFrame")
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="🗑️ ELIMINAR SELECCIONADA", command=self.delete_quotation).pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="🚀 CONVERTIR EN RESERVA", style="QuotAction.TButton", 
                   command=self.convert_to_reservation).pack(side=tk.RIGHT)

        # Limpiar cotizaciones vencidas antes de cargar (15 días = 360 horas)
        self.db.cleanup_old_quotations(hours=360)
        
        self.load_quotations()

    def bind_select(self, widget, quot_id):
        widget.bind("<Button-1>", lambda e, i=quot_id: self.select_card(i))
        for child in widget.winfo_children():
            self.bind_select(child, quot_id)

    def create_card(self, q):
        # q = (0:id, 1:cliente, 2:inmueble, 3:f_ing, 4:f_eg, 5:noches, 6:final, 7:f_cot, 8:id_cliente, 9:id_inmueble, 10:val_d, 11:total, 12:desc, 13:capacidad)
        quot_id = q[0]
        quot_code = f"Q-{str(quot_id).zfill(5)}"
        client_name = q[1]
        property_name = q[2]
        now = datetime.now()

        # Calcular Vigencia
        f_cot_raw = q[7]
        vigencia_text = "Expirado"
        vigencia_color = "#e74c3c"
        if isinstance(f_cot_raw, datetime):
            expiracion = f_cot_raw + timedelta(days=15)
            restante = expiracion - now
            if restante.total_seconds() > 0:
                dias = restante.days
                horas = restante.seconds // 3600
                vigencia_text = f"Quedan: {dias}d {horas}h" if dias > 0 else f"Quedan: {horas}h"
                vigencia_color = "#f39c12" if dias < 3 else "#27ae60"

        card = tk.Frame(self.scrollable, bg="white", bd=0, highlightbackground="#d1d8e0", highlightthickness=1)
        card.pack(fill=tk.X, padx=5, pady=8)
        self.bind_select(card, quot_id)
        
        inner = tk.Frame(card, bg="white", padx=15, pady=15)
        inner.pack(fill=tk.X)
        self.bind_select(inner, quot_id)

        # Izquierda: Código e Info Principal
        info_f = tk.Frame(inner, bg="white")
        info_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bind_select(info_f, quot_id)

        code_f = tk.Frame(info_f, bg="#ebf5fb", padx=8, pady=2)
        code_f.pack(anchor="w")
        tk.Label(code_f, text=quot_code, font=("Segoe UI", 10, "bold"), bg="#ebf5fb", fg="#2980b9").pack()
        
        tk.Label(info_f, text=client_name.upper(), font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=(5,0))
        tk.Label(info_f, text=f"🏠 {property_name}", font=("Segoe UI", 11), bg="white", fg="#34495e").pack(anchor="w")
        
        f_ing_str = q[3].strftime('%d/%m/%Y') if hasattr(q[3], 'strftime') else str(q[3])
        f_eg_str = q[4].strftime('%d/%m/%Y') if hasattr(q[4], 'strftime') else str(q[4])
        details_text = f"📅 {f_ing_str} al {f_eg_str} ({q[5]} noches)"
        tk.Label(info_f, text=details_text, font=("Segoe UI", 9), bg="white", fg="#7f8c8d").pack(anchor="w", pady=5)

        # Centro: Vigencia y Fecha Cotización
        time_f = tk.Frame(inner, bg="white", padx=20)
        time_f.pack(side=tk.LEFT, fill=tk.Y)
        self.bind_select(time_f, quot_id)

        tk.Label(time_f, text="VIGENCIA", font=("Segoe UI", 8, "bold"), bg="white", fg="#bdc3c7").pack(anchor="w")
        tk.Label(time_f, text=vigencia_text, font=("Segoe UI", 10, "bold"), bg="white", fg=vigencia_color).pack(anchor="w")
        
        f_cot_str = q[7].strftime("%d/%m/%Y %H:%M") if hasattr(q[7], 'strftime') else str(q[7])
        tk.Label(time_f, text=f"Enviada: {f_cot_str}", font=("Segoe UI", 8), bg="white", fg="#95a5a6").pack(anchor="w", pady=(5,0))

        # Derecha: Precios y Marketing
        price_f = tk.Frame(inner, bg="white", padx=10)
        price_f.pack(side=tk.RIGHT, fill=tk.Y)
        self.bind_select(price_f, quot_id)

        # Verificar disponibilidad y si ya fue enviada
        is_free = self.db.is_range_available(q[9], q[3], q[4])
        mkt_enviado = q[14] if len(q) > 14 else 0
        
        try:
            precio_orig = float(q[11])
            monto_desc = float(q[12])
            precio_final = float(q[6])
            pct = int((monto_desc/precio_orig)*100) if precio_orig > 0 else 0
            
            if monto_desc > 0:
                tk.Label(price_f, text=self._format_currency(precio_orig), font=("Segoe UI", 9, "overstrike"), bg="white", fg="#bdc3c7").pack(anchor="e")
                tk.Label(price_f, text=f"DESC. {pct}%: -{self._format_currency(monto_desc)}", font=("Segoe UI", 8, "bold"), bg="white", fg="#e74c3c").pack(anchor="e")
            
            tk.Label(price_f, text=self._format_currency(precio_final), font=("Segoe UI", 16, "bold"), bg="white", fg="#27ae60").pack(anchor="e", pady=(5, 0))
            
            # Botón de Marketing o Estado
            if mkt_enviado:
                tk.Label(price_f, text="✨ OFERTA ENVIADA", font=("Segoe UI", 8, "bold"), bg="#e8f8f5", fg="#16a085").pack(anchor="e", pady=(10, 0))
            elif is_free:
                btn_mkt = tk.Button(price_f, text="🎁 RE-OFERTAR", font=("Segoe UI", 8, "bold"), 
                                    bg="#27ae60", fg="white", bd=0, padx=10, pady=5, cursor="hand2",
                                    command=lambda i=quot_id: self.open_reoffer_dialog(i))
                btn_mkt.pack(anchor="e", pady=(10, 0))
            else:
                tk.Label(price_f, text="⚠️ OCUPADO", font=("Segoe UI", 8, "bold"), bg="white", fg="#95a5a6").pack(anchor="e", pady=(10, 0))

        except: pass

        card.quot_id = quot_id
        card.search_data = f"{quot_code} {client_name} {property_name}".lower()
        self.cards.append(card)

    def open_reoffer_dialog(self, quot_id):
        """Abre un diálogo para proponer un nuevo descuento."""
        # Obtener datos de la cotización
        all_q = self.db.get_all_quotations()
        q = next((x for x in all_q if x[0] == quot_id), None)
        if not q: return

        # Ventana emergente
        dialog = tk.Toplevel(self.window)
        dialog.title("Mejorar Oferta de Marketing")
        dialog.geometry("400x350")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self.window)
        dialog.grab_set()

        main_d = ttk.Frame(dialog, padding=25)
        main_d.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_d, text="🎁 NUEVA OFERTA ESPECIAL", font=("Segoe UI", 12, "bold"), fg="#27ae60").pack(pady=(0, 20))
        
        current_price = float(q[6])
        tk.Label(main_d, text=f"Precio actual: {self._format_currency(current_price)}", font=("Segoe UI", 10)).pack(anchor="w")
        
        tk.Label(main_d, text="Nuevo Descuento Adicional (%):", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(15, 5))
        discount_var = tk.StringVar(value="5")
        ent = ttk.Entry(main_d, textvariable=discount_var, font=("Segoe UI", 12))
        ent.pack(fill=tk.X)
        ent.focus_set()

        def confirm():
            try:
                extra_pct = float(discount_var.get())
                new_price = current_price * (1 - (extra_pct / 100))
                
                # Obtener datos del cliente
                client = self.db.get_client_by_id(q[8])
                if not client: return

                data = {
                    "id": quot_id,
                    "inmueble": q[2],
                    "old_price": self._format_currency(current_price, show_decimals=False),
                    "new_price": self._format_currency(new_price, show_decimals=False),
                    "fecha_ingreso": q[3].strftime("%d/%m/%Y"),
                    "fecha_egreso": q[4].strftime("%d/%m/%Y")
                }

                from utils.email_sender import send_marketing_offer_email
                if send_marketing_offer_email(client[3], f"{client[1]} {client[2]}", data):
                    self.db.mark_quotation_mkt_sent(quot_id)
                    messagebox.showinfo("Éxito", f"¡Oferta especial enviada a {client[3]}!", parent=dialog)
                    dialog.destroy()
                    self.load_quotations()
                else:
                    messagebox.showerror("Error", "No se pudo enviar el correo de marketing.", parent=dialog)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un porcentaje válido.", parent=dialog)

        ttk.Button(main_d, text="ENVIAR REGALO POR EMAIL", style="QuotAction.TButton", command=confirm).pack(fill=tk.X, pady=25)

    def select_card(self, quot_id):
        self.selected_id = quot_id
        for c in self.cards:
            is_sel = c.quot_id == quot_id
            c.configure(highlightbackground="#3498db" if is_sel else "#d1d8e0", highlightthickness=2 if is_sel else 1)
            bg_color = "#f1f9ff" if is_sel else "white"
            self._update_bg_recursive(c, bg_color)

    def _update_bg_recursive(self, widget, color):
        try:
            current_bg = str(widget.cget("background"))
            if "ebf5fb" not in current_bg and "e8f4fd" not in current_bg:
                widget.configure(bg=color)
        except: pass
        for child in widget.winfo_children():
            self._update_bg_recursive(child, color)

    def load_quotations(self):
        """Carga las cotizaciones desde la DB."""
        for w in self.scrollable.winfo_children(): w.destroy()
        self.cards = []
        self.selected_id = None
        self.search_var.set("")
        
        quotations = self.db.get_all_quotations()
        for q in quotations:
            self.create_card(q)
            
        self.lbl_stats.config(text=f"TOTAL: {len(quotations)} COTIZACIONES")
        self.filter_cards()

    def filter_cards(self):
        query = self.search_var.get().lower()
        visible_count = 0
        for card in self.cards:
            if query in card.search_data:
                card.pack(fill=tk.X, padx=5, pady=8)
                visible_count += 1
            else:
                card.pack_forget()
        self.lbl_stats.config(text=f"MOSTRANDO: {visible_count} / TOTAL: {len(self.cards)}")

    def _format_currency(self, value, show_decimals=True):
        try:
            val = float(value)
            if show_decimals:
                formatted = f"{val:,.2f}"
                m, d = formatted.split('.')
                return f"${m.replace(',', '.')},{d}"
            else:
                formatted = f"{val:,.0f}"
                return f"${formatted.replace(',', '.')}"
        except: return str(value)

    def delete_quotation(self):
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una cotización para eliminar.")
            return
            
        quot_code = f"Q-{str(self.selected_id).zfill(5)}"
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar la cotización {quot_code}?", parent=self.window):
            if self.db.delete_quotation(self.selected_id):
                self.load_quotations()

    def convert_to_reservation(self):
        """Toma los datos de la cotización y abre el formulario de reserva."""
        if not self.selected_id:
            messagebox.showwarning("Atención", "Seleccione una cotización para convertir.")
            return
            
        # Obtener datos completos de la DB
        all_q = self.db.get_all_quotations()
        q_data = next((x for x in all_q if x[0] == self.selected_id), None)
        
        if not q_data: return

        initial_data = {
            "quotation_id": self.selected_id,
            "id_cliente": q_data[8],
            "inmueble": q_data[2],
            "fecha_ingreso": q_data[3].strftime("%d/%m/%Y") if hasattr(q_data[3], 'strftime') else q_data[3],
            "fecha_egreso": q_data[4].strftime("%d/%m/%Y") if hasattr(q_data[4], 'strftime') else q_data[4],
            "descuento": str(int(q_data[12])),
            "discount_is_percentage": False, 
            "cantidad_personas": q_data[13]
        }
        
        quot_code = f"Q-{str(self.selected_id).zfill(5)}"
        if messagebox.askyesno("Convertir", f"¿Desea crear la reserva para {q_data[1]} basada en la cotización {quot_code}?", parent=self.window):
            self.window.destroy()
            self.controller.create_reservation(initial_data=initial_data)
