import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session
from crud.cliente_crud import *
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
