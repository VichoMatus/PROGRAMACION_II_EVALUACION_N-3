import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session
from crud.cliente_crud import *
from crud.pedido_crud import *
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

    # --- Pestaña de Menú ---
    def init_menu_tab(self, parent):
        """Inicializa la pestaña de menú."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gestión del Menú").pack(pady=10, padx=10)

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


    # --- Pestaña de Gráficos ---
    def init_graficos_tab(self, parent):
        """Inicializa la pestaña de gráficos."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gráficos e Informes").pack(pady=10, padx=10)

 

if __name__ == "__main__":
    app = App()
    app.mainloop()
