#Martin

from sqlalchemy.orm import Session
from models import Ingrediente  # Asegúrate de que Ingrediente esté definido en models.py
from sqlalchemy.exc import IntegrityError

class IngredienteCRUDException(Exception):
    pass

def crear_ingrediente(session: Session, nombre: str, tipo: str, cantidad: float, unidad: str):

    try:
        # Verificar si el ingrediente ya existe
        ingrediente_existente = session.query(Ingrediente).filter_by(nombre=nombre, tipo=tipo).first()
        if ingrediente_existente:
            raise IngredienteCRUDException("El ingrediente con este nombre y tipo ya existe.")
        
        # Crear un nuevo ingrediente
        nuevo_ingrediente = Ingrediente(nombre=nombre, tipo=tipo, cantidad=cantidad, unidad=unidad)
        session.add(nuevo_ingrediente)
        session.commit()
        return nuevo_ingrediente
    except IntegrityError:
        session.rollback()
        raise IngredienteCRUDException("Error al crear el ingrediente.")

def obtener_ingredientes(session: Session):
    """Obtiene todos los ingredientes registrados. """
    return session.query(Ingrediente).all()

def obtener_ingrediente_por_id(session: Session, ingrediente_id: int):
    """Obtiene un ingrediente específico por su ID. """
    return session.query(Ingrediente).filter_by(id=ingrediente_id).first()

def actualizar_ingrediente(session: Session, ingrediente_id: int, nombre: str = None, tipo: str = None, cantidad: float = None, unidad: str = None):
    """Actualiza los datos de un ingrediente."""
    ingrediente = obtener_ingrediente_por_id(session, ingrediente_id)
    if not ingrediente:
        return None  # Ingrediente no encontrado

    if nombre and tipo:
        # Verificar si el nombre y tipo ya están en uso
        ingrediente_existente = session.query(Ingrediente).filter_by(nombre=nombre, tipo=tipo).first()
        if ingrediente_existente and ingrediente_existente.id != ingrediente_id:
            raise IngredienteCRUDException("Otro ingrediente ya tiene este nombre y tipo.")
    
    if nombre:
        ingrediente.nombre = nombre
    if tipo:
        ingrediente.tipo = tipo
    if cantidad is not None:
        ingrediente.cantidad = cantidad
    if unidad:
        ingrediente.unidad = unidad
    
    session.commit()
    return ingrediente

def eliminar_ingrediente(session: Session, ingrediente_id: int):
    """Elimina un ingrediente por su ID."""
    ingrediente = obtener_ingrediente_por_id(session, ingrediente_id)
    if not ingrediente:
        return False  # Ingrediente no encontrado
    
    session.delete(ingrediente)
    session.commit()
    return True
