import tkinter as tk
from tkinter import ttk

class ReservationFormWindow:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Agregar Reserva")
        self.window.geometry("450x300")

        # Frame principal del formulario
        form_frame = ttk.Frame(self.window)
        form_frame.pack(padx=10, pady=10, expand=True)

        # Campos del formulario
        self.property_label = ttk.Label(form_frame, text="Inmueble:")
        self.property_label.grid(row=0, column=0, padx=5, pady=5)

        self.property_combobox = ttk.Combobox(form_frame)
        self.property_combobox.grid(row=0, column=1, padx=5, pady=5)

        # Cargar los inmuebles disponibles
        self.load_properties()

        self.save_button = ttk.Button(form_frame, text="Guardar", command=self.save_reservation)
        self.save_button.grid(row=2, columnspan=2, pady=10)

    def load_properties(self):
        from controllers.database import Database
        db = Database()
        properties = db.get_all_properties()
        property_names = [prop[1] for prop in properties]
        self.property_combobox['values'] = property_names

    def save_reservation(self):
        selected_property = self.property_combobox.get()
        # Aquí se debería implementar la lógica para guardar la reserva en la base de datos
        print(f"Reserva guardada con inmueble: {selected_property}")
