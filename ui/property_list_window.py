import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os

from controllers.database import Database
from controllers.property_controller import PropertyController
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "inmuebles")


class EditPropertyWindow:
    def __init__(self, master, property_id, property_list_window):
        self.master = master
        self.property_id = property_id
        self.property_list_window = property_list_window
        self.imagen_path = ""

        self.window = tk.Toplevel(master)
        self.window.title("Editar Inmueble")
        self.window.geometry("600x750")
        self.window.configure(bg="#f8f9fa")
        self.window.transient(master)

        # Estilos locales
        style = ttk.Style(self.window)
        style.configure("EditHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("EditSection.TLabelframe", font=("Segoe UI", 10, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_scroll_container = ttk.Frame(self.window)
        main_scroll_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_scroll_container, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=20)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=560)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(scrollable_frame, text=f"Editando Inmueble #{property_id}", style="EditHeader.TLabel").pack(pady=(0, 20))

        # --- SECCIÓN 1: DATOS BÁSICOS ---
        sec_info = ttk.LabelFrame(scrollable_frame, text=" Información General ", padding=15, style="EditSection.TLabelframe")
        sec_info.pack(fill=tk.X, pady=10)
        sec_info.columnconfigure(1, weight=1)

        self.fields = {
            "nombre": tk.StringVar(),
            "cantidad_personas": tk.StringVar(),
            "direccion": tk.StringVar(),
            "localidad": tk.StringVar(),
            "provincia": tk.StringVar(),
            "tipo": tk.StringVar(),
            "valor_dia": tk.StringVar()
        }

        fields_order = [
            ("Nombre:", "nombre"),
            ("Tipo:", "tipo"),
            ("Capacidad:", "cantidad_personas"),
            ("Dirección:", "direccion"),
            ("Localidad:", "localidad"),
            ("Provincia:", "provincia"),
            ("Valor por Día:", "valor_dia")
        ]

        for i, (label_text, field_name) in enumerate(fields_order):
            ttk.Label(sec_info, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            ent = ttk.Entry(sec_info, textvariable=self.fields[field_name])
            ent.grid(row=i, column=1, sticky=tk.EW, pady=8)
            if field_name == "valor_dia":
                ent.bind("<KeyRelease>", self._format_currency_input)

        # --- SECCIÓN 2: IMAGEN ---
        sec_img = ttk.LabelFrame(scrollable_frame, text=" Multimedia ", padding=15, style="EditSection.TLabelframe")
        sec_img.pack(fill=tk.X, pady=10)

        btn_row = ttk.Frame(sec_img)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Seleccionar Nueva Imagen", command=self.select_image).pack(side=tk.LEFT, padx=5)
        self.lbl_img_name = ttk.Label(btn_row, text="Sin cambios", foreground="gray", font=("Segoe UI", 9))
        self.lbl_img_name.pack(side=tk.LEFT, padx=5)

        self.img_preview = ttk.Label(sec_img, background="#ecf0f1", relief=tk.RIDGE)
        self.img_preview.pack(pady=15)

        self.load_property_data()

        # Botones de Acción
        btn_frame = ttk.Frame(scrollable_frame, padding=(0, 20, 0, 0))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="CANCELAR", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="GUARDAR CAMBIOS", style="Action.TButton", command=self.save_changes).pack(side=tk.RIGHT, padx=5)

    def _format_currency_input(self, event):
        text = self.fields["valor_dia"].get()
        cleaned = ''.join(filter(lambda char: char.isdigit(), text))
        if cleaned:
            val = float(cleaned)
            formatted = f"{val:,.0f}".replace(',', '.')
            self.fields["valor_dia"].set(f"${formatted}")
        else:
            self.fields["valor_dia"].set("")

    def _format_currency(self, value):
        try:
            val = float(value)
            formatted = f"{val:,.2f}"
            m, d = formatted.split('.')
            return f"${m.replace(',', '.')},{d}"
        except: return str(value)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            self.imagen_path = path
            self.lbl_img_name.config(text=os.path.basename(path), foreground="black")
            try:
                img = Image.open(path)
                img.thumbnail((250, 180))
                tk_img = ImageTk.PhotoImage(img)
                self.img_preview.config(image=tk_img)
                self.img_preview.image = tk_img
            except Exception as e:
                print(f"Error al cargar imagen: {e}")

    def load_property_data(self):
        db = Database()
        if db.connect():
            query = "SELECT nombre, cantidad_personas, direccion, localidad, provincia, tipo, valor_dia, COALESCE(imagen, '') FROM inmuebles WHERE id_inmueble = %s"
            cursor = db.connection.cursor()
            cursor.execute(query, (self.property_id,))
            result = cursor.fetchone()
            if result:
                self.fields["nombre"].set(result[0])
                self.fields["cantidad_personas"].set(result[1])
                self.fields["direccion"].set(result[2])
                self.fields["localidad"].set(result[3])
                self.fields["provincia"].set(result[4])
                self.fields["tipo"].set(result[5])
                self.fields["valor_dia"].set(self._format_currency(result[6]))
                
                img_path = result[7]
                if img_path and os.path.exists(img_path):
                    self.imagen_path = img_path
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((250, 180))
                        tk_img = ImageTk.PhotoImage(img)
                        self.img_preview.config(image=tk_img)
                        self.img_preview.image = tk_img
                    except: pass
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def save_changes(self):
        if not all(v.get() for v in self.fields.values()):
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        # Limpiar formato de moneda para guardar
        valor_raw = self.fields["valor_dia"].get().replace('$', '').replace('.', '').replace(',', '.')
        try:
            valor_dia = float(valor_raw)
        except:
            messagebox.showerror("Error", "Valor por día inválido")
            return

        property_data = (
            self.fields["nombre"].get(),
            self.fields["cantidad_personas"].get(),
            self.fields["direccion"].get(),
            self.fields["localidad"].get(),
            self.fields["provincia"].get(),
            self.fields["tipo"].get(),
            valor_dia
        )

        db = Database()
        if db.connect():
            cursor = db.connection.cursor()
            query = "UPDATE inmuebles SET nombre=%s, cantidad_personas=%s, direccion=%s, localidad=%s, provincia=%s, tipo=%s, valor_dia=%s WHERE id_inmueble=%s"
            cursor.execute(query, property_data + (self.property_id,))

            if self.imagen_path and not self.imagen_path.startswith(ASSETS_DIR):
                ext = os.path.splitext(self.imagen_path)[1]
                dest = os.path.join(ASSETS_DIR, f"{self.property_id}{ext}")
                try:
                    shutil.copy2(self.imagen_path, dest)
                    cursor.execute("UPDATE inmuebles SET imagen = %s WHERE id_inmueble = %s", (dest, self.property_id))
                except Exception as e:
                    print(f"Error al copiar imagen: {e}")

            db.connection.commit()
            cursor.close()
            messagebox.showinfo("Éxito", "Inmueble actualizado exitosamente", parent=self.window)
            self.window.destroy()
            self.property_list_window.refresh_properties()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos", parent=self.window)


