from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Pedido


class PedidoCRUDException(Exception):
    """Excepción personalizada para errores en PedidoCRUD."""
    pass


class PedidoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def _buscar_pedido_por_id(self, pedido_id: int):
        """Busca un pedido por su ID."""
        return self.db.query(Pedido).filter(Pedido.id == pedido_id).first()

    def _buscar_pedidos_por_cliente(self, cliente_email: str):
        """Busca pedidos por el email del cliente."""
        return self.db.query(Pedido).filter(Pedido.cliente_email == cliente_email).all()

    def crear_pedido(self, descripcion: str, cliente_email: str, cantidad_menus: int):
        """Crea un nuevo pedido."""
        if cantidad_menus <= 0:
            raise PedidoCRUDException("La cantidad de menús debe ser mayor a 0.")
        if not descripcion.strip():
            raise PedidoCRUDException("La descripción no puede estar vacía.")
        if not cliente_email.strip():
            raise PedidoCRUDException("El email del cliente no puede estar vacío.")

        try:
            nuevo_pedido = Pedido(
                descripcion=descripcion,
                cliente_email=cliente_email,
                cantidad_menus=cantidad_menus,
                fecha_creacion=func.now(),
            )
            self.db.add(nuevo_pedido)
            self.db.commit()
            self.db.refresh(nuevo_pedido)
            return nuevo_pedido
        except Exception as e:
            self.db.rollback()
            raise PedidoCRUDException(f"Error al crear el pedido: {e}")

    def obtener_pedidos(self):
        """Obtiene todos los pedidos."""
        try:
            return self.db.query(Pedido).all()
        except Exception as e:
            raise PedidoCRUDException(f"Error al obtener los pedidos: {e}")

    def obtener_pedidos_por_cliente(self, cliente_email: str):
        """Obtiene todos los pedidos de un cliente específico."""
        try:
            pedidos = self._buscar_pedidos_por_cliente(cliente_email)
            if not pedidos:
                raise PedidoCRUDException(f"No se encontraron pedidos para el cliente con email '{cliente_email}'.")
            return pedidos
        except Exception as e:
            raise PedidoCRUDException(f"Error al obtener los pedidos del cliente: {e}")

    def actualizar_pedido(self, pedido_id: int, descripcion: str = None, cantidad_menus: int = None):
        """Actualiza un pedido existente."""
        if cantidad_menus is not None and cantidad_menus <= 0:
            raise PedidoCRUDException("La cantidad de menús debe ser mayor a 0.")
        if descripcion and not descripcion.strip():
            raise PedidoCRUDException("La descripción no puede estar vacía.")

        try:
            pedido = self._buscar_pedido_por_id(pedido_id)
            if not pedido:
                raise PedidoCRUDException(f"Pedido con ID {pedido_id} no encontrado.")

            if descripcion:
                pedido.descripcion = descripcion
            if cantidad_menus is not None:
                pedido.cantidad_menus = cantidad_menus

            self.db.commit()
            self.db.refresh(pedido)
            return pedido
        except Exception as e:
            self.db.rollback()
            raise PedidoCRUDException(f"Error al actualizar el pedido: {e}")

    def eliminar_pedido(self, pedido_id: int):
        """Elimina un pedido existente."""
        try:
            pedido = self._buscar_pedido_por_id(pedido_id)
            if not pedido:
                raise PedidoCRUDException(f"Pedido con ID {pedido_id} no encontrado.")

            self.db.delete(pedido)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise PedidoCRUDException(f"Error al eliminar el pedido: {e}")
