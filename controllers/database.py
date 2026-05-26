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
                self._init_db()
                return True
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def _init_db(self):
        """Inicializa las tablas necesarias si no existen y sincroniza datos."""
        try:
            cursor = self.connection.cursor()
            
            # 0. Asegurar que la columna 'documento' existe en 'clientes'
            try:
                cursor.execute("ALTER TABLE clientes ADD COLUMN documento VARCHAR(20) AFTER id_clientes")
                self.connection.commit()
            except:
                pass # Probablemente ya existe
            
            # 1. Crear tabla de historial de pagos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_pagos (
                    id_pago INT AUTO_INCREMENT PRIMARY KEY,
                    id_reserva INT NOT NULL,
                    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
                    monto DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva) ON DELETE CASCADE
                )
            """)
            
            # 2. Sincronización inicial: 
            # Si una reserva tiene adelanto pero no tiene registros en historial_pagos,
            # creamos un registro inicial usando la fecha de ingreso (o curdate si es pasada)
            sync_query = """
                INSERT INTO historial_pagos (id_reserva, monto, fecha_pago)
                SELECT id_reserva, adelanto, CURDATE()
                FROM reservas
                WHERE adelanto > 0 
                AND id_reserva NOT IN (SELECT DISTINCT id_reserva FROM historial_pagos)
            """
            cursor.execute(sync_query)
            
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")

    def insert_client(self, client_data):
        try:
            cursor = self.connection.cursor()
            if len(client_data) == 6:
                query = "INSERT INTO clientes (id_clientes, documento, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s, %s)"
            else:
                query = "INSERT INTO clientes (documento, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s)"
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
            query = "SELECT id_clientes, documento, nombre, apellido, email, telefono FROM clientes"
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
            reservation_id = cursor.lastrowid
            
            # Registrar el primer pago si hay adelanto
            adelanto = float(data.get("adelanto", 0))
            if adelanto > 0:
                cursor.execute("INSERT INTO historial_pagos (id_reserva, monto) VALUES (%s, %s)", (reservation_id, adelanto))
            
            self.connection.commit()
            print(f"Reserva #{reservation_id} guardada exitosamente")
            return reservation_id
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
                conditions.append("r.id_inmueble = %s")
                params.append(id_inmueble)
            if exclude_id is not None:
                conditions.append("r.id_reserva != %s")
                params.append(exclude_id)
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"""SELECT r.fecha_ingreso, r.fecha_egreso, CONCAT(c.nombre, ' ', c.apellido) as cliente 
                       FROM reservas r
                       JOIN clientes c ON r.id_cliente = c.id_clientes
                       {where}"""
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
        query = "SELECT id_clientes, nombre, apellido, email, telefono, documento FROM clientes WHERE id_clientes = %s"
        cursor.execute(query, (client_id,))
        result = cursor.fetchone()
        cursor.close()

        return result

    # --- NUEVOS MÉTODOS FINANCIEROS ---

    def get_financial_summary(self):
        """Retorna totales generales: Potencial, Cobrado, Pendiente."""
        try:
            cursor = self.connection.cursor()
            query = """SELECT 
                        SUM(costo_con_descuento) as total_potencial, 
                        SUM(adelanto) as total_cobrado, 
                        SUM(pago_pendiente) as total_pendiente 
                       FROM reservas"""
            cursor.execute(query)
            result = cursor.fetchone()
            # Manejar caso de tabla vacía (sumas nulas)
            return [float(x) if x is not None else 0.0 for x in result]
        except Exception as e:
            print(f"Error en get_financial_summary: {e}")
            return [0.0, 0.0, 0.0]

    def get_revenue_by_month(self):
        """Retorna ingresos agrupados por mes (usando fecha de ingreso)."""
        try:
            cursor = self.connection.cursor()
            query = """SELECT 
                        DATE_FORMAT(fecha_ingreso, '%Y-%m') as mes,
                        SUM(costo_con_descuento) as total
                       FROM reservas
                       GROUP BY mes
                       ORDER BY mes DESC
                       LIMIT 12"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en get_revenue_by_month: {e}")
            return []

    def get_revenue_by_property(self):
        """Retorna ingresos agrupados por inmueble."""
        try:
            cursor = self.connection.cursor()
            query = """SELECT 
                        i.nombre,
                        SUM(r.costo_con_descuento) as total
                       FROM reservas r
                       JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
                       GROUP BY i.nombre
                       ORDER BY total DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en get_revenue_by_property: {e}")
            return []

    def get_pending_payments_list(self):
        """Lista detallada de deudores (reservas con saldo pendiente)."""
        try:
            cursor = self.connection.cursor()
            query = """SELECT 
                        r.id_reserva,
                        CONCAT(c.nombre, ' ', c.apellido) as cliente,
                        i.nombre as inmueble,
                        r.fecha_ingreso,
                        r.pago_pendiente
                       FROM reservas r
                       JOIN clientes c ON r.id_cliente = c.id_clientes
                       JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
                       WHERE r.pago_pendiente > 0
                       ORDER BY r.fecha_ingreso ASC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en get_pending_payments_list: {e}")
            return []

    def add_payment_to_reservation(self, reservation_id, amount):
        """Añade un pago (abono) a una reserva existente y actualiza el saldo pendiente."""
        try:
            cursor = self.connection.cursor()
            # 1. Obtener valores actuales
            query_get = "SELECT adelanto, pago_pendiente FROM reservas WHERE id_reserva = %s"
            cursor.execute(query_get, (reservation_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "No se encontró la reserva."
            
            actual_adelanto = float(result[0])
            actual_pendiente = float(result[1])
            
            if amount > actual_pendiente:
                return False, f"El monto (${amount:,.2f}) supera el saldo pendiente (${actual_pendiente:,.2f})."
            
            # 2. Calcular nuevos valores
            nuevo_adelanto = actual_adelanto + amount
            nuevo_pendiente = actual_pendiente - amount
            
            # 3. Registrar en Historial
            cursor.execute("INSERT INTO historial_pagos (id_reserva, monto) VALUES (%s, %s)", (reservation_id, amount))
            
            # 4. Actualizar Reserva
            query_upd = "UPDATE reservas SET adelanto = %s, pago_pendiente = %s WHERE id_reserva = %s"
            cursor.execute(query_upd, (nuevo_adelanto, nuevo_pendiente, reservation_id))
            
            self.connection.commit()
            return True, "Pago registrado con éxito e ingresado al historial."
            
        except Exception as e:
            print(f"Error en add_payment_to_reservation: {e}")
            return False, f"Error en la base de datos: {str(e)}"

    def get_payment_history(self, reservation_id):
        """Retorna el historial de abonos de una reserva."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT fecha_pago, monto FROM historial_pagos WHERE id_reserva = %s ORDER BY fecha_pago DESC"
            cursor.execute(query, (reservation_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en get_payment_history: {e}")
            return []
