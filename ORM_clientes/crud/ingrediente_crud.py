from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Ingrediente, menu_ingredientes
from database import engine

Session = Session(bind=engine)
conexion = Session()

class IngredienteCRUDException(Exception):
    pass

def crear_ingrediente(nombre: str, tipo: str, unidad_medida: str, cantidad: int):

    try:
        if conexion.query(Ingrediente).filter_by(nombre=nombre).first():
            raise IngredienteCRUDException(f"El ingrediente '{nombre}' ya existe.")
        
        nuevo_ingrediente = Ingrediente(nombre=nombre, tipo=tipo, unidad_medida=unidad_medida, cantidad=cantidad)
        conexion.add(nuevo_ingrediente)
        conexion.commit()
        return nuevo_ingrediente

    except IntegrityError:
        conexion.rollback()
        raise IngredienteCRUDException("Error de integridad al crear el ingrediente.")
    except Exception as e:
        conexion.rollback()
        raise IngredienteCRUDException(f"Error inesperado: {e}")

def listar_ingredientes():

    try:
        ingredientes = conexion.query(Ingrediente).all()
        for ingrediente in ingredientes:
            print(f"ID: {ingrediente.id}, Nombre: {ingrediente.nombre}, Tipo: {ingrediente.tipo}, Cantidad: {ingrediente.cantidad}, Unidad: {ingrediente.unidad_medida}")
        return ingredientes

    except Exception as e:
        raise IngredienteCRUDException(f"Error al listar ingredientes: {e}")

def buscar_ingrediente_por_id(ingrediente_id: int):

    try:
        ingrediente = conexion.query(Ingrediente).filter_by(id=ingrediente_id).first()
        if not ingrediente:
            raise IngredienteCRUDException(f"Ingrediente con ID {ingrediente_id} no encontrado.")
        return ingrediente

    except Exception as e:
        raise IngredienteCRUDException(f"Error al buscar el ingrediente: {e}")

def actualizar_ingrediente(ingrediente_id: int, nombre: str = None, tipo: str = None, unidad_medida: str = None, cantidad: int = None):

    try:
        ingrediente = buscar_ingrediente_por_id(ingrediente_id)

        if nombre:
            if conexion.query(Ingrediente).filter_by(nombre=nombre).first() and nombre != ingrediente.nombre:
                raise IngredienteCRUDException(f"El ingrediente con el nombre '{nombre}' ya existe.")
            ingrediente.nombre = nombre
        if tipo:
            ingrediente.tipo = tipo
        if unidad_medida:
            ingrediente.unidad_medida = unidad_medida
        if cantidad is not None:
            ingrediente.cantidad = cantidad
        
        conexion.commit()
        return ingrediente

    except IngredienteCRUDException as e:
        conexion.rollback()
        raise e
    except Exception as e:
        conexion.rollback()
        raise IngredienteCRUDException(f"Error inesperado al actualizar el ingrediente: {e}")

def eliminar_ingrediente(ingrediente_id: int):

    try:
        ingrediente = buscar_ingrediente_por_id(ingrediente_id)

        if conexion.query(menu_ingredientes).filter_by(ingrediente_id=ingrediente.id).first():
            raise IngredienteCRUDException(f"No se puede eliminar el ingrediente '{ingrediente.nombre}' porque está asociado a un menú.")

        conexion.delete(ingrediente)
        conexion.commit()
        print(f"Ingrediente con ID {ingrediente_id} eliminado correctamente.")

    except IngredienteCRUDException as e:
        conexion.rollback()
        raise e
    except Exception as e:
        conexion.rollback()
        raise IngredienteCRUDException(f"Error inesperado al eliminar el ingrediente: {e}")
