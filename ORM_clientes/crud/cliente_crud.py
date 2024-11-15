# Nicolas

from sqlalchemy.orm import Session
from models import Cliente  
from sqlalchemy.exc import IntegrityError

class ClienteCRUDException(Exception):
    pass

def crear_cliente(session: Session, nombre: str, correo: str):
    """Crea un nuevo cliente si no existe otro con el mismo correo.
    
    Args:
        session (Session): La sesión de la base de datos.
        nombre (str): Nombre del cliente.
        correo (str): Correo único del cliente.
        
    Returns:
        Cliente: El cliente creado.
    
    Raises:
        ClienteCRUDException: Si ya existe un cliente con el mismo correo.
    """
    try:
        # Crear nuevo cliente
        nuevo_cliente = Cliente(nombre=nombre, correo=correo)
        session.add(nuevo_cliente)
        session.commit()
        return nuevo_cliente
    except IntegrityError:
        session.rollback()
        raise ClienteCRUDException("El cliente con este correo ya existe.")

def obtener_clientes(session: Session):
    """Obtiene todos los clientes registrados.
    
    Args:
        session (Session): La sesión de la base de datos.
        
    Returns:
        list: Lista de todos los clientes.
    """
    return session.query(Cliente).all()

def obtener_cliente_por_id(session: Session, cliente_id: int):
    """Obtiene un cliente específico por su ID.
    
    Args:
        session (Session): La sesión de la base de datos.
        cliente_id (int): ID del cliente.
        
    Returns:
        Cliente or None: El cliente si existe, de lo contrario None.
    """
    return session.query(Cliente).filter_by(id=cliente_id).first()

def actualizar_cliente(session: Session, cliente_id: int, nombre: str = None, correo: str = None):
    """Actualiza los datos de un cliente.
    
    Args:
        session (Session): La sesión de la base de datos.
        cliente_id (int): ID del cliente a actualizar.
        nombre (str, opcional): Nuevo nombre del cliente.
        correo (str, opcional): Nuevo correo del cliente.
        
    Returns:
        Cliente or None: El cliente actualizado, o None si no se encontró.
        
    Raises:
        ClienteCRUDException: Si el correo ya está en uso por otro cliente.
    """
    cliente = obtener_cliente_por_id(session, cliente_id)
    if not cliente:
        return None  # Cliente no encontrado
    
    if nombre:
        cliente.nombre = nombre
    
    if correo and correo != cliente.correo:
        # Verificar si el correo está en uso
        correo_existente = session.query(Cliente).filter_by(correo=correo).first()
        if correo_existente:
            raise ClienteCRUDException("Otro cliente ya tiene este correo.")
        cliente.correo = correo
    
    session.commit()
    return cliente

def eliminar_cliente(session: Session, cliente_id: int):
    """Elimina un cliente por su ID.
    
    Args:
        session (Session): La sesión de la base de datos.
        cliente_id (int): ID del cliente a eliminar.
        
    Returns:
        bool: True si se eliminó correctamente, False si no se encontró el cliente.
    """
    cliente = obtener_cliente_por_id(session, cliente_id)
    if not cliente:
        return False  # Cliente no encontrado
    
    session.delete(cliente)
    session.commit()
    return True
