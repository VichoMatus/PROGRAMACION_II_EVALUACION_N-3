from sqlalchemy import Column, String, Integer, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base, engine  # Importar Base y engine desde database.py

# Tabla intermedia para la relación muchos-a-muchos entre Menu e Ingrediente
menu_ingredientes = Table(
    'menu_ingredientes', Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True),
    Column('ingrediente_id', Integer, ForeignKey('ingredientes.id'), primary_key=True),
    Column('cantidad_requerida', Integer, nullable=False)  # Cantidad requerida de cada ingrediente en un menú
)

# Clase Cliente
class Cliente(Base):
    __tablename__ = 'clientes'
    
    email = Column(String(255), primary_key=True)  # Email como clave primaria
    nombre = Column(String(255), nullable=False)  # Nombre del cliente
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")

# Clase Pedido
class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True)  # Identificador único del pedido, autoincrement automático
    descripcion = Column(String(255), nullable=False)  # Descripción del pedido
    cliente_email = Column(String(255), ForeignKey('clientes.email', onupdate="CASCADE"), nullable=False)  # Clave foránea
    cliente = relationship("Cliente", back_populates="pedidos")
    fecha_creacion = Column(DateTime, default=func.now())  # Fecha de creación del pedido
    cantidad_menus = Column(Integer, nullable=False)  # Cantidad de menús comprados

# Clase Ingrediente
class Ingrediente(Base):
    __tablename__ = 'ingredientes'
    
    id = Column(Integer, primary_key=True)  # Identificador único del ingrediente, autoincrement automático
    nombre = Column(String(255), nullable=False, unique=True)  # Nombre único del ingrediente
    tipo = Column(String(255), nullable=False)  # Tipo del ingrediente (Vegetal, Proteína, etc.)
    unidad_medida = Column(String(50), nullable=False)  # Unidad de medida (g, ml, unidad, etc.)
    cantidad = Column(Integer, nullable=False)  # Cantidad disponible en el inventario
    menus = relationship("Menu", secondary=menu_ingredientes, back_populates="ingredientes")

# Clase Menu
class Menu(Base):
    __tablename__ = 'menus'
    
    id = Column(Integer, primary_key=True)  # Identificador único del menú, autoincrement automático
    nombre = Column(String(255), nullable=False, unique=True)  # Nombre único del menú
    descripcion = Column(String(255), nullable=False)  # Descripción del menú
    ingredientes = relationship("Ingrediente", secondary=menu_ingredientes, back_populates="menus")

# Crear todas las tablas en la base de datos
Base.metadata.create_all(engine)
