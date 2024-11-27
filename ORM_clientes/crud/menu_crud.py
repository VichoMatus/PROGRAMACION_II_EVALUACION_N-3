from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database import engine
from models import Menu, Ingrediente, menu_ingredientes

Session = sessionmaker(bind=engine)

class MenuCRUDException(Exception):
    pass

class MenuCRUD:
    def __init__(self, conexion=None):
        self.conexion = conexion or Session()

    def _buscar_ingrediente_por_nombre(self, nombre_ingrediente: str):
        """Busca un ingrediente por su nombre."""
        return self.conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()

    def _buscar_menu_por_id(self, menu_id: int):
        """Busca un menú por su ID."""
        return self.conexion.query(Menu).filter_by(id=menu_id).first()

    def crear_menu(self, nombre: str, descripcion: str, ingredientes: dict, precio: float):
        """Crea un nuevo menú con los ingredientes asociados."""
        try:
            # Crear el menú principal
            menu_nuevo = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
            self.conexion.add(menu_nuevo)
            self.conexion.flush()  # Asegura que el menú tiene un ID antes de asociar los ingredientes

            # Asociar ingredientes al menú
            for nombre_ingrediente, cantidad in ingredientes.items():
                if cantidad <= 0:
                    raise MenuCRUDException(f"La cantidad para '{nombre_ingrediente}' debe ser mayor a cero.")
                ingrediente = self._buscar_ingrediente_por_nombre(nombre_ingrediente)
                if not ingrediente:
                    raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")

                self.conexion.execute(menu_ingredientes.insert().values(
                    menu_id=menu_nuevo.id,
                    ingrediente_id=ingrediente.id,
                    cantidad_requerida=cantidad
                ))

            self.conexion.commit()
            return menu_nuevo
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado: {e}")

    def listar_menus(self):
        """Devuelve todos los menús con sus ingredientes asociados."""
        try:
            menus = self.conexion.query(Menu).all()
            resultados = []
            for menu in menus:
                # Recuperar los ingredientes asociados al menú
                ingredientes = self.conexion.execute(
                    menu_ingredientes.select().where(menu_ingredientes.c.menu_id == menu.id)
                ).fetchall()
                ingredientes_detalle = [
                    {
                        "id": ingrediente[1],  # ID del ingrediente
                        "cantidad_requerida": ingrediente[2]  # Cantidad requerida
                    }
                    for ingrediente in ingredientes
                ]
                resultados.append({
                    "id": menu.id,
                    "nombre": menu.nombre,
                    "descripcion": menu.descripcion,
                    "precio": menu.precio,
                    "ingredientes": ingredientes_detalle
                })
            return resultados
        except Exception as e:
            raise MenuCRUDException(f"Error al listar menús: {e}")

    def actualizar_menu(self, menu_id: int, nuevo_nombre: str = None, nueva_descripcion: str = None, nuevos_ingredientes: dict = None, nuevo_precio: float = None):
        """Actualiza un menú existente."""
        try:
            menu = self._buscar_menu_por_id(menu_id)
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")

            if nuevo_nombre:
                menu.nombre = nuevo_nombre
            if nueva_descripcion:
                menu.descripcion = nueva_descripcion
            if nuevo_precio is not None:
                menu.precio = nuevo_precio

            if nuevos_ingredientes:
                # Eliminar relaciones existentes
                self.conexion.execute(menu_ingredientes.delete().where(menu_ingredientes.c.menu_id == menu_id))

                # Agregar nuevas relaciones
                for nombre_ingrediente, cantidad in nuevos_ingredientes.items():
                    if cantidad <= 0:
                        raise MenuCRUDException(f"La cantidad para '{nombre_ingrediente}' debe ser mayor a cero.")
                    ingrediente = self._buscar_ingrediente_por_nombre(nombre_ingrediente)
                    if not ingrediente:
                        raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")

                    self.conexion.execute(menu_ingredientes.insert().values(
                        menu_id=menu.id,
                        ingrediente_id=ingrediente.id,
                        cantidad_requerida=cantidad
                    ))

            self.conexion.commit()
            return menu
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al actualizar el menú: {e}")

    def eliminar_menu(self, menu_id: int):
        """Elimina un menú y sus relaciones con ingredientes."""
        try:
            self.conexion.execute(menu_ingredientes.delete().where(menu_ingredientes.c.menu_id == menu_id))
            menu = self._buscar_menu_por_id(menu_id)
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")
            self.conexion.delete(menu)
            self.conexion.commit()
            return f"Menú con ID {menu_id} eliminado correctamente."
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al eliminar el menú: {e}")
