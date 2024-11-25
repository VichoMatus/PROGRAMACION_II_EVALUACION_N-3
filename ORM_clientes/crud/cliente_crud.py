from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Cliente
from database import get_session

class ClienteCRUDException(Exception):
    pass

class ClienteCRUD:
    def __init__(self, db: Session):
        self.db = db


    def _buscar_cliente_por_email(self, email: str):
        return self.db.query(Cliente).filter(Cliente.email == email).first()

    def _validar_datos_cliente(self, email: str, nombre: str):
        if not email or "@" not in email:
            raise ClienteCRUDException("El email proporcionado no es válido.")
        if not nombre or len(nombre.strip()) == 0:
            raise ClienteCRUDException("El nombre no puede estar vacío.")

    def crear_cliente(self, email: str, nombre: str):
        self._validar_datos_cliente(email, nombre)
        try:
            if self._buscar_cliente_por_email(email):


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

    def actualizar_cliente(self, email_actual: str, nuevo_nombre: str = None, nuevo_email: str = None):
        if nuevo_nombre and len(nuevo_nombre.strip()) == 0:
            raise ClienteCRUDException("El nombre no puede estar vacío.")
        if nuevo_email and "@" not in nuevo_email:
            raise ClienteCRUDException("El email proporcionado no es válido.")
        
        try:
            cliente = self._buscar_cliente_por_email(email_actual)
            if not cliente:
                raise ClienteCRUDException(f"Cliente con email '{email_actual}' no encontrado.")

            # Validar nuevo email si es diferente al actual
            if nuevo_email and nuevo_email != email_actual:
                if self._buscar_cliente_por_email(nuevo_email):
                    raise ClienteCRUDException(f"El email '{nuevo_email}' ya está registrado.")

            if nuevo_nombre:
                cliente.nombre = nuevo_nombre
            if nuevo_email:
                cliente.email = nuevo_email

            
            self.db.commit()
            self.db.refresh(cliente)
            return cliente

        except Exception as e:
            self.db.rollback()
            raise ClienteCRUDException(f"Error al actualizar el cliente: {e}")

    def eliminar_cliente(self, email: str):
        try:
            cliente = self._buscar_cliente_por_email(email)

            if not cliente:
                raise ClienteCRUDException(f"Cliente con email '{email}' no encontrado.")
            
            self.db.delete(cliente)
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise ClienteCRUDException(f"Error al eliminar el cliente: {e}")

    def buscar_clientes_por_nombre(self, nombre: str):
        try:
            return self.db.query(Cliente).filter(Cliente.nombre.ilike(f"%{nombre}%")).all()
        except Exception as e:
            raise ClienteCRUDException(f"Error al buscar clientes por nombre: {e}")
        
        
    def obtener_correos_clientes(self):
        """Obtiene los correos de los clientes desde la base de datos."""
        with next(get_session()) as db:
            clientes = ClienteCRUD(db).obtener_clientes()
            correos = [cliente.email for cliente in clientes]  # Obtener solo los correos
        return correos

    def obtener_cliente_por_email(self, email):
        """Obtiene un cliente por su correo electrónico."""
        return self.db.query(Cliente).filter(Cliente.email == email).first()

