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
        self.window.geometry("500x550")

        form_frame = ttk.Frame(self.window)
        form_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        ttk.Label(form_frame, text="Ingrese los datos del inmueble", font=('Arial', 14)).pack(pady=5)

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
            ("Cantidad:", "cantidad_personas"),
            ("Dirección:", "direccion"),
            ("Localidad:", "localidad"),
            ("Provincia:", "provincia"),
            ("Tipo:", "tipo"),
            ("Valor por Día:", "valor_dia")
        ]

        for label_text, field_name in fields_order:
            row = ttk.Frame(form_frame)
            row.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(row, text=label_text, width=15).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=self.fields[field_name]).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Imagen
        img_frame = ttk.LabelFrame(form_frame, text="Imagen", padding=5)
        img_frame.pack(fill=tk.X, padx=5, pady=5)

        btn_row = ttk.Frame(img_frame)
        btn_row.pack(fill=tk.X, pady=2)
        ttk.Button(btn_row, text="Seleccionar Imagen", command=self.select_image).pack(side=tk.LEFT, padx=5)
        self.lbl_img_name = ttk.Label(btn_row, text="", foreground="gray")
        self.lbl_img_name.pack(side=tk.LEFT, padx=5)

        self.img_preview = ttk.Label(img_frame)
        self.img_preview.pack(pady=5)

        self.load_property_data()

        ttk.Button(form_frame, text="Guardar Cambios", command=self.save_changes, style="TButton").pack(pady=10, side=tk.BOTTOM)

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
                img.thumbnail((200, 150))
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
                try:
                    valor = float(result[6])
                    self.fields["valor_dia"].set(f"{valor:,.0f}".replace(",", "."))
                except (ValueError, TypeError):
                    self.fields["valor_dia"].set(result[6])
                img_path = result[7]
                if img_path and os.path.exists(img_path):
                    self.imagen_path = img_path
                    self.lbl_img_name.config(text=os.path.basename(img_path), foreground="black")
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((200, 150))
                        tk_img = ImageTk.PhotoImage(img)
                        self.img_preview.config(image=tk_img)
                        self.img_preview.image = tk_img
                    except Exception as e:
                        print(f"Error al cargar imagen: {e}")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    def save_changes(self):
        if not all(v.get() for v in self.fields.values()):
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.window)
            return

        valor_dia_clean = self.fields["valor_dia"].get().replace(".", "")
        property_data = (
            self.fields["nombre"].get(),
            self.fields["cantidad_personas"].get(),
            self.fields["direccion"].get(),
            self.fields["localidad"].get(),
            self.fields["provincia"].get(),
            self.fields["tipo"].get(),
            valor_dia_clean
        )

        db = Database()
        if db.connect():
            cursor = db.connection.cursor()
            query = "UPDATE inmuebles SET nombre=%s, cantidad_personas=%s, direccion=%s, localidad=%s, provincia=%s, tipo=%s, valor_dia=%s WHERE id_inmueble=%s"
            cursor.execute(query, property_data + (self.property_id,))

            if self.imagen_path:
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
        self.window.title("Lista de Inmuebles")
        self.window.geometry("850x600")

        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(top_frame, text="Buscar", command=self.filter_cards).pack(side=tk.RIGHT, padx=5)

        canvas_frame = ttk.Frame(self.window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable = ttk.Frame(self.canvas)

        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Editar Inmueble", command=self.edit_property).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar Inmueble", command=self.delete_property).pack(side=tk.LEFT, padx=5)

        self.db = Database()
        self.load_properties()

    def clear_cards(self):
        for w in self.scrollable.winfo_children():
            w.destroy()
        self.cards = []
        self.images = []

    def load_properties(self):
        self.clear_cards()
        if not self.db.connect():
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        for prop in self.db.get_all_properties():
            self.create_card(prop)
        if self.search_var.get():
            self.filter_cards()

    def bind_select(self, widget, id_inmueble):
        widget.bind("<Button-1>", lambda e, i=id_inmueble: self.select_card(i))
        for child in widget.winfo_children():
            self.bind_select(child, id_inmueble)

    def create_card(self, prop):
        id_inmueble, nombre, capacidad, direccion, localidad, provincia, tipo, valor_dia, img_path = prop

        card = tk.Frame(self.scrollable, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=10)
        card.pack(fill=tk.X, padx=5, pady=5)
        self.bind_select(card, id_inmueble)
        card.bind("<Double-Button-1>", lambda e, i=id_inmueble: self.edit_property_by_id(i))

        inner = ttk.Frame(card)
        inner.pack(fill=tk.X)

        img_label = ttk.Label(inner, text="Sin imagen", anchor="center")
        img_label.pack(side=tk.LEFT, padx=(0, 10))

        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((120, 90))
                tk_img = ImageTk.PhotoImage(img)
                img_label.config(image=tk_img, text="")
                self.images.append(tk_img)
            except Exception:
                pass

        data_frame = ttk.Frame(inner)
        data_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        try:
            valor_fmt = f"${float(valor_dia):,.2f}"
        except (ValueError, TypeError):
            valor_fmt = valor_dia

        ttk.Label(data_frame, text=nombre, font=('Arial', 13, 'bold')).pack(anchor="w")
        ttk.Label(data_frame, text=f"{tipo} | {capacidad} pers. | {direccion}, {localidad}, {provincia}",
                  font=('Arial', 9), foreground="gray").pack(anchor="w")
        ttk.Label(data_frame, text=f"Valor por día: {valor_fmt}",
                  font=('Arial', 10), foreground="#2e7d32").pack(anchor="w")

        card.id_inmueble = id_inmueble
        self.cards.append(card)

    def select_card(self, id_inmueble):
        self.selected_id = id_inmueble
        for c in self.cards:
            if hasattr(c, 'id_inmueble') and c.id_inmueble == id_inmueble:
                c.configure(bg="#e3f2fd")
            else:
                c.configure(bg="white")

    def get_selected_id(self):
        if self.selected_id is not None:
            return self.selected_id
        messagebox.showwarning("Advertencia", "Seleccione un inmueble")
        return None

    def filter_cards(self):
        text = self.search_var.get().lower()
        all_labels = []
        for card in self.cards:
            labels = []
            for w in card.winfo_children():
                for sub in w.winfo_children():
                    try:
                        t = sub.cget("text").lower()
                        labels.append(t)
                    except:
                        pass
            card.pack_forget()
            if any(text in lbl for lbl in labels) or text in str(card.id_inmueble):
                card.pack(fill=tk.X, padx=5, pady=5)

    def edit_property_by_id(self, id_inmueble):
        EditPropertyWindow(self.master, id_inmueble, self)

    def delete_property(self):
        pid = self.get_selected_id()
        if pid is None:
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este inmueble?"):
            pc = PropertyController()
            if pc.delete_property(pid):
                messagebox.showinfo("Éxito", "Inmueble eliminado correctamente")
                self.refresh_properties()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inmueble")

    def edit_property(self):
        pid = self.get_selected_id()
        if pid is None:
            return
        EditPropertyWindow(self.master, pid, self)

    def refresh_properties(self):
        self.selected_id = None
        self.load_properties()

    def show(self):
        self.window.mainloop()
