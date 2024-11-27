import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session
from crud.cliente_crud import ClienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD, IngredienteCRUDException
from sqlalchemy.exc import IntegrityError

# Configuración inicial
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Clientes y Pedidos")
        self.geometry("900x700")

        # Crear el Tabview (pestañas)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        # Crear pestañas
        self.tab_ingredientes = self.tabview.add("Ingredientes")
        self.init_ingredientes_tab(self.tab_ingredientes)
        
        self.tab_clientes = self.tabview.add("Clientes")
        self.init_clientes_tab(self.tab_clientes)


        self.tab_menu = self.tabview.add("Menú")
        self.init_menu_tab(self.tab_menu)

        self.tab_panel_compra = self.tabview.add("Panel de Compra")
        self.init_panel_compra_tab(self.tab_panel_compra)

        self.tab_pedidos = self.tabview.add("Pedidos")
        self.init_pedidos_tab(self.tab_pedidos)

     # --- Pestaña de Ingredientes ---
    def init_ingredientes_tab(self, parent):
        """Inicializa la pestaña de ingredientes."""
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        # Entradas para el nombre, tipo, unidad de medida y cantidad
        ctk.CTkLabel(frame_superior, text="Nombre:").grid(row=0, column=0, pady=10, padx=10)
        self.entry_nombre_ingrediente = ctk.CTkEntry(frame_superior)
        self.entry_nombre_ingrediente.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Tipo:").grid(row=0, column=2, pady=10, padx=10)
        self.entry_tipo_ingrediente = ctk.CTkEntry(frame_superior)
        self.entry_tipo_ingrediente.grid(row=0, column=3, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Unidad de Medida:").grid(row=1, column=0, pady=10, padx=10)
        self.entry_unidad_medida_ingrediente = ctk.CTkEntry(frame_superior)
        self.entry_unidad_medida_ingrediente.grid(row=1, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Cantidad:").grid(row=1, column=2, pady=10, padx=10)
        self.entry_cantidad_ingrediente = ctk.CTkEntry(frame_superior)
        self.entry_cantidad_ingrediente.grid(row=1, column=3, pady=10, padx=10)

        # Botones para agregar y eliminar ingredientes
        ctk.CTkButton(frame_superior, text="Agregar Ingrediente", command=self.agregar_ingrediente).grid(row=2, column=1, pady=10, padx=10)
        ctk.CTkButton(frame_superior, text="Eliminar Ingrediente", command=self.eliminar_ingrediente).grid(row=2, column=2, pady=10, padx=10)
        
        # Treeview para mostrar los ingredientes
        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_ingredientes = ttk.Treeview(frame_inferior, columns=("Nombre", "Tipo", "Unidad de Medida", "Cantidad"), show="headings")
        self.treeview_ingredientes.heading("Nombre", text="Nombre")
        self.treeview_ingredientes.heading("Tipo", text="Tipo")
        self.treeview_ingredientes.heading("Unidad de Medida", text="Unidad de Medida")
        self.treeview_ingredientes.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes.pack(fill="both", expand=True)

        # Cargar ingredientes iniciales
        self.cargar_ingredientes()

    def cargar_ingredientes(self):
        """Carga los ingredientes en el Treeview."""
        self.treeview_ingredientes.delete(*self.treeview_ingredientes.get_children())
        with next(get_session()) as db:
            ingredientes = IngredienteCRUD().listar_ingredientes()
            for ingrediente in ingredientes:
                self.treeview_ingredientes.insert("", "end", values=(ingrediente.nombre, ingrediente.tipo, ingrediente.unidad_medida, ingrediente.cantidad))

    def agregar_ingrediente(self):
        """Agrega un ingrediente o suma la cantidad si ya existe."""
        nombre = self.entry_nombre_ingrediente.get().strip()
        tipo = self.entry_tipo_ingrediente.get().strip()
        unidad_medida = self.entry_unidad_medida_ingrediente.get().strip()
        cantidad = self.entry_cantidad_ingrediente.get().strip()

        if not nombre or not tipo or not unidad_medida or not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showwarning("Datos Inválidos", "Por favor, complete todos los campos con datos válidos.")
            return

        cantidad = int(cantidad)

        try:
            with next(get_session()) as db:
                crud = IngredienteCRUD()
                ingrediente = crud._buscar_ingrediente_por_nombre(nombre)
                if ingrediente:
                    # Si el ingrediente ya existe, sumar la cantidad
                    crud.actualizar_ingrediente(ingrediente.id, cantidad=ingrediente.cantidad + cantidad)
                else:
                    # Crear nuevo ingrediente
                    crud.crear_ingrediente(nombre, tipo, unidad_medida, cantidad)
            self.cargar_ingredientes()
            messagebox.showinfo("Éxito", "Ingrediente agregado correctamente.")
        except IngredienteCRUDException as e:
            messagebox.showerror("Error", str(e))
    

    def eliminar_ingrediente(self):
        """Elimina un ingrediente seleccionado."""
        selected_item = self.treeview_ingredientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione un ingrediente.")
            return

        nombre = self.treeview_ingredientes.item(selected_item)["values"][0]
        try:
            with next(get_session()) as db:
                crud = IngredienteCRUD()
                ingrediente = crud._buscar_ingrediente_por_nombre(nombre)
                if ingrediente:
                    crud.eliminar_ingrediente(ingrediente.id)
            self.cargar_ingredientes()
            messagebox.showinfo("Éxito", "Ingrediente eliminado correctamente.")
        except IngredienteCRUDException as e:
            messagebox.showerror("Error", str(e))

    # --- Pestaña de Clientes ---
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

        frame_superior.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkButton(frame_superior, text="Crear Cliente", command=self.crear_cliente).grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        ctk.CTkButton(frame_superior, text="Actualizar Cliente", command=self.actualizar_cliente).grid(row=1, column=2, pady=10, padx=10, sticky="ew")
        ctk.CTkButton(frame_superior, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=1, column=3, pady=10, padx=10, sticky="ew")

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_clientes = ttk.Treeview(frame_inferior, columns=("Nombre", "Email"), show="headings")
        self.treeview_clientes.heading("Nombre", text="Nombre")
        self.treeview_clientes.heading("Email", text="Email")
        self.treeview_clientes.pack(fill="both", expand=True)

        self.cargar_clientes()


    def cargar_clientes(self):
        """Carga los clientes en el Treeview."""
        self.treeview_clientes.delete(*self.treeview_clientes.get_children())
        with next(get_session()) as db:
            clientes = ClienteCRUD(db).obtener_clientes()
            for cliente in clientes:
                self.treeview_clientes.insert("", "end", values=(cliente.nombre, cliente.email))

    def crear_cliente(self):
        """Crea un nuevo cliente con los datos ingresados."""
        nombre = self.entry_nombre.get().strip()
        email = self.entry_email.get().strip()

        if not nombre or not email:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos.")
            return

        try:
            with next(get_session()) as db:
                cliente_crud = ClienteCRUD(db)
                cliente_crud.crear_cliente(email=email, nombre=nombre)
                messagebox.showinfo("Éxito", "Cliente creado correctamente.")
                self.cargar_clientes()
        except IntegrityError:
            messagebox.showwarning("Error", "El cliente ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear el cliente: {e}")

    def actualizar_cliente(self):
        """Actualiza un cliente seleccionado."""
        selected_item = self.treeview_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección Vacía", "Por favor, seleccione un cliente.")
            return

        email_actual = self.treeview_clientes.item(selected_item)["values"][1]
        nuevo_nombre = self.entry_nombre.get().strip()
        nuevo_email = self.entry_email.get().strip()

        if not nuevo_nombre or not nuevo_email:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos.")
            return

        try:
            with next(get_session()) as db:
                cliente_crud = ClienteCRUD(db)
                cliente_crud.actualizar_cliente(email_actual, nuevo_nombre=nuevo_nombre, nuevo_email=nuevo_email)
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
                self.cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el cliente: {e}")

    def eliminar_cliente(self):
        """Elimina un cliente seleccionado."""
        selected_item = self.treeview_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección Vacía", "Por favor, seleccione un cliente.")
            return

        email = self.treeview_clientes.item(selected_item)["values"][1]

        try:
            with next(get_session()) as db:
                cliente_crud = ClienteCRUD(db)
                cliente_crud.eliminar_cliente(email)
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.cargar_clientes()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el cliente: {e}")

 # -----------------------------------------------------------------MENU-----------------------------------------------------------------
    def init_menu_tab(self, parent):
        """Inicializa la pestaña de Menús."""
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        # Campos de entrada para nombre, descripción y precio
        ctk.CTkLabel(frame_superior, text="Nombre del Menú:").grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.entry_menu_nombre = ctk.CTkEntry(frame_superior)
        self.entry_menu_nombre.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(frame_superior, text="Descripción:").grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.entry_menu_descripcion = ctk.CTkEntry(frame_superior)
        self.entry_menu_descripcion.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(frame_superior, text="Precio:").grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.entry_menu_precio = ctk.CTkEntry(frame_superior)
        self.entry_menu_precio.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

        # Tabla de ingredientes para agregar al menú
        ctk.CTkLabel(frame_superior, text="Ingredientes:").grid(row=3, column=0, pady=10, padx=10, sticky="nw")
        self.treeview_ingredientes_menu = ttk.Treeview(frame_superior, columns=("Ingrediente", "Cantidad"), show="headings", height=5)
        self.treeview_ingredientes_menu.heading("Ingrediente", text="Ingrediente")
        self.treeview_ingredientes_menu.heading("Cantidad", text="Cantidad")
        self.treeview_ingredientes_menu.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        # Botones de acción para ingredientes
        ctk.CTkButton(frame_superior, text="Agregar Ingrediente", command=self.agregar_ingrediente_menu).grid(row=4, column=0, pady=10, padx=10)
        ctk.CTkButton(frame_superior, text="Crear Menú", command=self.crear_menu).grid(row=4, column=1, pady=10, padx=10)

        # Lista de menús
        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_menus = ttk.Treeview(frame_inferior, columns=("ID", "Nombre", "Descripción", "Precio"), show="headings")
        self.treeview_menus.heading("ID", text="ID")
        self.treeview_menus.heading("Nombre", text="Nombre")
        self.treeview_menus.heading("Descripción", text="Descripción")
        self.treeview_menus.heading("Precio", text="Precio")
        self.treeview_menus.pack(fill="both", expand=True)

        # Botones para cargar, actualizar y eliminar menús
        ctk.CTkButton(frame_inferior, text="Cargar Menús", command=self.cargar_menus).pack(side="left", pady=10, padx=10)
        ctk.CTkButton(frame_inferior, text="Actualizar Menú", command=self.actualizar_menu).pack(side="left", pady=10, padx=10)
        ctk.CTkButton(frame_inferior, text="Eliminar Menú", command=self.eliminar_menu).pack(side="left", pady=10, padx=10)

    def cargar_menus(self):
        """Carga todos los menús desde la base de datos."""
        self.treeview_menus.delete(*self.treeview_menus.get_children())
        with next(get_session()) as db:
            try:
                menus = MenuCRUD(db).listar_menus()
                for menu in menus:
                    self.treeview_menus.insert("", "end", values=(menu["id"], menu["nombre"], menu["descripcion"], menu["precio"]))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los menús: {e}")

    def crear_menu(self):
        """Crea un nuevo menú."""
        nombre = self.entry_menu_nombre.get().strip()
        descripcion = self.entry_menu_descripcion.get().strip()
        precio = self.entry_menu_precio.get().strip()

        if not nombre or not descripcion or not precio:
            messagebox.showwarning("Campos Vacíos", "Complete todos los campos antes de crear un menú.")
            return

        try:
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser un número positivo.")
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido y positivo.")
            return

        # Obtener los ingredientes seleccionados
        ingredientes = {
            self.treeview_ingredientes_menu.item(item)["values"][0]: int(self.treeview_ingredientes_menu.item(item)["values"][1])
            for item in self.treeview_ingredientes_menu.get_children()
        }

        if not ingredientes:
            messagebox.showwarning("Sin Ingredientes", "Debe agregar al menos un ingrediente al menú.")
            return

        with next(get_session()) as db:
            try:
                MenuCRUD(db).crear_menu(nombre=nombre, descripcion=descripcion, ingredientes=ingredientes, precio=precio)
                self.cargar_menus()
                messagebox.showinfo("Éxito", "Menú creado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el menú: {e}")

    def agregar_ingrediente_menu(self):
        """Abre una ventana para agregar ingredientes al menú."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Ingrediente")
        dialog.geometry("400x300")

        ctk.CTkLabel(dialog, text="Seleccione un ingrediente:").pack(pady=10)

        treeview_ingredientes = ttk.Treeview(dialog, columns=("ID", "Nombre"), show="headings")
        treeview_ingredientes.heading("ID", text="ID")
        treeview_ingredientes.heading("Nombre", text="Nombre")
        treeview_ingredientes.pack(fill="both", expand=True)

        # Cargar ingredientes desde la base de datos
        try:
            with next(get_session()) as db:
                ingredientes = IngredienteCRUD(db).listar_ingredientes()
                if ingredientes:
                    for ingrediente in ingredientes:
                        treeview_ingredientes.insert("", "end", values=(ingrediente.id, ingrediente.nombre))
                else:
                    messagebox.showinfo("Sin Ingredientes", "No hay ingredientes disponibles para agregar.")
                    dialog.destroy()
                    return
        except Exception as e:
            messagebox.showerror("Error", f"No se pueden cargar ingredientes: {e}")
            dialog.destroy()
            return

        def confirmar_seleccion():
            selected_item = treeview_ingredientes.selection()
            if not selected_item:
                messagebox.showwarning("Selección Vacía", "Seleccione un ingrediente para agregar.")
                return

            item_values = treeview_ingredientes.item(selected_item)["values"]
            ingrediente_nombre = item_values[1]

            # Pedir cantidad
            cantidad_dialog = ctk.CTkInputDialog(title="Cantidad", text="Ingrese la cantidad del ingrediente:")
            cantidad = cantidad_dialog.get_input()
            if not cantidad or not cantidad.isdigit() or int(cantidad) <= 0:
                messagebox.showwarning("Cantidad Inválida", "Debe ingresar una cantidad válida.")
                return

            self.treeview_ingredientes_menu.insert("", "end", values=(ingrediente_nombre, cantidad))
            dialog.destroy()

        ctk.CTkButton(dialog, text="Aceptar", command=confirmar_seleccion).pack(pady=10)

    def actualizar_menu(self):
        """Actualiza un menú existente."""
        selected_item = self.treeview_menus.selection()
        if not selected_item:
            messagebox.showwarning("Selección Vacía", "Seleccione un menú para actualizar.")
            return

        menu_id = self.treeview_menus.item(selected_item)["values"][0]
        nombre = self.entry_menu_nombre.get()
        descripcion = self.entry_menu_descripcion.get()

        if not nombre or not descripcion:
            messagebox.showwarning("Campos Vacíos", "Complete todos los campos antes de actualizar el menú.")
            return

        with next(get_session()) as db:
            try:
                MenuCRUD(db).actualizar_menu(menu_id, nombre, descripcion, {})
                self.cargar_menus()
                messagebox.showinfo("Éxito", "Menú actualizado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el menú: {e}")

    def eliminar_menu(self):
        """Elimina un menú seleccionado."""
        selected_item = self.treeview_menus.selection()
        if not selected_item:
            messagebox.showwarning("Selección Vacía", "Seleccione un menú para eliminar.")
            return

        menu_id = self.treeview_menus.item(selected_item)["values"][0]

        with next(get_session()) as db:
            try:
                MenuCRUD(db).eliminar_menu(menu_id)
                self.cargar_menus()
                messagebox.showinfo("Éxito", "Menú eliminado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el menú: {e}")


# -----------------------------------------------------------------PANEL DE COMPRA-----------------------------------------------------------------
    def init_panel_compra_tab(self, parent):
        """Inicializa la pestaña de Panel de Compra con todos los elementos necesarios."""
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_superior, text="Seleccionar Cliente:").grid(row=0, column=0, pady=10, padx=10)
        self.combo_clientes = ctk.CTkComboBox(frame_superior)
        self.combo_clientes.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(frame_superior, text="Seleccionar Menú:").grid(row=0, column=2, pady=10, padx=10)
        self.combo_productos = ctk.CTkComboBox(frame_superior)
        self.combo_productos.grid(row=0, column=3, pady=10, padx=10)

        ctk.CTkButton(frame_superior, text="Agregar al Carrito", command=self.agregar_a_carrito).grid(row=0, column=4, pady=10, padx=10)

        frame_carrito = ctk.CTkFrame(parent)
        frame_carrito.pack(pady=10, padx=10, fill="both", expand=True)

        self.treeview_carrito = ttk.Treeview(frame_carrito, columns=("Producto", "Cantidad", "Precio"), show="headings")
        self.treeview_carrito.heading("Producto", text="Producto")
        self.treeview_carrito.heading("Cantidad", text="Cantidad")
        self.treeview_carrito.heading("Precio", text="Precio")
        self.treeview_carrito.pack(fill="both", expand=True)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="x")

        self.label_total = ctk.CTkLabel(frame_inferior, text="Total: $0")
        self.label_total.pack(side="left", padx=10)

        ctk.CTkButton(frame_inferior, text="Confirmar Compra", command=self.confirmar_compra).pack(side="right", padx=10)

        # Cargar clientes y productos
        self.cargar_clientes_y_productos()

    def cargar_clientes_y_productos(self):
        """Carga los clientes y menús en los combos."""
        try:
            with next(get_session()) as db:
                clientes = ClienteCRUD(db).obtener_clientes()
                self.combo_clientes.configure(values=[cliente.email for cliente in clientes])

                menus = MenuCRUD().listar_menus()
                self.combo_productos.configure(values=[f"{menu['nombre']} - ${menu['precio']}" for menu in menus])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes o productos: {e}")

    def agregar_a_carrito(self):
        """Agrega el producto seleccionado al carrito."""
        cliente_email = self.combo_clientes.get()
        producto_seleccionado = self.combo_productos.get()

        if not cliente_email or not producto_seleccionado:
            messagebox.showwarning("Campos Vacíos", "Por favor, seleccione un cliente y un producto.")
            return

        try:
            producto_nombre, producto_precio = producto_seleccionado.split(" - $")
            producto_precio = float(producto_precio)
        except ValueError:
            messagebox.showerror("Error", "El formato del producto seleccionado es inválido.")
            return

        self.treeview_carrito.insert("", "end", values=(producto_nombre, 1, f"${producto_precio:.2f}"))
        self.actualizar_total()

    def actualizar_total(self):
        """Actualiza el total del carrito."""
        total = 0
        for item in self.treeview_carrito.get_children():
            precio = self.treeview_carrito.item(item)["values"][2]
            total += float(precio.strip("$"))
        self.label_total.configure(text=f"Total: ${total:.2f}")

    def confirmar_compra(self):
        """Confirma la compra y la registra en la base de datos."""
        cliente_email = self.combo_clientes.get()
        if not cliente_email:
            messagebox.showwarning("Campos Vacíos", "Por favor, seleccione un cliente.")
            return

        carrito = []
        for item in self.treeview_carrito.get_children():
            producto, cantidad, precio = self.treeview_carrito.item(item)["values"]
            carrito.append({"producto": producto, "cantidad": cantidad, "precio": float(precio.strip("$"))})

        if not carrito:
            messagebox.showwarning("Carrito Vacío", "El carrito está vacío. Agregue productos para confirmar la compra.")
            return

        try:
            with next(get_session()) as db:
                descripcion = f"Compra realizada con {len(carrito)} productos."
                total_menus = sum(item["cantidad"] for item in carrito)
                PedidoCRUD(db).crear_pedido(descripcion, cliente_email, total_menus)
                messagebox.showinfo("Éxito", "Compra confirmada y registrada correctamente.")
        except IntegrityError:
            messagebox.showerror("Error", "Error de integridad al confirmar la compra.")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            return
        finally:
            self.treeview_carrito.delete(*self.treeview_carrito.get_children())
            self.actualizar_total()
# -----------------------------------------------------------------PEDIDOS-----------------------------------------------------------------
# --- Pestaña de Pedidos ---
    def init_pedidos_tab(self, parent):
        """Inicializa la pestaña de pedidos."""
        frame_superior = ctk.CTkFrame(parent)
        frame_superior.pack(pady=10, padx=10, fill="x")

        # Select para correos de clientes
        ctk.CTkLabel(frame_superior, text="Correo Cliente:").grid(row=0, column=0, pady=10, padx=10)
        with next(get_session()) as db:
            self.clientes = ClienteCRUD(db).obtener_correos_clientes()
        self.select_cliente = ctk.CTkOptionMenu(frame_superior, values=self.clientes)
        self.select_cliente.grid(row=0, column=1, pady=10, padx=10)

        # Campo de descripción
        ctk.CTkLabel(frame_superior, text="Descripción:").grid(row=1, column=0, pady=10, padx=10)
        self.entry_descripcion = ctk.CTkEntry(frame_superior, height=50, width=400)
        self.entry_descripcion.grid(row=1, column=1, pady=10, padx=10)

        # Campo de cantidad
        ctk.CTkLabel(frame_superior, text="Cantidad:").grid(row=2, column=0, pady=10, padx=10)
        self.entry_cantidad = ctk.CTkEntry(frame_superior)
        self.entry_cantidad.grid(row=2, column=1, pady=10, padx=10)

        # Botones de acción

        ctk.CTkButton(
            frame_superior, text="Crear Pedido", command=self.crear_pedido).grid(
            row=4, column=0, pady=10, padx=10)
        ctk.CTkButton(
            frame_superior, text="Actualizar Pedido", command=self.actualizar_pedido).grid(
            row=4, column=1, pady=10, padx=10)

        # Botón de acción para eliminar
        ctk.CTkButton(
            frame_superior, text="Eliminar Pedido", command=self.eliminar_pedido).grid(
            row=4, column=2, pady=10, padx=10)

        frame_inferior = ctk.CTkFrame(parent)
        frame_inferior.pack(pady=10, padx=10, fill="both", expand=True)

        # Configuración del Treeview para mostrar pedidos
        self.treeview_pedidos = ttk.Treeview(frame_inferior, columns=(
            "ID Pedido", "Correo Cliente", "Descripción", "Fecha de creación", "Cantidad"), show="headings")
        self.treeview_pedidos.heading("ID Pedido", text="ID Pedido")
        self.treeview_pedidos.heading("Correo Cliente", text="Correo Cliente")
        self.treeview_pedidos.heading("Descripción", text="Descripción")
        self.treeview_pedidos.heading("Fecha de creación", text="Fecha de creación")
        self.treeview_pedidos.heading("Cantidad", text="Cantidad")
        self.treeview_pedidos.pack(fill="both", expand=True)

        # Cargar pedidos al iniciar
        self.cargar_pedidos()

    def cargar_pedidos(self):
        """Carga los pedidos en el Treeview."""
        self.treeview_pedidos.delete(*self.treeview_pedidos.get_children())
        with next(get_session()) as db:
            pedidos = PedidoCRUD(db).obtener_pedidos()
            for pedido in pedidos:
                # Agregar el correo del cliente al mostrar
                cliente = ClienteCRUD(db).obtener_cliente_por_email(pedido.cliente_email)
                correo_cliente = cliente.email if cliente else "Desconocido"
                self.treeview_pedidos.insert("", "end", values=(
                    pedido.id, correo_cliente, pedido.descripcion, pedido.fecha_creacion, pedido.cantidad_menus))

    def crear_pedido(self):
        """Crea un nuevo pedido."""
        correo_cliente = self.select_cliente.get()  # Correo seleccionado
        descripcion = self.entry_descripcion.get()  # Descripción del pedido
        cantidad = self.entry_cantidad.get()  # Cantidad del pedido

        # Convertir la cantidad a entero (asegurándote de que sea un número válido)
        try:
            cantidad = int(cantidad)  # Convertir a entero
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número válido.")
            return

        # Validar que todos los campos estén completos
        if correo_cliente and descripcion and cantidad > 0:
            try:
                with next(get_session()) as db:
                    cliente = ClienteCRUD(db).obtener_cliente_por_email(correo_cliente)
                    if cliente:
                        # Crear pedido en la base de datos
                        PedidoCRUD(db).crear_pedido(descripcion, cliente.email, cantidad)
                        messagebox.showinfo("Éxito", "Pedido creado exitosamente.")
                        self.cargar_pedidos()  # Recargar los pedidos
                    else:
                        messagebox.showwarning("Cliente no encontrado", "El cliente con ese correo no existe.")
            except Exception as e:
                messagebox.showwarning("Error", f"Ocurrió un error: {e}")
        else:
            messagebox.showwarning(
                "Campos Vacíos", "Por favor, ingrese todos los campos y asegúrese de que la cantidad sea válida.")

    def actualizar_pedido(self):
        """Actualiza un pedido existente."""
        correo_cliente = self.select_cliente.get()  # Correo seleccionado
        descripcion = self.entry_descripcion.get()  # Nueva descripción del pedido
        cantidad = self.entry_cantidad.get()  # Nueva cantidad del pedido

        # Convertir la cantidad a entero (asegurándote de que sea un número válido)
        try:
            cantidad = int(cantidad)  # Convertir a entero
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número válido.")
            return

        # Validar si todos los campos están llenos
        if correo_cliente and descripcion and cantidad > 0:
            try:
                with next(get_session()) as db:
                    # Obtener el cliente por correo
                    cliente = ClienteCRUD(db).obtener_cliente_por_email(correo_cliente)
                    if cliente:
                        # Obtener el ID del pedido seleccionado (debería obtenerse desde el Treeview)
                        selected_item = self.treeview_pedidos.selection()
                        if selected_item:
                            pedido_id = self.treeview_pedidos.item(selected_item)["values"][0]  # ID del pedido
                            # Actualizar el pedido en la base de datos
                            PedidoCRUD(db).actualizar_pedido(pedido_id, descripcion, cantidad)
                            self.cargar_pedidos()  # Recargar los pedidos
                            messagebox.showinfo("Éxito", "Pedido actualizado correctamente.")
                        else:
                            messagebox.showwarning("Selección Incorrecta",
                                                   "Por favor, seleccione un pedido para actualizar.")
                    else:
                        messagebox.showwarning("Error", "Cliente no encontrado.")
            except Exception as e:
                messagebox.showwarning("Error", f"Ocurrió un error: {e}")
        else:
            messagebox.showwarning("Campos Vacíos", "Por favor, ingrese todos los campos.")

    def eliminar_pedido(self):
        """Elimina un pedido seleccionado."""
        selected_item = self.treeview_pedidos.selection()  # Obtenemos el pedido seleccionado
        if selected_item:
            pedido_id = self.treeview_pedidos.item(selected_item)["values"][0]  # ID del pedido
            confirm = messagebox.askyesno("Confirmar Eliminación",
                                          f"¿Estás seguro de eliminar el pedido con ID: {pedido_id}?")
            if confirm:
                try:
                    with next(get_session()) as db:
                        PedidoCRUD(db).eliminar_pedido(pedido_id)  # Eliminar pedido
                        self.cargar_pedidos()  # Recargar los pedidos
                        messagebox.showinfo("Éxito", "Pedido eliminado correctamente.")
                except Exception as e:
                    messagebox.showwarning("Error", f"Ocurrió un error al eliminar el pedido: {e}")
        else:
            messagebox.showwarning("Selección Incorrecta", "Por favor, seleccione un pedido para eliminar.")



if __name__ == "__main__":
    app = App()
    app.mainloop()
