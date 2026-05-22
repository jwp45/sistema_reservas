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
            query = "INSERT INTO clientes (id_clientes, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, client_data)
            self.connection.commit()
            print("Cliente guardado exitosamente")
        except Exception as e:
            print(f"Error al guardar el cliente: {e}")
