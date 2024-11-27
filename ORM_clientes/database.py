from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración del motor y la sesión
DATABASE_URL = 'sqlite:///gestion_clientes_y_pedidos.db'
engine = create_engine(DATABASE_URL, echo=True)  # 'echo=True' para logs SQL opcionales
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa
Base = declarative_base()

# Función para obtener la sesión de base de datos
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
