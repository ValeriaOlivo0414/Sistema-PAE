from database.connector import DatabaseConnector
from gui.main_window import MainView

def main():
    db_connector = DatabaseConnector(
        host="localhost",
        user="root",
        password="1234",
        database="sistemapae"
    )

    app = MainView(db_connector)
    app.mainloop()

if __name__ == "__main__":
    main()

