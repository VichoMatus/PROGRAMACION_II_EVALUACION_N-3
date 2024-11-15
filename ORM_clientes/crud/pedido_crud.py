#Yadhira
from sqlalchemy.orm import Session
from models import Pedido
from datetime import datetime

def crear_pedido(db: Session, descripcion: str, total: float, cantidad_menus: int, cliente_id: int):
    nuevo_pedido = Pedido(
        descripcion=descripcion,
        total=total,
        cantidad_menus=cantidad_menus,
        fecha_creacion=datetime.now(),
        cliente_id=cliente_id
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

def obtener_pedidos(db: Session):
    return db.query(Pedido).all()

def obtener_pedidos_por_cliente(db: Session, cliente_id: int):
    return db.query(Pedido).filter(Pedido.cliente_id == cliente_id).all()

def eliminar_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        db.delete(pedido)
        db.commit()
        return True
    return False
