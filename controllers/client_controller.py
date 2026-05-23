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

    def delete_client(self, client_id):
        """Eliminar un cliente de la base de datos"""
        db = Database()
        if db.connect():
            return db.delete_client(client_id)
        else:
            print("No se pudo conectar a la base de datos")
            return False
