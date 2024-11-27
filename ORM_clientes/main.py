import logging
from database import Base, engine

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def verificar_conexion():
    """
    Verifica si la conexión al motor de base de datos es válida.
    """
    try:
        with engine.connect() as connection:
            logging.info("Conexión al motor de base de datos exitosa.")
    except Exception as e:
        logging.error(f"Error al conectar con el motor de base de datos: {e}")
        raise

def crear_tablas():
    """
    Crea las tablas necesarias en la base de datos.
    """
    try:
        Base.metadata.create_all(engine)
        logging.info("Tablas creadas correctamente (si no existían).")
    except Exception as e:
        logging.error(f"Error al crear tablas: {e}")
        raise

def inicializar_bd():
    """
    Inicializa la base de datos y crea las tablas necesarias.
    """
    try:
        logging.info("Iniciando inicialización de la base de datos...")
        verificar_conexion()
        crear_tablas()
        logging.info("Base de datos inicializada correctamente.")
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    inicializar_bd()
