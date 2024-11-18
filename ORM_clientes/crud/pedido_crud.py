from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Pedido

def crear_pedido(db: Session, descripcion: str, cliente_email: str, cantidad_menus: int):
    """Crea un nuevo pedido."""
    nuevo_pedido = Pedido(
        descripcion=descripcion,
        cliente_email=cliente_email,
        cantidad_menus=cantidad_menus,
        fecha_creacion=func.now()  # Fecha actual
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

def obtener_pedidos(db: Session):
    """Obtiene todos los pedidos de la base de datos."""
    return db.query(Pedido).all()

def obtener_pedidos_por_cliente(db: Session, cliente_email: str):
    """Obtiene todos los pedidos de un cliente específico."""
    return db.query(Pedido).filter(Pedido.cliente_email == cliente_email).all()

def actualizar_pedido(db: Session, pedido_id: int, descripcion: str = None, cantidad_menus: int = None):
    """Actualiza un pedido existente."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        return None
    if descripcion:
        pedido.descripcion = descripcion
    if cantidad_menus:
        pedido.cantidad_menus = cantidad_menus
    db.commit()
    db.refresh(pedido)
    return pedido

def eliminar_pedido(db: Session, pedido_id: int):
    """Elimina un pedido por su ID."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        db.delete(pedido)
        db.commit()
        return True
    return False