class PropertyListWindow:
    def __init__(self, master):
        self.master = master
        self.cards = []
        self.images = []
        self.selected_id = None

        self.window = tk.Toplevel(master)
        self.window.title("Gestión de Inmuebles")
        self.window.geometry("1100x800")
        self.window.configure(bg="#f8f9fa")

        # Estilos
        style = ttk.Style(self.window)
        style.configure("Dashboard.TFrame", background="#f8f9fa")
        style.configure("Card.TFrame", background="white", relief="ridge", borderwidth=1)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#2c3e50", background="#f8f9fa")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        main_container = ttk.Frame(self.window, padding=25, style="Dashboard.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- CABECERA ---
        header_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text="Catálogo de Inmuebles", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.lbl_stats = ttk.Label(header_frame, text="Cargando catálogo...", font=("Segoe UI", 10), foreground="#7f8c8d", background="#f8f9fa")
        self.lbl_stats.pack(side=tk.LEFT, padx=20, pady=(10, 0))

        # --- BARRA DE FILTROS ---
        filter_card = ttk.Frame(main_container, padding=15, style="Card.TFrame")
        filter_card.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(filter_card, text="BUSCAR:", font=("Segoe UI", 9, "bold"), background="white").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_card, textvariable=self.search_var, font=("Segoe UI", 10), width=35)
        search_entry.pack(side=tk.LEFT, padx=(0, 20))
        search_entry.bind("<KeyRelease>", lambda e: self.filter_cards())

        ttk.Label(filter_card, text="TIPO:", font=("Segoe UI", 9, "bold"), background="white").pack(side=tk.LEFT, padx=(0, 10))
        self.type_filter = ttk.Combobox(filter_card, values=["Todos", "Casa", "Departamento", "Cabaña", "Habitación"], state="readonly", width=18)
        self.type_filter.set("Todos")
        self.type_filter.pack(side=tk.LEFT, padx=(0, 20))
        self.type_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_cards())

        ttk.Button(filter_card, text="Refrescar", command=self.load_properties).pack(side=tk.RIGHT, padx=5)

        # --- CONTENEDOR DE TARJETAS ---
        canvas_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable = ttk.Frame(self.canvas, style="Dashboard.TFrame")

        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw", width=1020)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- BARRA DE ACCIONES ---
        btn_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="ELIMINAR SELECCIONADO", command=self.delete_property).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="EDITAR DETALLES", style="Action.TButton", command=self.edit_property).pack(side=tk.RIGHT)

        self.db = Database()
        self.load_properties()

    def bind_select(self, widget, id_inmueble):
        widget.bind("<Button-1>", lambda e, i=id_inmueble: self.select_card(i))
        for child in widget.winfo_children():
            self.bind_select(child, id_inmueble)

    def create_card(self, prop):
        id_inmueble, nombre, capacidad, direccion, localidad, provincia, tipo, valor_dia, img_path = prop

        card = tk.Frame(self.scrollable, bg="white", bd=0, highlightbackground="#d1d8e0", highlightthickness=1)
        card.pack(fill=tk.X, padx=5, pady=8)
        self.bind_select(card, id_inmueble)
        card.bind("<Double-Button-1>", lambda e, i=id_inmueble: self.edit_property_by_id(i))

        inner = tk.Frame(card, bg="white", padx=15, pady=15)
        inner.pack(fill=tk.X)
        self.bind_select(inner, id_inmueble)

        # Imagen
        img_container = tk.Frame(inner, width=180, height=120, bg="#f1f2f6")
        img_container.pack_propagate(False)
        img_container.pack(side=tk.LEFT)
        self.bind_select(img_container, id_inmueble)

        img_label = tk.Label(img_container, text="Sin imagen", bg="#f1f2f6", fg="#a4b0be", font=("Segoe UI", 9))
        img_label.pack(fill=tk.BOTH, expand=True)
        self.bind_select(img_label, id_inmueble)

        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((180, 120))
                tk_img = ImageTk.PhotoImage(img)
                img_label.config(image=tk_img, text="")
                self.images.append(tk_img)
            except: pass

        # Info Central
        info_frame = tk.Frame(inner, bg="white", padx=25)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bind_select(info_frame, id_inmueble)

        tk.Label(info_frame, text=nombre.upper(), font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(anchor="w")
        
        type_tag = tk.Frame(info_frame, bg="#e8f4fd", padx=8, pady=2)
        type_tag.pack(anchor="w", pady=5)
        tk.Label(type_tag, text=tipo, font=("Segoe UI", 9, "bold"), bg="#e8f4fd", fg="#3498db").pack()
        
        tk.Label(info_frame, text=f"👥 Capacidad: {capacidad} personas", font=("Segoe UI", 10), bg="white", fg="#7f8c8d").pack(anchor="w")
        
        loc_text = f"📍 {direccion}, {localidad} ({provincia})"
        tk.Label(info_frame, text=loc_text, font=("Segoe UI", 9), bg="white", fg="#57606f").pack(anchor="w", pady=(5, 0))

        # Precio y ID
        price_frame = tk.Frame(inner, bg="white", padx=10)
        price_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.bind_select(price_frame, id_inmueble)

        tk.Label(price_frame, text=f"ID #{id_inmueble}", font=("Segoe UI", 8, "bold"), bg="white", fg="#dfe4ea").pack(anchor="e")
        
        try:
            val = float(valor_dia)
            formatted = f"{val:,.2f}"
            m, d = formatted.split('.')
            valor_fmt = f"${m.replace(',', '.')},{d}"
        except: valor_fmt = str(valor_dia)

        tk.Label(price_frame, text=valor_fmt, font=("Segoe UI", 16, "bold"), bg="white", fg="#27ae60").pack(anchor="e", pady=(15, 0))
        tk.Label(price_frame, text="POR NOCHE", font=("Segoe UI", 8, "bold"), bg="white", fg="#a4b0be").pack(anchor="e")

        card.id_inmueble = id_inmueble
        card.search_data = f"{nombre} {tipo} {direccion} {localidad} {provincia}".lower()
        card.tipo = tipo.lower()
        self.cards.append(card)

    def filter_cards(self):
        query = self.search_var.get().lower()
        tipo_sel = self.type_filter.get().lower()

        visible_count = 0
        for card in self.cards:
            match_query = query in card.search_data or query in str(card.id_inmueble)
            match_type = tipo_sel == "todos" or tipo_sel in card.tipo
            
            if match_query and match_type:
                card.pack(fill=tk.X, padx=5, pady=8)
                visible_count += 1
            else:
                card.pack_forget()
        
        self.lbl_stats.config(text=f"Mostrando: {visible_count} de {len(self.cards)} inmuebles")

    def select_card(self, id_inmueble):
        self.selected_id = id_inmueble
        for c in self.cards:
            if hasattr(c, 'id_inmueble') and c.id_inmueble == id_inmueble:
                c.configure(highlightbackground="#3498db", highlightthickness=2)
                for w in c.winfo_children(): # inner
                    w.configure(bg="#f1f9ff")
                    for sub in w.winfo_children():
                        try: sub.configure(bg="#f1f9ff")
                        except: pass
                        if isinstance(sub, tk.Frame):
                            for g in sub.winfo_children():
                                # No cambiar el fondo de los tags de tipo
                                if "e8f4fd" not in str(sub.cget("background")):
                                    try: g.configure(bg="#f1f9ff")
                                    except: pass
            else:
                c.configure(highlightbackground="#d1d8e0", highlightthickness=1)
                for w in c.winfo_children():
                    w.configure(bg="white")
                    for sub in w.winfo_children():
                        try: sub.configure(bg="white")
                        except: pass
                        if isinstance(sub, tk.Frame):
                            for g in sub.winfo_children():
                                if "e8f4fd" not in str(sub.cget("background")):
                                    try: g.configure(bg="white")
                                    except: pass

    def load_properties(self):
        for w in self.scrollable.winfo_children():
            w.destroy()
        self.cards = []
        self.images = []
        
        if not self.db.connect():
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        props = self.db.get_all_properties()
        for prop in props:
            self.create_card(prop)
        self.lbl_stats.config(text=f"Total: {len(props)} inmuebles")
        self.filter_cards()

    def edit_property_by_id(self, id_inmueble):
        EditPropertyWindow(self.master, id_inmueble, self)

    def delete_property(self):
        pid = self.get_selected_id()
        if pid is None: return
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el inmueble #{pid}?"):
            pc = PropertyController()
            if pc.delete_property(pid):
                messagebox.showinfo("Éxito", "Inmueble eliminado correctamente")
                self.load_properties()
            else:
                messagebox.showerror("Error", "No se pudo eliminar")

    def edit_property(self):
        pid = self.get_selected_id()
        if pid is None: return
        self.edit_property_by_id(pid)

    def refresh_properties(self):
        self.selected_id = None
        self.load_properties()

    def get_selected_id(self):
        if self.selected_id: return self.selected_id
        messagebox.showwarning("Advertencia", "Seleccione un inmueble")
        return None

    def show(self):
        pass
