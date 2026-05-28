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
            # Usar cursor buffered para evitar errores de resultados no leídos
            cursor = self.connection.cursor(buffered=True)
            
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

            # 2. Crear tabla de cotizaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cotizaciones (
                    id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT NOT NULL,
                    id_inmueble INT NOT NULL,
                    fecha_ingreso DATE NOT NULL,
                    fecha_egreso DATE NOT NULL,
                    noches INT NOT NULL,
                    valor_dia DECIMAL(10, 2) NOT NULL,
                    costo_total DECIMAL(10, 2) NOT NULL,
                    descuento DECIMAL(10, 2) DEFAULT 0,
                    costo_con_descuento DECIMAL(10, 2) NOT NULL,
                    fecha_cotizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    mkt_enviado TINYINT(1) DEFAULT 0,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id_clientes) ON DELETE CASCADE,
                    FOREIGN KEY (id_inmueble) REFERENCES inmuebles(id_inmueble) ON DELETE CASCADE
                )
            """)
            
            # Asegurar que la columna existe por si la tabla ya fue creada
            try:
                cursor.execute("ALTER TABLE cotizaciones ADD COLUMN mkt_enviado TINYINT(1) DEFAULT 0")
                self.connection.commit()
            except: pass
            
            # 3. Crear tabla de configuración
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    id INT PRIMARY KEY DEFAULT 1,
                    smtp_server VARCHAR(255),
                    smtp_port INT,
                    smtp_user VARCHAR(255),
                    smtp_password VARCHAR(255),
                    from_email VARCHAR(255),
                    business_name VARCHAR(255),
                    whatsapp_number VARCHAR(50),
                    logo_path VARCHAR(255),
                    CHECK (id = 1)
                )
            """)
            
            # 5. Crear tabla de servicios de inmuebles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servicios_inmuebles (
                    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
                    id_inmueble INT NOT NULL,
                    nombre_servicio VARCHAR(100) NOT NULL,
                    icono VARCHAR(50) DEFAULT '✨',
                    FOREIGN KEY (id_inmueble) REFERENCES inmuebles(id_inmueble) ON DELETE CASCADE
                )
            """)
            
            # 6. Crear tabla de galería de inmuebles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS galeria_inmuebles (
                    id_imagen INT AUTO_INCREMENT PRIMARY KEY,
                    id_inmueble INT NOT NULL,
                    ruta_imagen VARCHAR(255) NOT NULL,
                    FOREIGN KEY (id_inmueble) REFERENCES inmuebles(id_inmueble) ON DELETE CASCADE
                )
            """)
            
            # Asegurar que la columna icono existe
            try:
                cursor.execute("ALTER TABLE servicios_inmuebles ADD COLUMN icono VARCHAR(50) DEFAULT '✨'")
                self.connection.commit()
            except: pass
            
            # Asegurar que la columna existe por si la tabla ya fue creada
            try:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN logo_path VARCHAR(255)")
                self.connection.commit()
            except: pass
            
            # Insertar valores por defecto si no existen
            cursor.execute("SELECT COUNT(*) FROM configuracion")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO configuracion (id, smtp_server, smtp_port, smtp_user, smtp_password, from_email, business_name, whatsapp_number, logo_path)
                    VALUES (1, 'smtp.gmail.com', 587, 'wolf10dra@gmail.com', 'xsyy xbcl rkoq esud', 'wolf10dra@gmail.com', 'Sistema de Reservas', '5492236689548', '')
                """)

            # Asegurar columnas de detalle en inmuebles
            try:
                cursor.execute("ALTER TABLE inmuebles ADD COLUMN dormitorios INT DEFAULT 0")
                cursor.execute("ALTER TABLE inmuebles ADD COLUMN camas INT DEFAULT 0")
                cursor.execute("ALTER TABLE inmuebles ADD COLUMN baños INT DEFAULT 0")
                self.connection.commit()
            except: pass

            # 4. Sincronización inicial
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

    def get_config(self):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            query = "SELECT * FROM configuracion WHERE id = 1"
            cursor.execute(query)
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener configuración: {e}")
            return None
        finally:
            if cursor: cursor.close()

    def update_config(self, data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """UPDATE configuracion SET 
                       smtp_server = %(smtp_server)s,
                       smtp_port = %(smtp_port)s,
                       smtp_user = %(smtp_user)s,
                       smtp_password = %(smtp_password)s,
                       from_email = %(from_email)s,
                       business_name = %(business_name)s,
                       whatsapp_number = %(whatsapp_number)s,
                       logo_path = %(logo_path)s
                       WHERE id = 1"""
            cursor.execute(query, data)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar configuración: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def insert_client(self, client_data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            if len(client_data) == 6:
                query = "INSERT INTO clientes (id_clientes, documento, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s, %s)"
            else:
                query = "INSERT INTO clientes (documento, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, client_data)
            client_id = cursor.lastrowid
            self.connection.commit()
            print(f"Cliente guardado exitosamente con ID: {client_id}")
            return client_id
        except Exception as e:
            print(f"Error al guardar the cliente: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def get_next_available_client_id(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
                return 1
        except Exception as e:
            print(f"Error al obtener el próximo ID disponible: {e}")
            return 1
        finally:
            if cursor: cursor.close()

    def get_all_clients(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT id_clientes, documento, nombre, apellido, email, telefono FROM clientes"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error al obtener los clientes: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def get_all_properties(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """SELECT id_inmueble, nombre, cantidad_personas, direccion, localidad, 
                              provincia, tipo, valor_dia, COALESCE(imagen, ''),
                              dormitorios, camas, baños 
                       FROM inmuebles"""
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error al obtener los inmuebles: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def get_property_services(self, id_inmueble):
        """Retorna la lista de servicios de un inmueble (icono, nombre)."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT icono, nombre_servicio FROM servicios_inmuebles WHERE id_inmueble = %s"
            cursor.execute(query, (id_inmueble,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener servicios del inmueble: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def insert_property_services(self, id_inmueble, servicios_con_iconos):
        """Guarda una lista de servicios (icono, nombre) para un inmueble."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            # Primero eliminamos los existentes
            cursor.execute("DELETE FROM servicios_inmuebles WHERE id_inmueble = %s", (id_inmueble,))
            
            if servicios_con_iconos:
                query = "INSERT INTO servicios_inmuebles (id_inmueble, icono, nombre_servicio) VALUES (%s, %s, %s)"
                data = [(id_inmueble, s[0], s[1]) for s in servicios_con_iconos if s[1].strip()]
                cursor.executemany(query, data)
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al guardar servicios del inmueble: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def delete_client(self, client_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "DELETE FROM clientes WHERE id_clientes = %s"
            cursor.execute(query, (client_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar el cliente: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def get_gallery_images(self, id_inmueble):
        """Retorna las rutas de las imágenes de la galería de un inmueble."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT id_imagen, ruta_imagen FROM galeria_inmuebles WHERE id_inmueble = %s"
            cursor.execute(query, (id_inmueble,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener galería del inmueble: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def insert_gallery_image(self, id_inmueble, ruta_imagen):
        """Guarda una imagen en la galería de un inmueble."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "INSERT INTO galeria_inmuebles (id_inmueble, ruta_imagen) VALUES (%s, %s)"
            cursor.execute(query, (id_inmueble, ruta_imagen))
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al guardar imagen en galería: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def delete_gallery_image(self, id_imagen):
        """Elimina una imagen de la galería."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "DELETE FROM galeria_inmuebles WHERE id_imagen = %s"
            cursor.execute(query, (id_imagen,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar imagen de galería: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def update_client(self, client_id, client_data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """UPDATE clientes SET 
                       documento = %s, nombre = %s, apellido = %s, 
                       email = %s, telefono = %s 
                       WHERE id_clientes = %s"""
            cursor.execute(query, (*client_data, client_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar el cliente: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def delete_property(self, property_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "DELETE FROM inmuebles WHERE id_inmueble = %s"
            cursor.execute(query, (property_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar el inmueble: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def insert_reservation(self, data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """INSERT INTO reservas 
                (id_cliente, id_inmueble, fecha_ingreso, fecha_egreso, valor_dia, noches, costo_total, costo_con_descuento, adelanto, pago_pendiente, provincia)
                VALUES (%(id_cliente)s, %(id_inmueble)s, %(fecha_ingreso)s, %(fecha_egreso)s, %(valor_dia)s, %(noches)s, %(costo_total)s, %(costo_con_descuento)s, %(adelanto)s, %(pago_pendiente)s, %(provincia)s)"""
            cursor.execute(query, data)
            reservation_id = cursor.lastrowid

            adelanto = float(data.get("adelanto", 0))
            if adelanto > 0:
                cursor.execute("INSERT INTO historial_pagos (id_reserva, monto) VALUES (%s, %s)", (reservation_id, adelanto))

            self.connection.commit()
            return reservation_id

        except Exception as e:
            print(f"Error al guardar la reserva: {e}")
            raise
        finally:
            if cursor: cursor.close()

    def get_all_reservations(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def delete_reservation(self, reservation_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (reservation_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar la reserva: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def get_reservation_by_id(self, reservation_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """SELECT id_cliente, id_inmueble, fecha_ingreso, fecha_egreso,
                              valor_dia, noches, costo_total, costo_con_descuento,
                              adelanto, pago_pendiente, provincia
                       FROM reservas WHERE id_reserva = %s"""
            cursor.execute(query, (reservation_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener la reserva: {e}")
            return None
        finally:
            if cursor: cursor.close()

    def update_reservation(self, reservation_id, data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def get_reserved_ranges(self, id_inmueble=None, exclude_id=None):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def is_range_available(self, id_inmueble, start_date, end_date, exclude_res_id=None):
        """Verifica si un rango de fechas está libre para un inmueble."""
        ranges = self.get_reserved_ranges(id_inmueble=id_inmueble, exclude_id=exclude_res_id)
        from datetime import date
        # Convertir a objetos date si vienen como string ISO
        if isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            from datetime import datetime
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        for r_start, r_end, _ in ranges:
            # r_start/r_end suelen venir como objetos date de MySQL
            if (start_date < r_end) and (end_date > r_start):
                return False
        return True

    def get_upcoming_checkins(self, days=7):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def get_upcoming_checkouts(self, days=7):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def get_client_by_id(self, client_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT id_clientes, nombre, apellido, email, telefono, documento FROM clientes WHERE id_clientes = %s"
            cursor.execute(query, (client_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener el cliente: {e}")
            return None
        finally:
            if cursor: cursor.close()

    def get_client_by_email(self, email):
        """Retorna los datos del cliente si el email ya existe."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT id_clientes, documento, nombre, apellido, email, telefono FROM clientes WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener cliente por email: {e}")
            return None
        finally:
            if cursor: cursor.close()

    def get_financial_summary(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """SELECT 
                        SUM(costo_con_descuento) as total_potencial, 
                        SUM(adelanto) as total_cobrado, 
                        SUM(pago_pendiente) as total_pendiente 
                       FROM reservas"""
            cursor.execute(query)
            result = cursor.fetchone()
            return [float(x) if x is not None else 0.0 for x in result]
        except Exception as e:
            print(f"Error en get_financial_summary: {e}")
            return [0.0, 0.0, 0.0]
        finally:
            if cursor: cursor.close()

    def search_clients(self, query):
        """Busca clientes por nombre, apellido, documento o email."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            sql = """SELECT id_clientes, documento, nombre, apellido, email, telefono 
                     FROM clientes 
                     WHERE nombre LIKE %s OR apellido LIKE %s OR email LIKE %s OR documento LIKE %s
                     LIMIT 10"""
            q = f"%{query}%"
            cursor.execute(sql, (q, q, q, q))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def get_revenue_by_month(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def get_revenue_by_property(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def get_pending_payments_list(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
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
        finally:
            if cursor: cursor.close()

    def add_payment_to_reservation(self, reservation_id, amount):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query_get = "SELECT adelanto, pago_pendiente FROM reservas WHERE id_reserva = %s"
            cursor.execute(query_get, (reservation_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "No se encontró la reserva."
            
            actual_adelanto = float(result[0])
            actual_pendiente = float(result[1])
            
            if amount > actual_pendiente:
                return False, f"El monto (${amount:,.2f}) supera el saldo pendiente (${actual_pendiente:,.2f})."
            
            nuevo_adelanto = actual_adelanto + amount
            nuevo_pendiente = actual_pendiente - amount
            
            cursor.execute("INSERT INTO historial_pagos (id_reserva, monto) VALUES (%s, %s)", (reservation_id, amount))
            
            query_upd = "UPDATE reservas SET adelanto = %s, pago_pendiente = %s WHERE id_reserva = %s"
            cursor.execute(query_upd, (nuevo_adelanto, nuevo_pendiente, reservation_id))
            
            self.connection.commit()
            return True, "Pago registrado con éxito e ingresado al historial."
            
        except Exception as e:
            print(f"Error en add_payment_to_reservation: {e}")
            return False, f"Error en la base de datos: {str(e)}"
        finally:
            if cursor: cursor.close()

    def get_payment_history(self, reservation_id):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT fecha_pago, monto FROM historial_pagos WHERE id_reserva = %s ORDER BY fecha_pago DESC"
            cursor.execute(query, (reservation_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en get_payment_history: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def insert_quotation(self, data):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """INSERT INTO cotizaciones 
                (id_cliente, id_inmueble, fecha_ingreso, fecha_egreso, noches, valor_dia, costo_total, descuento, costo_con_descuento)
                VALUES (%(id_cliente)s, %(id_inmueble)s, %(fecha_ingreso)s, %(fecha_egreso)s, %(noches)s, %(valor_dia)s, %(costo_total)s, %(descuento)s, %(costo_con_descuento)s)"""
            cursor.execute(query, data)
            quot_id = cursor.lastrowid
            self.connection.commit()
            return quot_id
        except Exception as e:
            print(f"Error al guardar la cotización: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def get_all_quotations(self):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """SELECT q.id_cotizacion, CONCAT(c.nombre, ' ', c.apellido) as cliente,
                              i.nombre as inmueble, q.fecha_ingreso, q.fecha_egreso, 
                              q.noches, q.costo_con_descuento, q.fecha_cotizacion,
                              q.id_cliente, q.id_inmueble, q.valor_dia, q.costo_total, q.descuento,
                              i.cantidad_personas, q.mkt_enviado
                       FROM cotizaciones q
                       JOIN clientes c ON q.id_cliente = c.id_clientes
                       JOIN inmuebles i ON q.id_inmueble = i.id_inmueble
                       ORDER BY q.fecha_cotizacion DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener cotizaciones: {e}")
            return []
        finally:
            if cursor: cursor.close()

    def mark_quotation_mkt_sent(self, id_cotizacion):
        """Marca una cotización indicando que ya se envió una oferta de marketing."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute("UPDATE cotizaciones SET mkt_enviado = 1 WHERE id_cotizacion = %s", (id_cotizacion,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al marcar mkt_enviado: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def delete_quotation(self, id_cotizacion):
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute("DELETE FROM cotizaciones WHERE id_cotizacion = %s", (id_cotizacion,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar cotización: {e}")
            return False
        finally:
            if cursor: cursor.close()

    def cleanup_old_quotations(self, hours=72):
        """Elimina cotizaciones que superen el tiempo de validez."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "DELETE FROM cotizaciones WHERE fecha_cotizacion < DATE_SUB(NOW(), INTERVAL %s HOUR)"
            cursor.execute(query, (hours,))
            count = cursor.rowcount
            self.connection.commit()
            if count > 0:
                print(f"Limpieza: Se eliminaron {count} cotizaciones vencidas (> {hours}hs).")
            return count
        except Exception as e:
            print(f"Error al limpiar cotizaciones: {e}")
            return 0
        finally:
            if cursor: cursor.close()

    def get_quotations_expiring_soon(self, hours=48):
        """Retorna el conteo de cotizaciones que vencen en las próximas X horas."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            # Validez de 15 días = 360 horas. 
            # Vence pronto si: (fecha_cotizacion + 360h) está entre NOW y (NOW + hours)
            query = """SELECT COUNT(*) FROM cotizaciones 
                       WHERE DATE_ADD(fecha_cotizacion, INTERVAL 360 HOUR) 
                       BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s HOUR)"""
            cursor.execute(query, (hours,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error en get_quotations_expiring_soon: {e}")
            return 0
        finally:
            if cursor: cursor.close()

    def get_today_occupancy_stats(self):
        """Retorna el total de inmuebles y cuántos están ocupados hoy."""
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=True)
            # Total inmuebles
            cursor.execute("SELECT COUNT(*) FROM inmuebles")
            total = cursor.fetchone()[0]
            
            # Ocupados hoy (fecha actual entre ingreso y egreso)
            cursor.execute("""SELECT COUNT(DISTINCT id_inmueble) FROM reservas 
                            WHERE CURDATE() >= fecha_ingreso AND CURDATE() < fecha_egreso""")
            occupied = cursor.fetchone()[0]
            
            return occupied, total
        except Exception as e:
            print(f"Error en get_today_occupancy_stats: {e}")
            return 0, 0
        finally:
            if cursor: cursor.close()
