from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database import engine
from models import Menu, Ingrediente, menu_ingredientes
import logging

Session = sessionmaker(bind=engine)

class MenuCRUDException(Exception):
    """Excepción personalizada para errores de MenuCRUD."""
    pass

class MenuCRUD:
    def __init__(self):
        self.conexion = Session()
        logging.info("Sesión iniciada para MenuCRUD.")

    def _buscar_ingrediente_por_nombre(self, nombre_ingrediente: str):
        """Busca un ingrediente por su nombre."""
        if not nombre_ingrediente.strip():
            raise MenuCRUDException("El nombre del ingrediente no puede estar vacío.")
        return self.conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()

    def _buscar_menu_por_id(self, menu_id: int):
        """Busca un menú por su ID."""
        return self.conexion.query(Menu).filter_by(id=menu_id).first()

    def crear_menu(self, nombre_menu: str, descripcion_menu: str, lista_ingredientes: dict, precio: float):
        """Crea un nuevo menú."""
        try:
            if precio <= 0:
                raise MenuCRUDException("El precio del menú debe ser mayor a cero.")
            
            menu_nuevo = Menu(nombre=nombre_menu, descripcion=descripcion_menu, precio=precio)

            for nombre_ingrediente, cantidad in lista_ingredientes.items():
                if cantidad <= 0:
                    raise MenuCRUDException(f"La cantidad para '{nombre_ingrediente}' debe ser mayor a cero.")
                ingrediente = self._buscar_ingrediente_por_nombre(nombre_ingrediente)
                if not ingrediente:
                    raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
                
                menu_nuevo.ingredientes.append(ingrediente)
                self.conexion.execute(menu_ingredientes.insert().values(
                    menu_id=menu_nuevo.id,
                    ingrediente_id=ingrediente.id,
                    cantidad_requerida=cantidad
                ))

            self.conexion.add(menu_nuevo)
            self.conexion.commit()
            logging.info(f"Menú '{nombre_menu}' creado exitosamente.")
            return menu_nuevo

        except IntegrityError:
            self.conexion.rollback()
            raise MenuCRUDException("Error de integridad al crear el menú.")
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado: {e}")

    def listar_menus(self):
        """Lista todos los menús con sus descripciones, precios y detalles de ingredientes."""
        try:
            menus = self.conexion.query(Menu).all()
            menus_detallados = []
            for menu in menus:
                ingredientes = ", ".join([f"{i.nombre} ({i.cantidad})" for i in menu.ingredientes])
                menus_detallados.append({
                    "id": menu.id,
                    "nombre": menu.nombre,
                    "descripcion": menu.descripcion,
                    "precio": menu.precio,
                    "ingredientes": ingredientes
                })
            logging.info("Menús listados correctamente.")
            return menus_detallados
        except Exception as e:
            raise MenuCRUDException(f"Error al listar menús: {e}")

    def buscar_menu_por_id(self, menu_id: int):
        """Busca un menú por su ID."""
        try:
            menu = self._buscar_menu_por_id(menu_id)
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")
            return menu
        except Exception as e:
            raise MenuCRUDException(f"Error al buscar el menú: {e}")

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
            if nuevo_precio:
                if nuevo_precio <= 0:
                    raise MenuCRUDException("El precio del menú debe ser mayor a cero.")
                menu.precio = nuevo_precio
            if nuevos_ingredientes:
                menu.ingredientes.clear()
                for nombre_ingrediente, cantidad in nuevos_ingredientes.items():
                    if cantidad <= 0:
                        raise MenuCRUDException(f"La cantidad para '{nombre_ingrediente}' debe ser mayor a cero.")
                    ingrediente = self._buscar_ingrediente_por_nombre(nombre_ingrediente)
                    if not ingrediente:
                        raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
                    menu.ingredientes.append(ingrediente)

            self.conexion.commit()
            logging.info(f"Menú con ID {menu_id} actualizado correctamente.")
            return menu

        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al actualizar el menú: {e}")

    def eliminar_menu(self, menu_id: int):
        """Elimina un menú existente."""
        try:
            menu = self._buscar_menu_por_id(menu_id)
            if not menu:
                raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")

            self.conexion.delete(menu)
            self.conexion.commit()
            logging.info(f"Menú con ID {menu_id} eliminado correctamente.")
            return f"Menú con ID {menu_id} eliminado correctamente."
        except Exception as e:
            self.conexion.rollback()
            raise MenuCRUDException(f"Error inesperado al eliminar el menú: {e}")

    def cerrar_sesion(self):
        """Cierra la sesión de la conexión."""
        self.conexion.close()
        logging.info("Sesión cerrada para MenuCRUD.")
