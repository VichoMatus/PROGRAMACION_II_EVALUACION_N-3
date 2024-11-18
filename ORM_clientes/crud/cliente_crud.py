from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Cliente

class ClienteCRUDException(Exception):
    pass

class ClienteCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_cliente(self, email: str, nombre: str):
        try:
            # Verificar si ya existe un cliente con el mismo correo electrónico
            if self.db.query(Cliente).filter_by(email=email).first():
                raise ClienteCRUDException(f"El cliente con email '{email}' ya existe.")
            
            cliente = Cliente(email=email, nombre=nombre)
            self.db.add(cliente)
            self.db.commit()
            self.db.refresh(cliente)
            return cliente
        except IntegrityError:
            self.db.rollback()
            raise ClienteCRUDException("Error de integridad al crear el cliente.")
        except Exception as e:
            self.db.rollback()
            raise ClienteCRUDException(f"Error inesperado: {e}")

    def obtener_clientes(self):
        try:
            return self.db.query(Cliente).all()
        except Exception as e:
            raise ClienteCRUDException(f"Error al obtener los clientes: {e}")

    def obtener_cliente_por_id(self, cliente_id: int):
        try:
            cliente = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
            if not cliente:
                raise ClienteCRUDException(f"Cliente con ID {cliente_id} no encontrado.")
            return cliente
        except Exception as e:
            raise ClienteCRUDException(f"Error al buscar el cliente: {e}")

    def actualizar_cliente(self, email: str, nombre: str = None):
        try:
            cliente = self.db.query(Cliente).filter(Cliente.email == email).first()
            if not cliente:
                raise ClienteCRUDException(f"Cliente con email '{email}' no encontrado.")
            
            if nombre:
                cliente.nombre = nombre
            
            self.db.commit()
            self.db.refresh(cliente)
            return cliente
        except ClienteCRUDException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise ClienteCRUDException(f"Error inesperado al actualizar el cliente: {e}")

    def eliminar_cliente(self, email: str):
        try:
            cliente = self.db.query(Cliente).filter(Cliente.email == email).first()
            if not cliente:
                raise ClienteCRUDException(f"Cliente con email '{email}' no encontrado.")
            
            self.db.delete(cliente)
            self.db.commit()
            return True
        except ClienteCRUDException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise ClienteCRUDException(f"Error inesperado al eliminar el cliente: {e}")
