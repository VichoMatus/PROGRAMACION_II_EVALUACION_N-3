#Elias

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, NoResultFound
from database import engine
from models import Menu, Ingrediente,menu_ingredientes

Session = sessionmaker(bind=engine)
conexion = Session()

class MenuCRUDException(Exception):
    pass

def crear_menu(nombre_menu: str, descripcion_menu: str, lista_ingredientes: dict):

    try:
        menu_nuevo = Menu(nombre=nombre_menu, descripcion=descripcion_menu)

        # Verificar y asociar ingredientes con cantidades requeridas
        for nombre_ingrediente, cantidad in lista_ingredientes.items():
            ingrediente = conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()
            if not ingrediente:
                raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
            # Agregar al menú con la cantidad requerida
            menu_nuevo.ingredientes.append(ingrediente)
            conexion.execute(menu_ingredientes.insert().values(
                menu_id=menu_nuevo.id,
                ingrediente_id=ingrediente.id,
                cantidad_requerida=cantidad
            ))
        
        conexion.add(menu_nuevo)
        conexion.commit()
        return menu_nuevo

    except IntegrityError:
        conexion.rollback()
        raise MenuCRUDException("Error de integridad al crear el menú.")
    except Exception as e:
        conexion.rollback()
        raise MenuCRUDException(f"Error inesperado: {e}")


def listar_menus():
 
    try:
        menus = conexion.query(Menu).all()
        for menu in menus:
            print(f"ID: {menu.id}, Nombre: {menu.nombre}, Descripción: {menu.descripcion}")
            for ingrediente in menu.ingredientes:
                print(f"  - Ingrediente: {ingrediente.nombre}, Cantidad: {ingrediente.cantidad}")
        return menus

    except Exception as e:
        raise MenuCRUDException(f"Error al listar menús: {e}")

def buscar_menu_por_id(menu_id: int):

    try:
        menu = conexion.query(Menu).filter_by(id=menu_id).first()
        if not menu:
            raise MenuCRUDException(f"Menú con ID {menu_id} no encontrado.")
        return menu
    except Exception as e:
        raise MenuCRUDException(f"Error al buscar el menú: {e}")

def actualizar_menu(menu_id: int, nuevo_nombre: str = None, nueva_descripcion: str = None, nuevos_ingredientes: dict = None):

    try:
        menu = buscar_menu_por_id(menu_id)

        if nuevo_nombre:
            menu.nombre = nuevo_nombre
        if nueva_descripcion:
            menu.descripcion = nueva_descripcion
        if nuevos_ingredientes:
            menu.ingredientes.clear()
            for nombre_ingrediente, cantidad in nuevos_ingredientes.items():
                ingrediente = conexion.query(Ingrediente).filter_by(nombre=nombre_ingrediente).first()
                if not ingrediente:
                    raise MenuCRUDException(f"Ingrediente '{nombre_ingrediente}' no existe.")
                menu.ingredientes.append(ingrediente)
        
        conexion.commit()
        return menu
    except MenuCRUDException as e:
        conexion.rollback()
        raise e
    except Exception as e:
        conexion.rollback()
        raise MenuCRUDException(f"Error inesperado al actualizar el menú: {e}")

def eliminar_menu(menu_id: int):

    try:
        menu = buscar_menu_por_id(menu_id)
        conexion.delete(menu)
        conexion.commit()
        print(f"Menú con ID {menu_id} eliminado correctamente.")
    except MenuCRUDException as e:
        conexion.rollback()
        raise e
    except Exception as e:
        conexion.rollback()
        raise MenuCRUDException(f"Error inesperado al eliminar el menú: {e}")
