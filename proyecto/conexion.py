import psycopg
from psycopg.rows import dict_row
 
# Cambia estos datos por los tuyos
HOST = "localhost"
PUERTO = 2020
BASE = "menus_db"
USUARIO = "postgres"
CLAVE = "hola"
 
 
def db():
    """Devuelve una conexión nueva a PostgreSQL (filas como diccionarios)."""
    return psycopg.connect(
        host=HOST, port=PUERTO, dbname=BASE,
        user=USUARIO, password=CLAVE, row_factory=dict_row,
    )
 
 
def init_db():
    """Crea las tablas si todavía no existen."""
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS par_impar (
            id SERIAL PRIMARY KEY,
            numero INTEGER NOT NULL,
            tipo VARCHAR(5) NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS multiplicador (
            id SERIAL PRIMARY KEY,
            numero INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS ranking (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(60) NOT NULL,
            total_intentos INTEGER NOT NULL,
            numeros_intentados TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
        );
        """)
 