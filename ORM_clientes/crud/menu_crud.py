from sqlalchemy.orm import sessionmaker
from database import engine
from models import Menu, Ingrediente

# Se configura la sesión de la base de datos para gestionar las operaciones
Session = sessionmaker(bind=engine)
conexion = Session()

# Crea un nuevo menú con sus ingredientes
def crear_menu(nombre_menu, descripcion_menu, lista_ingredientes):
    menu_nuevo = Menu(nombre=nombre_menu, descripcion=descripcion_menu)
    for nombre_ingrediente, cantidad in lista_ingredientes.items():
        menu_nuevo.ingredientes.append(Ingrediente(nombre=nombre_ingrediente, cantidad=cantidad))
    conexion.add(menu_nuevo)
    conexion.commit()
    print(f"Menú '{nombre_menu}' creado exitosamente.")

# Se lista todos los menús existentes junto con sus ingredientes
def listar_menus():
    menus = conexion.query(Menu).all()
    for menu in menus:
        print(f"ID: {menu.id}, Nombre: {menu.nombre}, Descripción: {menu.descripcion}")
        for ingrediente in menu.ingredientes:
            print(f"  - {ingrediente.nombre}: {ingrediente.cantidad}")
    return menus

# Actualiza un menú existente usando su ID
def actualizar_menu(id_menu, nuevo_nombre=None, nueva_descripcion=None, nuevos_ingredientes=None):
    # Buscamos el menú específico que queremos actualizar
    menu = conexion.query(Menu).filter(Menu.id == id_menu).first()
    if menu:
        if nuevo_nombre:
            menu.nombre = nuevo_nombre
        if nueva_descripcion:
            menu.descripcion = nueva_descripcion
        if nuevos_ingredientes:
            menu.ingredientes.clear()  # Limpiamos los ingredientes actuales
            for nombre_ingrediente, cantidad in nuevos_ingredientes.items():
                menu.ingredientes.append(Ingrediente(nombre=nombre_ingrediente, cantidad=cantidad))
        conexion.commit()
        print(f"Menú '{menu.nombre}' actualizado exitosamente.")
    else:
        print("Menú no encontrado.")

# Elimina un menú por su ID
def eliminar_menu(id_menu):
    # Buscamos el menú específico que queremos eliminar
    menu = conexion.query(Menu).filter(Menu.id == id_menu).first()
    if menu:
        # Eliminamos el menú de la base de datos
        conexion.delete(menu)
        conexion.commit()
        print(f"Menú '{menu.nombre}' eliminado exitosamente.")
    else:
        print("Menú no encontrado.")

# Función para cerrar la sesión de conexión con la base de datos
def cerrar_conexion():
    conexion.close()
