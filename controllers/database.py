import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "reservas_profesionales"

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            return False

    def get_next_id(self):
        if self.connect():
            cursor = self.connection.cursor()
            query = "SELECT MAX(id_clientes) FROM clientes"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            self.connection.close()
            if result[0] is None:
                return 1
            else:
                return result[0] + 1

    def insert_client(self, client_data):
        if self.connect():
            cursor = self.connection.cursor()
            query = "INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, client_data)
            self.connection.commit()
            cursor.close()
            self.connection.close()

    def get_all_clients(self):
        if self.connect():
            cursor = self.connection.cursor()
            query = "SELECT id_clientes, nombre, apellido, email, telefono FROM clientes"
            cursor.execute(query)
            clients = cursor.fetchall()
            cursor.close()
            self.connection.close()
            return clients
