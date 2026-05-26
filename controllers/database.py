import mysql.connector

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "clientes"
        self.connection = None

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
            if len(client_data) == 5:
                query = "INSERT INTO clientes (id_clientes, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s)"
            else:
                query = "INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, client_data)
            self.connection.commit()
            print("Cliente guardado exitosamente")
            return True
        except Exception as e:
            print(f"Error al guardar el cliente: {e}")
            return False

    def get_next_available_client_id(self):
        try:
            cursor = self.connection.cursor()
            # Buscar el primer ID libre (hueco) o el máximo + 1
            query = """
                SELECT MIN(t1.id_clientes + 1) AS next_id
                FROM clientes t1
                LEFT JOIN clientes t2 ON t1.id_clientes + 1 = t2.id_clientes
                WHERE t2.id_clientes IS NULL
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
            else:
                # Si la tabla está vacía, empezamos en 1
                return 1
        except Exception as e:
            print(f"Error al obtener el próximo ID disponible: {e}")
            return 1

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

    def get_all_properties(self):
        """Obtener todos los inmuebles desde la base de datos"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT id_inmueble, nombre, cantidad_personas, direccion, localidad, provincia, tipo, valor_dia, COALESCE(imagen, '') FROM inmuebles"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error al obtener los inmuebles: {e}")
            return []

    def delete_client(self, client_id):
        """Eliminar un cliente de la base de datos"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM clientes WHERE id_clientes = %s"
            cursor.execute(query, (client_id,))
            self.connection.commit()
            print("Cliente eliminado exitosamente")
            return True
        except Exception as e:
            print(f"Error al eliminar el cliente: {e}")
            return False

    def delete_property(self, property_id):
        """Eliminar un inmueble de la base de datos"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM inmuebles WHERE id_inmueble = %s"
            cursor.execute(query, (property_id,))
            self.connection.commit()
            print("Inmueble eliminado exitosamente")
            return True
        except Exception as e:
            print(f"Error al eliminar el inmueble: {e}")
            return False

    def insert_reservation(self, data):
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO reservas 
                (id_cliente, id_inmueble, fecha_ingreso, fecha_egreso, valor_dia, noches, costo_total, costo_con_descuento, adelanto, pago_pendiente, provincia)
                VALUES (%(id_cliente)s, %(id_inmueble)s, %(fecha_ingreso)s, %(fecha_egreso)s, %(valor_dia)s, %(noches)s, %(costo_total)s, %(costo_con_descuento)s, %(adelanto)s, %(pago_pendiente)s, %(provincia)s)"""
            cursor.execute(query, data)
            self.connection.commit()
            print("Reserva guardada exitosamente")
        except Exception as e:
            print(f"Error al guardar la reserva: {e}")
            raise

    def get_all_reservations(self):
        try:
            cursor = self.connection.cursor()
            query = """SELECT r.id_reserva, CONCAT(c.nombre, ' ', c.apellido), c.telefono,
                              i.nombre, r.fecha_ingreso, r.fecha_egreso, r.noches,
                              r.valor_dia, r.costo_total, r.costo_con_descuento,
                              r.adelanto, r.pago_pendiente, r.provincia
                       FROM reservas r
                       JOIN clientes c ON r.id_cliente = c.id_clientes
                       JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
                       ORDER BY r.id_reserva DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener las reservas: {e}")
            return []

    def delete_reservation(self, reservation_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (reservation_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar la reserva: {e}")
            return False

    def get_reservation_by_id(self, reservation_id):
        try:
            cursor = self.connection.cursor()
            query = """SELECT id_cliente, id_inmueble, fecha_ingreso, fecha_egreso,
                              valor_dia, noches, costo_total, costo_con_descuento,
                              adelanto, pago_pendiente, provincia
                       FROM reservas WHERE id_reserva = %s"""
            cursor.execute(query, (reservation_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener la reserva: {e}")
            return None

    def update_reservation(self, reservation_id, data):
        try:
            cursor = self.connection.cursor()
            query = """UPDATE reservas SET
                id_cliente = %(id_cliente)s, id_inmueble = %(id_inmueble)s,
                fecha_ingreso = %(fecha_ingreso)s, fecha_egreso = %(fecha_egreso)s,
                valor_dia = %(valor_dia)s, noches = %(noches)s,
                costo_total = %(costo_total)s, costo_con_descuento = %(costo_con_descuento)s,
                adelanto = %(adelanto)s, pago_pendiente = %(pago_pendiente)s,
                provincia = %(provincia)s
                WHERE id_reserva = %(id_reserva)s"""
            data["id_reserva"] = reservation_id
            cursor.execute(query, data)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar la reserva: {e}")
            return False

    def get_reserved_ranges(self, id_inmueble=None, exclude_id=None):
        try:
            cursor = self.connection.cursor()
            conditions = []
            params = []
            if id_inmueble is not None:
                conditions.append("id_inmueble = %s")
                params.append(id_inmueble)
            if exclude_id is not None:
                conditions.append("id_reserva != %s")
                params.append(exclude_id)
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"SELECT fecha_ingreso, fecha_egreso FROM reservas {where}"
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener rangos reservados: {e}")
            return []

    def get_upcoming_checkins(self, days=7):
        try:
            cursor = self.connection.cursor()
            query = """SELECT r.id_reserva, CONCAT(c.nombre, ' ', c.apellido), c.telefono,
                              r.provincia, i.nombre, r.fecha_ingreso, r.fecha_egreso
                       FROM reservas r
                       JOIN clientes c ON r.id_cliente = c.id_clientes
                       JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
                       WHERE r.fecha_ingreso BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                       ORDER BY r.fecha_ingreso"""
            cursor.execute(query, (days,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener próximos ingresos: {e}")
            return []

    def get_upcoming_checkouts(self, days=7):
        try:
            cursor = self.connection.cursor()
            query = """SELECT r.id_reserva, CONCAT(c.nombre, ' ', c.apellido), c.telefono,
                              r.provincia, i.nombre, r.fecha_ingreso, r.fecha_egreso
                       FROM reservas r
                       JOIN clientes c ON r.id_cliente = c.id_clientes
                       JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
                       WHERE r.fecha_egreso BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                       ORDER BY r.fecha_egreso"""
            cursor.execute(query, (days,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener próximos egresos: {e}")
            return []

    def get_client_by_id(self, client_id):
        if not self.connection:
            return None

        cursor = self.connection.cursor()
        query = "SELECT id_clientes, nombre, apellido, email, telefono FROM clientes WHERE id_clientes = %s"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        return result
