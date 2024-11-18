# main.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from models import Base

# Crear las tablas
def inicializar_bd():
    engine = create_engine("sqlite:///restaurante.db")  # Cambia el nombre al usar otra BD
    Base.metadata.create_all(engine)
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    inicializar_bd()
