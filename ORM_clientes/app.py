import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session
from crud.cliente_crud import ClienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
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
        self.tab_clientes = self.tabview.add("Clientes")
        self.init_clientes_tab(self.tab_clientes)

        self.tab_menu = self.tabview.add("Menú")
        self.init_menu_tab(self.tab_menu)

        self.tab_panel_compra = self.tabview.add("Panel de Compra")
        self.init_panel_compra_tab(self.tab_panel_compra)

        self.tab_pedidos = self.tabview.add("Pedidos")
        self.init_pedidos_tab(self.tab_pedidos)

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

    # --- Pestaña de Menú ---
    def init_menu_tab(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gestión del Menú").pack(pady=10, padx=10)

    # --- Pestaña de Panel de Compra ---
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

    # --- Pestaña de Pedidos ---
    def init_pedidos_tab(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Gestión de Pedidos").pack(pady=10, padx=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
