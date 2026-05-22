class ClientController:
    def __init__(self):
        pass

    def create_client(self, client_data):
        # Lógica para crear un nuevo cliente
        db = Database()
        if db.connect():
            db.insert_client(client_data)
        else:
            print("No se pudo conectar a la base de datos")
