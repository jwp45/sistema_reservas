from ui.main_window import MainWindow

if __name__ == '__main__':
    app = MainWindow()
    app.setup_ui()  # Corregí el nombre del método
    app.run()

# Nota: La instalación de mysql-connector-python debe hacerse en la terminal, no dentro del script Python.
