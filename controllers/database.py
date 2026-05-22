import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "reservas"

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

    def cursor(self):
        if self.connection.is_connected():
            return self.connection.cursor()
        else:
            raise Exception("No se ha establecido una conexión a la base de datos")

    def execute_query(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
