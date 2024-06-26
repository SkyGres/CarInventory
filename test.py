import sqlite3

def fetch_archived_cars(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM archived_cars')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Error fetching archived cars: {e}")

# Example usage
archive_conn = sqlite3.connect('car_archive.db')
fetch_archived_cars(archive_conn)
archive_conn.close()