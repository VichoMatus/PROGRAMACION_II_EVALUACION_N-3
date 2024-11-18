from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database import engine
from models import Menu, Ingrediente, menu_ingredientes

Session = sessionmaker(bind=engine)

class MenuCRUDException(Exception):
    pass

class MenuCRUD:
    def __init__(self):
        self.conexion = Session()

    def crear_menu(self, nombre_menu: str, descripcion_menu: str, lista_ingredientes: dict):
        try:
            menu_nuevo = Menu(nombre=nombre_menu, descripcion=descripcion_menu)

            # Verificar y asociar ingredientes con cantidades requeridas
            for nombre_ingrediente, cantidad in lista_ingredientes.items():
                ingrediente = self.conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()
                if not ingrediente:
                    raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
                # Asociar el ingrediente al menú
                menu_nuevo.ingredientes.append(ingrediente)
                self.conexion.execute(menu_ingredientes.insert().values(
                    menu_id=menu_nuevo.id,
                    ingrediente_id=ingrediente.id,
                    cantidad_requerida=cantidad
                ))

            self.conexion.add(menu_nuevo)
            self.conexion.commit()
            return menu_nuevo

        except IntegrityError:
            self.conexion.rollback()
            raise MenuCRUDException("Error de integridad al crear el menú.")
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado: {e}")

    def listar_menus(self):
        try:
            menus = self.conexion.query(Menu).all()
            for menu in menus:
                print(f"ID: {menu.id}, Nombre: {menu.nombre}, Descripción: {menu.descripcion}")
                for ingrediente in menu.ingredientes:
                    print(f"  - Ingrediente: {ingrediente.nombre}, Cantidad: {ingrediente.cantidad}")
            return menus
        except Exception as e:
            raise MenuCRUDException(f"Error al listar menús: {e}")

    def buscar_menu_por_id(self, menu_id: int):
        try:
            menu = self.conexion.query(Menu).filter_by(id=menu_id).first()
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")
            return menu
        except Exception as e:
            raise MenuCRUDException(f"Error al buscar el menú: {e}")

    def actualizar_menu(self, menu_id: int, nuevo_nombre: str = None, nueva_descripcion: str = None, nuevos_ingredientes: dict = None):
        try:
            menu = self.buscar_menu_por_id(menu_id)

            if nuevo_nombre:
                menu.nombre = nuevo_nombre
            if nueva_descripcion:
                menu.descripcion = nueva_descripcion
            if nuevos_ingredientes:
                menu.ingredientes.clear()
                for nombre_ingrediente, cantidad in nuevos_ingredientes.items():
                    ingrediente = self.conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()
                    if not ingrediente:
                        raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
                    menu.ingredientes.append(ingrediente)

            self.conexion.commit()
            return menu
        except MenuCRUDException as e:
            self.conexion.rollback()
            raise e
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al actualizar el menú: {e}")

    def eliminar_menu(self, menu_id: int):
        try:
            menu = self.buscar_menu_por_id(menu_id)
            self.conexion.delete(menu)
            self.conexion.commit()
            print(f"Menú con ID {menu_id} eliminado correctamente.")
        except MenuCRUDException as e:
            self.conexion.rollback()
            raise e
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al eliminar el menú: {e}")
