import os
from database import Base, engine  # Reutilizar configuración existente en database.py

def inicializar_bd():
    """Inicializa la base de datos y crea las tablas necesarias."""
    try:
        Base.metadata.create_all(engine)
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    inicializar_bd()
