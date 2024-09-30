import tkinter as tk
from tkinter import ttk, messagebox
from database.connector import DatabaseConnector
from gui.second_window import SecondWindow
from utils.helper_functions import validate_document
from config import ICON_PATH
from datetime import datetime
import mysql.connector

class MainView(tk.Tk):
    def __init__(self, db_connector: DatabaseConnector):
        super().__init__()
        self.db_connector = db_connector
        self.title("Sistema PAE")
        self.geometry("1000x800")
        self.iconbitmap(ICON_PATH)
        self.create_widgets()

    def create_widgets(self):
        # Configurar estilos para ttk.Label
        style = ttk.Style()
        style.theme_use('clam')  # Cambia el tema si es necesario

        # Definir un estilo personalizado llamado "Custom.TLabel"
        style.configure("Custom.TLabel",
                        foreground="black",
                        background="gray85")

        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame información del estudiante
        info_frame = tk.LabelFrame(main_frame, text="Información del Estudiante", padx=10, pady=10, bg="gray85")
        info_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.fields = ['Documento', 'Nombres', 'Apellidos', 'Grado']
        self.entries = {}

        for i, field in enumerate(self.fields):
            # Usar ttk.Label con el estilo personalizado
            label = ttk.Label(info_frame, text=field, style="Custom.TLabel")
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)

            # Usar ttk.Entry para los campos de entrada
            entry = ttk.Entry(info_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[field] = entry

        # Frame de botones CRUD
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(button_frame, text="Buscar", command=self.search_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Insertar", command=self.insert_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Borrar", command=self.delete_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mostrar Todos", command=self.show_all_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # Botón para abrir la segunda ventana
        ttk.Button(button_frame, text="Escáner", command=self.open_second_window).pack(side=tk.LEFT, padx=5)

        # Treeview para mostrar estudiantes
        tree_frame = tk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=self.fields, show="headings")
        for field in self.fields:
            self.tree.heading(field, text=field)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configurar expansión de filas y columnas
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def search_estudiante(self):
        documento = self.entries['Documento'].get()

        if validate_document(documento):
            query = "SELECT Documento, Nombres, Apellidos, Grado FROM Estudiantes WHERE Documento = %s"
            result = self.db_connector.execute_query(query, (documento,))

            if result:
                self.display_results(result)
            else:
                messagebox.showinfo("Información", "No se encontró el estudiante con ese documento")
        else:
            messagebox.showwarning("Advertencia", "El documento debe ser un número válido")

    def insert_estudiante(self):
        documento = self.entries['Documento'].get()
        nombres = self.entries['Nombres'].get()
        apellidos = self.entries['Apellidos'].get()
        grado = self.entries['Grado'].get()

        if validate_document(documento):
            query = "INSERT INTO Estudiantes (Documento, Nombres, Apellidos, Grado) VALUES (%s, %s, %s, %s)"
            try:
                self.db_connector.execute_query(query, (documento, nombres, apellidos, grado))
                messagebox.showinfo("Información", "Estudiante insertado correctamente")
                self.clear_fields()
                self.show_all_estudiante()
            except mysql.connector.errors.IntegrityError as e:
                if "Duplicate entry" in str(e):
                    messagebox.showwarning("Advertencia", "Ya existe un estudiante con el mismo documento.")
                else:
                    messagebox.showerror("Error", f"Error en la base de datos: {e}")
        else:
            messagebox.showwarning("Advertencia", "El documento debe ser un número válido")

    def update_estudiante(self):
        documento = self.entries['Documento'].get()
        nombres = self.entries['Nombres'].get()
        apellidos = self.entries['Apellidos'].get()
        grado = self.entries['Grado'].get()

        if validate_document(documento):
            query = "UPDATE Estudiantes SET Nombres = %s, Apellidos = %s, Grado = %s WHERE Documento = %s"
            self.db_connector.execute_query(query, (nombres, apellidos, grado, documento))
            messagebox.showinfo("Información", "Estudiante actualizado correctamente")
            self.clear_fields()
            self.show_all_estudiante()
        else:
            messagebox.showwarning("Advertencia", "El documento debe ser un número válido")

    def delete_estudiante(self):
        documento = self.entries['Documento'].get()

        if validate_document(documento):
            # Primero, eliminar las acciones del estudiante
            delete_actions_query = "DELETE FROM EstudiantesActions WHERE Documento = %s"
            self.db_connector.execute_query(delete_actions_query, (documento,))

            # Luego, eliminar al estudiante
            delete_estudiante_query = "DELETE FROM Estudiantes WHERE Documento = %s"
            self.db_connector.execute_query(delete_estudiante_query, (documento,))

            messagebox.showinfo("Información", "Estudiante y sus acciones eliminados correctamente")
            self.clear_fields()
            self.show_all_estudiante()
        else:
            messagebox.showwarning("Advertencia", "El documento debe ser un número válido")

    def show_all_estudiante(self):
        query = "SELECT Documento, Nombres, Apellidos, Grado FROM Estudiantes ORDER BY Apellidos, Nombres"
        result = self.db_connector.execute_query(query)

        if result:
            self.display_results(result)

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def open_second_window(self):
        SecondWindow(self.db_connector)

    def display_results(self, rows):
        # Limpiar el TreeView antes de mostrar nuevos resultados
        self.tree.delete(*self.tree.get_children())

        for row in rows:
            self.tree.insert("", "end", values=row)
