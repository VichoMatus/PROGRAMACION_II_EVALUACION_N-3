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


    def _buscar_ingrediente_por_nombre(self, nombre_ingrediente: str):
        """Busca un ingrediente por su nombre."""
        return self.conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()

    def _buscar_menu_por_id(self, menu_id: int):
        """Busca un menú por su ID."""
        return self.conexion.query(Menu).filter_by(id=menu_id).first()


    def crear_menu(self, nombre_menu: str, descripcion_menu: str, lista_ingredientes: dict):
        """Crea un nuevo menú."""
        try:
            menu_nuevo = Menu(nombre=nombre_menu, descripcion=descripcion_menu)
            self.conexion.add(menu_nuevo)
            self.conexion.flush()  

            for nombre_ingrediente, cantidad in lista_ingredientes.items():
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
        except IntegrityError:
            self.conexion.rollback()
            raise MenuCRUDException("Error de integridad al crear el menú.")
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado: {e}")

        except IntegrityError:
            self.conexion.rollback()
            raise MenuCRUDException("Error de integridad al crear el menú.")
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado: {e}")
        
    def listar_menus(self):
        """Devuelve todos los menús con sus ingredientes."""
        try:
            menus = self.conexion.query(Menu).all()
            resultados = []
            for menu in menus:
                ingredientes = self.conexion.execute(
                    menu_ingredientes.select().where(menu_ingredientes.c.menu_id == menu.id)
                ).fetchall()
                resultados.append(
                    {
                        "id": menu.id,
                        "nombre": menu.nombre,
                        "descripcion": menu.descripcion,
                        "ingredientes": [{"id": i[1], "cantidad_requerida": i[2]} for i in ingredientes],
                    }
                )
            return resultados
        except Exception as e:
            raise MenuCRUDException(f"Error al listar menús: {e}")

    def buscar_menu_por_id(self, menu_id: int):
        try:
            menu = self._buscar_menu_por_id(menu_id)

            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")
            return menu
        except Exception as e:
            raise MenuCRUDException(f"Error al buscar el menú: {e}")

    def actualizar_menu(self, menu_id: int, nuevo_nombre: str = None, nueva_descripcion: str = None, nuevos_ingredientes: dict = None):
        """Actualiza un menú existente."""
        try:
            menu = self._buscar_menu_por_id(menu_id)
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")

            if nuevo_nombre:
                menu.nombre = nuevo_nombre
            if nueva_descripcion:
                menu.descripcion = nueva_descripcion

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


