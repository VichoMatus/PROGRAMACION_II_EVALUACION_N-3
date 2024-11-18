# app.py
import customtkinter as ctk
from cliente_crud import *
from ingrediente_crud import *
from sqlalchemy.orm import sessionmaker
from database import engine
from tkinter import ttk

# Configurar la sesión de la base de datos
Session = sessionmaker(bind=engine)
session = Session()

class RestauranteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Restaurante")
        self.geometry("800x600")

        # Configuración de pestañas
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")

        # Crear pestañas
        self.tab_clientes = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(self.tab_clientes, text="Clientes")

        self.tab_ingredientes = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(self.tab_ingredientes, text="Ingredientes")

        # Inicializar vistas
        self.init_clientes_tab()
        self.init_ingredientes_tab()

    def init_clientes_tab(self):
        # Elementos GUI para la pestaña de clientes
        ctk.CTkLabel(self.tab_clientes, text="Gestión de Clientes").pack(pady=10)

        self.cliente_nombre = ctk.CTkEntry(self.tab_clientes, placeholder_text="Nombre")
        self.cliente_nombre.pack(pady=5)

        self.cliente_correo = ctk.CTkEntry(self.tab_clientes, placeholder_text="Correo Electrónico")
        self.cliente_correo.pack(pady=5)

        ctk.CTkButton(self.tab_clientes, text="Agregar Cliente", command=self.agregar_cliente).pack(pady=10)

    def agregar_cliente(self):
        # Función para agregar un cliente
        nombre = self.cliente_nombre.get()
        correo = self.cliente_correo.get()
        if nombre and correo:
            try:
                crear_cliente(session, nombre, correo)
                ctk.CTkLabel(self.tab_clientes, text="Cliente agregado correctamente", text_color="green").pack(pady=5)
            except Exception as e:
                ctk.CTkLabel(self.tab_clientes, text=f"Error: {e}", text_color="red").pack(pady=5)

    def init_ingredientes_tab(self):
        # Elementos GUI para la pestaña de ingredientes
        ctk.CTkLabel(self.tab_ingredientes, text="Gestión de Ingredientes").pack(pady=10)

        self.ingrediente_nombre = ctk.CTkEntry(self.tab_ingredientes, placeholder_text="Nombre")
        self.ingrediente_nombre.pack(pady=5)

        self.ingrediente_tipo = ctk.CTkEntry(self.tab_ingredientes, placeholder_text="Tipo")
        self.ingrediente_tipo.pack(pady=5)

        self.ingrediente_cantidad = ctk.CTkEntry(self.tab_ingredientes, placeholder_text="Cantidad")
        self.ingrediente_cantidad.pack(pady=5)

        self.ingrediente_unidad = ctk.CTkEntry(self.tab_ingredientes, placeholder_text="Unidad de Medida")
        self.ingrediente_unidad.pack(pady=5)

        ctk.CTkButton(self.tab_ingredientes, text="Agregar Ingrediente", command=self.agregar_ingrediente).pack(pady=10)

    def agregar_ingrediente(self):
        # Función para agregar un ingrediente
        nombre = self.ingrediente_nombre.get()
        tipo = self.ingrediente_tipo.get()
        cantidad = float(self.ingrediente_cantidad.get()) if self.ingrediente_cantidad.get() else 0
        unidad = self.ingrediente_unidad.get()
        if nombre and tipo and unidad:
            try:
                crear_ingrediente(session, nombre, tipo, cantidad, unidad)
                ctk.CTkLabel(self.tab_ingredientes, text="Ingrediente agregado correctamente", text_color="green").pack(pady=5)
            except Exception as e:
                ctk.CTkLabel(self.tab_ingredientes, text=f"Error: {e}", text_color="red").pack(pady=5)

if __name__ == "__main__":
    app = RestauranteApp()
    app.mainloop()
