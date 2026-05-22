import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "clientes"

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Conexión exitosa a la base de datos")
                return True
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def insert_client(self, client_data):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, client_data)
            self.connection.commit()
            print("Cliente guardado exitosamente")
        except Exception as e:
            print(f"Error al guardar el cliente: {e}")

    def get_next_id(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'clientes' AND TABLE_NAME = 'clientes'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error al obtener el próximo ID: {e}")
            return None

    def get_all_clients(self):
        """Obtener todos los clientes desde la base de datos"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT id_clientes, nombre, apellido, email, telefono FROM clientes"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error al obtener los clientes: {e}")
            return []
