from sqlalchemy.orm import Session
from database.database import get_db
from models import Cliente

# Crear un cliente
def crear_cliente(db: Session, email: str, nombre: str):
    """Crear un nuevo cliente."""
    cliente = Cliente(email=email, nombre=nombre)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente
# Leer todos los clientes
def obtener_clientes(db: Session):
    return db.query(models.Cliente).all()

# Leer un cliente por ID
def obtener_cliente_por_id(db: Session, cliente_id: int):
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

# Actualizar un cliente
def actualizar_cliente(db: Session, email: str, nombre: str = None):
    """Actualizar los datos de un cliente."""
    cliente = db.query(Cliente).filter(Cliente.email == email).first()
    if cliente:
        if nombre:
            cliente.nombre = nombre
        db.commit()
        db.refresh(cliente)
        return cliente
    return None

def eliminar_cliente(db: Session, email: str):
    """Eliminar un cliente por su correo electrónico."""
    cliente = db.query(Cliente).filter(Cliente.email == email).first()
    if cliente:
        db.delete(cliente)
        db.commit()
        return True
    return False