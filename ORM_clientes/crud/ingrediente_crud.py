from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Ingrediente, menu_ingredientes
from database import engine

class IngredienteCRUDException(Exception):
    pass

class IngredienteCRUD:
    def __init__(self):
        self.conexion = Session(bind=engine)

    def crear_ingrediente(self, nombre: str, tipo: str, unidad_medida: str, cantidad: int):
        if not nombre or len(nombre.strip()) == 0:
            raise IngredienteCRUDException("El nombre del ingrediente no puede estar vacío.")
        if cantidad is not None and cantidad < 0:
            raise IngredienteCRUDException("La cantidad no puede ser negativa.")

        try:
            if self._buscar_ingrediente_por_nombre(nombre):
                raise IngredienteCRUDException(f"El ingrediente '{nombre}' ya existe.")
            
            nuevo_ingrediente = Ingrediente(
                nombre=nombre, tipo=tipo, unidad_medida=unidad_medida, cantidad=cantidad
            )
            self.conexion.add(nuevo_ingrediente)
            self.conexion.commit()
            return nuevo_ingrediente
        except IntegrityError:
            self.conexion.rollback()
            raise IngredienteCRUDException("Error de integridad al crear el ingrediente.")
        except Exception as e:
            self.conexion.rollback()
            raise IngredienteCRUDException(f"Error inesperado: {e}")

    def listar_ingredientes(self):
        try:
            return self.conexion.query(Ingrediente).all()
        except Exception as e:
            raise IngredienteCRUDException(f"Error al listar ingredientes: {e}")

    def buscar_ingrediente_por_id(self, ingrediente_id: int):
        try:
            ingrediente = self.conexion.query(Ingrediente).filter_by(id=ingrediente_id).first()
            if not ingrediente:
                raise IngredienteCRUDException(f"Ingrediente con ID {ingrediente_id} no encontrado.")
            return ingrediente
        except Exception as e:
            raise IngredienteCRUDException(f"Error al buscar el ingrediente: {e}")

    def actualizar_ingrediente(self, ingrediente_id: int, nombre: str = None, tipo: str = None, unidad_medida: str = None, cantidad: int = None):
        if cantidad is not None and cantidad < 0:
            raise IngredienteCRUDException("La cantidad no puede ser negativa.")

        try:
            ingrediente = self.buscar_ingrediente_por_id(ingrediente_id)

            if nombre and nombre != ingrediente.nombre:
                if self._buscar_ingrediente_por_nombre(nombre):
                    raise IngredienteCRUDException(f"El ingrediente con el nombre '{nombre}' ya existe.")
                ingrediente.nombre = nombre
            if tipo:
                ingrediente.tipo = tipo
            if unidad_medida:
                ingrediente.unidad_medida = unidad_medida
            if cantidad is not None:
                ingrediente.cantidad = cantidad
            
            self.conexion.commit()
            return ingrediente
        except IngredienteCRUDException as e:
            self.conexion.rollback()
            raise e
        except Exception as e:
            self.conexion.rollback()
            raise IngredienteCRUDException(f"Error inesperado al actualizar el ingrediente: {e}")

    def eliminar_ingrediente(self, ingrediente_id: int):
        try:
            ingrediente = self.buscar_ingrediente_por_id(ingrediente_id)

            if self.conexion.query(menu_ingredientes).filter_by(ingrediente_id=ingrediente.id).first():
                raise IngredienteCRUDException(f"No se puede eliminar el ingrediente '{ingrediente.nombre}' porque está asociado a un menú.")

            self.conexion.delete(ingrediente)
            self.conexion.commit()
            return f"Ingrediente con ID {ingrediente_id} eliminado correctamente."
        except IngredienteCRUDException as e:
            self.conexion.rollback()
            raise e
        except Exception as e:
            self.conexion.rollback()
            raise IngredienteCRUDException(f"Error inesperado al eliminar el ingrediente: {e}")

    def _buscar_ingrediente_por_nombre(self, nombre: str):
        """Método interno para buscar un ingrediente por su nombre."""
        return self.conexion.query(Ingrediente).filter_by(nombre=nombre).first()

    def cerrar_sesion(self):
        """Cierra la sesión de la conexión."""
        self.conexion.close()
