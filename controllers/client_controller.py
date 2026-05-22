from controllers.database import Database

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

    def get_all_clients(self):
        # Lógica para obtener todos los clientes
        db = Database()
        if db.connect():
            return db.get_all_clients()
        else:
            return []
