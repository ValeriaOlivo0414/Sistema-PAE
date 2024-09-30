import mysql.connector
from mysql.connector import Error
from typing import Any, List, Tuple
from tkinter import messagebox

class DatabaseConnector:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        """Realiza la conexión a la base de datos"""
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        print("Conexión establecida a la base de datos")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        """Ejecuta una consulta SQL"""
        try:
            self.connect()
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            self.connection.commit()
            return rows
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
            return []
        finally:
            self.connection.close()

    def execute_procedure(self, procedure_name: str, *args) -> List[Tuple[List[str], List[Tuple[Any, ...]]]]:
        """Ejecuta un procedimiento almacenado"""
        try:
            self.connect()
            self.cursor.callproc(procedure_name, args)

            results = []
            for result in self.cursor.stored_results():
                results.append((result.column_names, result.fetchall()))
            self.connection.commit()
            return results
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
            return []
        finally:
            self.connection.close()