-- Estructura de la base de datos para el proyecto de alquileres

CREATE TABLE clientes (
  id_clientes INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre VARCHAR(20) NOT NULL,
  apellido VARCHAR(20) NOT NULL,
  email VARCHAR(30) NOT NULL,
  telefono INTEGER NOT NULL
);

CREATE TABLE inmuebles (
  id_inmueble INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre VARCHAR(30) NOT NULL,
  cantidad_personas INTEGER NOT NULL,
  direccion VARCHAR(30) NOT NULL,
  localidad VARCHAR(30) NOT NULL,
  provincia VARCHAR(30) NOT NULL,
  tipo VARCHAR(30) NOT NULL,
  valor_dia INTEGER NOT NULL
);
