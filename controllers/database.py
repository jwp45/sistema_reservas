import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "sistema_reservas"

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
            print(f"Error: {err}")
            return False

    def insert_client(self, client_data):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, client_data)
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def get_next_id(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT MAX(id_clientes) FROM clientes"
            cursor.execute(query)
            result = cursor.fetchone()
            if result[0] is None:
                return 1
            else:
                return result[0] + 1
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def get_all_clients(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM clientes"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
