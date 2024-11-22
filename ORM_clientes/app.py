import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session
from crud.cliente_crud import *
from crud.menu_crud import *
from sqlalchemy.exc import IntegrityError

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Clientes y Pedidos")
        self.geometry("750x600")

        # Crear el Tabview (pestañas)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        # Crear pestañas
        self.tab_ingredientes = self.tabview.add("Ingredientes")
        self.init_ingredientes_tab(self.tab_ingredientes)

        self.tab_menu = self.tabview.add("Menú")
        self.init_menu_tab(self.tab_menu)

        self.tab_clientes = self.tabview.add("Clientes")
        self.init_clientes_tab(self.tab_clientes)

        self.tab_panel_compra = self.tabview.add("Panel de Compra")
        self.init_panel_compra_tab(self.tab_panel_compra)

        self.tab_pedidos = self.tabview.add("Pedidos")
        self.init_pedidos_tab(self.tab_pedidos)

        self.tab_graficos = self.tabview.add("Gráficos")
        self.init_graficos_tab(self.tab_graficos)


    # --- Pestaña de Ingredientes ---
    def init_ingredientes_tab(self, parent):
        """Inicializa la pestaña de ingredientes."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gestión de Ingredientes").pack(pady=10, padx=10)

    def init_menu_tab(self, parent):
        """Inicializa la pestaña de menú."""
        # Marco superior: Formulario para crear/editar menús
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Nombre del Menú:").grid(row=0, column=0, pady=10, padx=10)
        self.entry_menu_nombre = ctk.CTkEntry(frame_superior)
        self.entry_menu_nombre.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Descripción:").grid(row=1, column=0, pady=10, padx=10)
        self.entry_menu_descripcion = ctk.CTkEntry(frame_superior)
        self.entry_menu_descripcion.grid(row=1, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Ingredientes:").grid(row=2, column=0, pady=10, padx=10)
        self.treeview_ingredientes_menu = ttk.Treeview(frame_superior, columns=("Ingrediente", "Cantidad"), show="headings", height=5)
        self.treeview_ingredientes_menu.heading("Ingrediente", text="Ingrediente")
        self.treeview_ingredientes_menu.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes_menu.grid(row=2, column=1, pady=10, padx=10)

        ctk.CTkButton(frame_superior, text="Agregar Ingrediente", command=self.agregar_ingrediente_menu).grid(row=3, column=0, pady=10, padx=10)
        ctk.CTkButton(frame_superior, text="Crear Menú", command=self.crear_menu).grid(row=3, column=1, pady=10, padx=10)

        # Marco inferior: Lista de menús y botones de acciones
        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_menus = ttk.Treeview(frame_inferior, columns=("ID", "Nombre", "Descripción"), show="headings")
        self.treeview_menus.heading("ID", text="ID")
        self.treeview_menus.heading("Nombre", text="Nombre")
        self.treeview_menus.heading("Descripción", text="Descripción")
        self.treeview_menus.pack(fill="both", expand=True)

        ctk.CTkButton(frame_inferior, text="Cargar Menús", command=self.cargar_menus).pack(side="left", pady=10, padx=10)
        ctk.CTkButton(frame_inferior, text="Actualizar Menú", command=self.actualizar_menu).pack(side="left", pady=10, padx=10)
        ctk.CTkButton(frame_inferior, text="Eliminar Menú", command=self.eliminar_menu).pack(side="left", pady=10, padx=10)

    def cargar_menus(self):
        """Carga los menús desde la base de datos al Treeview."""
        self.treeview_menus.delete(*self.treeview_menus.get_children())
        with next(get_session()) as db:
            menus = MenuCRUD(db).listar_menus()
            for menu in menus:
                self.treeview_menus.insert("", "end", values=(menu["id"], menu["nombre"], menu["descripcion"]))

    def crear_menu(self):
        """Crea un nuevo menú con los datos ingresados."""
        nombre = self.entry_menu_nombre.get()
        descripcion = self.entry_menu_descripcion.get()
        ingredientes = {
            item[0]: int(item[1]) for item in [
                self.treeview_ingredientes_menu.item(i)["values"] for i in self.treeview_ingredientes_menu.get_children()
            ]
        }
        if not nombre or not descripcion or not ingredientes:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos y agregue al menos un ingrediente.")
            return

        try:
            with next(get_session()) as db:
                menu_crud = MenuCRUD(db)
                menu_crud.crear_menu(nombre, descripcion, ingredientes)
            self.cargar_menus()
            messagebox.showinfo("Éxito", "Menú creado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def agregar_ingrediente_menu(self):
        """Abre una ventana para agregar un ingrediente al menú."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Ingrediente")
        dialog.geometry("300x200")

        ctk.CTkLabel(dialog, text="Nombre del Ingrediente:").pack(pady=10, padx=10)
        entry_ingrediente = ctk.CTkEntry(dialog)
        entry_ingrediente.pack(pady=5, padx=10)

        ctk.CTkLabel(dialog, text="Cantidad:").pack(pady=10, padx=10)
        entry_cantidad = ctk.CTkEntry(dialog)
        entry_cantidad.pack(pady=5, padx=10)

        def confirmar_agregar():
            nombre = entry_ingrediente.get()
            cantidad = entry_cantidad.get()
            if nombre and cantidad.isdigit() and int(cantidad) > 0:
                self.treeview_ingredientes_menu.insert("", "end", values=(nombre, cantidad))
                dialog.destroy()  
            else:
                messagebox.showwarning("Error", "Por favor, ingrese un nombre válido y una cantidad mayor a 0.")

        ctk.CTkButton(dialog, text="Aceptar", command=confirmar_agregar).pack(pady=20, padx=10)


    def actualizar_menu(self):
        """Actualiza el menú seleccionado."""
        selected_item = self.treeview_menus.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione un menú.")
            return

        menu_id = self.treeview_menus.item(selected_item)["values"][0]
        nombre = self.entry_menu_nombre.get()
        descripcion = self.entry_menu_descripcion.get()
        ingredientes = {
            item[0]: int(item[1]) for item in [
                self.treeview_ingredientes_menu.item(i)["values"] for i in self.treeview_ingredientes_menu.get_children()
            ]
        }
        if not nombre or not descripcion or not ingredientes:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos y agregue al menos un ingrediente.")
            return

        try:
            with next(get_session()) as db:
                menu_crud = MenuCRUD(db)
                menu_crud.actualizar_menu(menu_id, nombre, descripcion, ingredientes)
            self.cargar_menus()
            messagebox.showinfo("Éxito", "Menú actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_menu(self):
        """Elimina el menú seleccionado."""
        selected_item = self.treeview_menus.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione un menú.")
            return

        menu_id = self.treeview_menus.item(selected_item)["values"][0]
        try:
            with next(get_session()) as db:
                MenuCRUD(db).eliminar_menu(menu_id)
            self.cargar_menus()
            messagebox.showinfo("Éxito", "Menú eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    #-----------------------------------------------------------------CLIENTES-----------------------------------------------------------------
    def init_clientes_tab(self, parent): 
        """Inicializa la pestaña de clientes."""
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Nombre:").grid(row=0, column=0, pady=10, padx=10)
        self.entry_nombre = ctk.CTkEntry(frame_superior)
        self.entry_nombre.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Email:").grid(row=0, column=2, pady=10, padx=10)
        self.entry_email = ctk.CTkEntry(frame_superior)
        self.entry_email.grid(row=0, column=3, pady=10, padx=10)

        # Configuración de espaciado uniforme para los botones
        frame_superior.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Más columnas para el espaciado

        ctk.CTkButton(frame_superior, text="Crear Cliente", command=self.crear_cliente).grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        ctk.CTkButton(frame_superior, text="Actualizar Cliente", command=self.actualizar_cliente).grid(row=1, column=2, pady=10, padx=10, sticky="ew")
        ctk.CTkButton(frame_superior, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=1, column=3, pady=10, padx=10, sticky="ew")

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        # Configuración del Treeview
        self.treeview_clientes = ttk.Treeview(frame_inferior, columns=("Nombre", "Email"), show="headings")
        self.treeview_clientes.heading("Nombre", text="Nombre")
        self.treeview_clientes.heading("Email", text="Email")
        self.treeview_clientes.pack(fill="both", expand=True)

        # Cargar los clientes iniciales
        self.cargar_clientes()



    def cargar_clientes(self):
        """Carga los clientes en el Treeview."""
        self.treeview_clientes.delete(*self.treeview_clientes.get_children())
        with next(get_session()) as db:
            clientes = ClienteCRUD(db).obtener_clientes()
            for cliente in clientes:
                self.treeview_clientes.insert("", "end", values=(cliente.nombre, cliente.email))
    

    def crear_cliente(self):
        """Crea un cliente."""
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        if nombre and email:
            try:
                with next(get_session()) as db:
                    ClienteCRUD(db).crear_cliente(email, nombre)
                self.cargar_clientes()
                messagebox.showinfo("Éxito", "Cliente creado correctamente.")
            except IntegrityError:
                messagebox.showwarning("Error", "El cliente ya existe.")
        else:
            messagebox.showwarning("Campos Vacíos", "Por favor, ingrese todos los campos.")

    def actualizar_cliente(self):
        """Actualiza un cliente seleccionado."""
        selected_item = self.treeview_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione un cliente.")
            return

        email_actual = self.treeview_clientes.item(selected_item)["values"][1]
        nuevo_nombre = self.entry_nombre.get()
        nuevo_email = self.entry_email.get()

        if not nuevo_nombre or not nuevo_email:
            messagebox.showwarning("Campos Vacíos", "Por favor, ingrese todos los campos.")
            return

        try:
            with next(get_session()) as db:
                cliente_actualizado = ClienteCRUD(db).actualizar_cliente(email_actual, nuevo_nombre, nuevo_email)
                if cliente_actualizado:
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
                    self.cargar_clientes()
                else:
                    messagebox.showwarning("Error", "No se pudo actualizar el cliente.")
        except ClienteCRUDException as e:
            messagebox.showerror("Error", str(e))

    def eliminar_cliente(self):
        """Elimina un cliente seleccionado."""
        selected_item = self.treeview_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione un cliente.")
            return

        email = self.treeview_clientes.item(selected_item)["values"][1]
        try:
            with next(get_session()) as db:
                ClienteCRUD(db).eliminar_cliente(email)
            self.cargar_clientes()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
        except ClienteCRUDException as e:
            messagebox.showerror("Error", str(e))

    #-----------------------------------------------------------------CLIENTES-----------------------------------------------------------------
    # --- Pestaña de Panel de Compra ---
    def init_panel_compra_tab(self, parent):
        """Inicializa la pestaña de panel de compra."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Panel de Compra").pack(pady=10, padx=10)

    # --- Pestaña de Pedidos ---
    def init_pedidos_tab(self, parent):
        """Inicializa la pestaña de pedidos."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gestión de Pedidos").pack(pady=10, padx=10)

    # --- Pestaña de Gráficos ---
    def init_graficos_tab(self, parent):
        """Inicializa la pestaña de gráficos."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gráficos e Informes").pack(pady=10, padx=10)

 

if __name__ == "__main__":
    app = App()
    app.mainloop()
