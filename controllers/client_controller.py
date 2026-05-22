import mysql.connector
from controllers.database import Database

class ClientController:
    def __init__(self):
        self.db = Database()

    def get_all_clients(self):
        query = "SELECT * FROM clientes"
        result = self.db.execute_query(query)
        return result

    def execute_query(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
