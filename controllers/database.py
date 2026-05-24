import sqlite3

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "clientes"

    def connect(self):
        return sqlite3.connect(self.database)

    def insert_client(self, client_data):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (?, ?, ?, ?)", client_data)
        conn.commit()
        conn.close()

    def get_next_id(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id_clientes) FROM clientes")
        last_id = cursor.fetchone()[0]
        conn.close()
        return last_id + 1 if last_id else 1

    def get_all_clients(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        clients = cursor.fetchall()
        conn.close()
        return clients

    def get_all_properties(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inmuebles")
        properties = cursor.fetchall()
        conn.close()
        return properties

    def delete_client(self, client_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_clientes = ?", (client_id,))
        conn.commit()
        conn.close()

    def delete_property(self, property_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inmuebles WHERE id_inmueble = ?", (property_id,))
        conn.commit()
        conn.close()

    def get_client_by_id(self, client_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id_clientes = ?", (client_id,))
        client = cursor.fetchone()
        conn.close()
        return client
