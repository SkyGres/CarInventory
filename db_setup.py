import sqlite3
import logging


def init_db(conn):
    logging.debug("Initializing database")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vin TEXT UNIQUE NOT NULL,
            make TEXT,
            model TEXT,
            model_year TEXT,
            series TEXT,
            options TEXT,
            key_features TEXT,
            stock_number TEXT
        )
    ''')
    conn.commit()
    logging.debug("Database initialized successfully")


def init_archive_db(conn):
    logging.debug("Initializing archive database")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vin TEXT UNIQUE NOT NULL,
            make TEXT,
            model TEXT,
            model_year TEXT,
            series TEXT,
            options TEXT,
            key_features TEXT,
            stock_number TEXT
        )
    ''')
    conn.commit()
    logging.debug("Archive database initialized successfully")


if __name__ == "__main__":
    conn = sqlite3.connect('car_inventory.db')
    init_db(conn)
    conn.close()

    archive_conn = sqlite3.connect('car_archive.db')
    init_archive_db(archive_conn)
    archive_conn.close()