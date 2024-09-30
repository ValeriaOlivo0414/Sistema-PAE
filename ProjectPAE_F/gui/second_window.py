import tkinter as tk
from tkinter import ttk, messagebox
from tabulate import tabulate
from datetime import datetime
from config import ICON_PATH

class SecondWindow(tk.Toplevel):
    def __init__(self, db_connector):
        super().__init__()
        self.db_connector = db_connector
        self.title("Lectura con Código de Barras")
        self.geometry("1000x600")
        self.iconbitmap(ICON_PATH)
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Campo para el código de barras
        barcode_frame = tk.LabelFrame(main_frame, text="Escanear Código de Barras", padx=10, pady=10, bg="gray85")
        barcode_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.barcode_entry = ttk.Entry(barcode_frame, width=40)
        self.barcode_entry.grid(row=0, column=0, padx=5, pady=5)
        self.barcode_entry.bind("<Return>", self.handle_barcode_scan)

        # Campo para ingresar la fecha y grado
        filter_frame = tk.LabelFrame(main_frame, text="Filtrar por Fecha y Grado", padx=10, pady=10, bg="gray85")
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Filtro de fecha y grado en la misma fila
        ttk.Label(filter_frame, text="Fecha:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.date_entry = ttk.Entry(filter_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Grado:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.grade_entry = ttk.Entry(filter_frame, width=20)
        self.grade_entry.grid(row=0, column=3, padx=5, pady=5)

        # Botón para filtrar por fecha y grado
        self.search_button = ttk.Button(filter_frame, text="Buscar por Filtros", command=self.handle_date_search)
        self.search_button.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Botón para marcar acciones como "No reclamado"
        self.mark_no_reclamado_button = ttk.Button(filter_frame, text="Finalizar Listado",
                                                   command=self.handle_mark_no_reclamado)
        self.mark_no_reclamado_button.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

        # Treeview para mostrar resultados del estudiante y la fecha
        tree_frame = tk.Frame(main_frame)
        tree_frame.grid(row=3, column=0, sticky="nsew", pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Documento", "Nombres", "Apellidos", "Grado", "Acción", "Fecha"),
                                 show="headings")
        self.tree.heading("Documento", text="Documento")
        self.tree.heading("Nombres", text="Nombres")
        self.tree.heading("Apellidos", text="Apellidos")
        self.tree.heading("Grado", text="Grado")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Acción", text="Acción")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configurar expansión de filas y columnas
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def handle_barcode_scan(self, event):
        """Este método maneja la lectura del código de barras"""
        barcode = self.barcode_entry.get()
        action_date = self.date_entry.get() or datetime.now().strftime('%Y-%m-%d')  # Tomar la fecha actual si no se ingresa

        if not barcode.isdigit():
            messagebox.showwarning("Advertencia", "El código de barras debe ser tu Documento de Identidad")
            return

        # Ejecutar el procedimiento almacenado con el código de barras y la fecha ingresada
        results = self.db_connector.execute_procedure('FuncionEstudiantesAction', barcode)

        if results:
            for headers, rows in results:
                self.display_results(headers, rows)
        else:
            messagebox.showinfo("Información", "No puedes registrarte fuera de los horarios permitidos")

        # Limpiar el campo de entrada para el siguiente código de barras
        self.barcode_entry.delete(0, tk.END)

    def handle_date_search(self):
        """Este método filtra las acciones por la fecha y opcionalmente por grado"""
        action_date = self.date_entry.get()
        student_grade = self.grade_entry.get() or 'Todos'  # Tomar 'Todos' como valor predeterminado si el campo está vacío

        # Validar si se ingresó una fecha en el formato correcto
        try:
            datetime.strptime(action_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Advertencia", "La fecha debe ser de la manera YYYY-MM-DD")
            return

        # Ejecutar el procedimiento para filtrar por la fecha y opcionalmente por grado
        results = self.db_connector.execute_procedure('FuncionEstudiantesActionByDate', action_date, student_grade)

        if results:
            for headers, rows in results:
                self.display_results(headers, rows)
        else:
            messagebox.showinfo("Información", "No se encontraron resultados de esta fecha y grado")

    def handle_mark_no_reclamado(self):
        """Este método marca las acciones faltantes como 'No reclamado'"""
        action_date = self.date_entry.get() or datetime.now().strftime('%Y-%m-%d')

        # Validar si se ingresó una fecha en el formato correcto
        try:
            datetime.strptime(action_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Advertencia", "La fecha debe tener el formato YYYY-MM-DD")
            return

        # Ejecutar el procedimiento para marcar las acciones como no reclamadas
        self.db_connector.execute_procedure('MarcarNoReclamado', action_date)

        # Informar al usuario que las acciones se han marcado como "No reclamado"
        messagebox.showinfo("Finalización", "Los estudiantes faltantes han sido marcados como 'No reclamado'")

    def display_results(self, headers, rows):
        # Limpiar el TreeView antes de mostrar nuevos resultados
        self.tree.delete(*self.tree.get_children())

        for row in rows:
            self.tree.insert("", "end", values=row)
