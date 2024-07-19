import json
import logging
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from home_page import HomePage
from inventory_page import InventoryPage
from add_car_page import AddCarPage
from settings_page import SettingsPage
from archive_page import ArchivePage
from car_details_page import CarDetailsPage
import sv_ttk  # Assuming sv_ttk provides set_theme() function


class CarInventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize main database connection and cursor
        self.conn = sqlite3.connect('car_inventory.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Initialize archive database connection and cursor
        self.archive_conn = sqlite3.connect('car_archive.db')
        self.archive_cursor = self.archive_conn.cursor()

        # Initialize logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logging.debug("Initializing CarInventoryApp")
        self.title("Car Inventory Management")
        self.minsize(1200, 600)  # Set a minimum size of 1200x600 pixels

        # Set window icon
        try:
            self.iconbitmap(default="logo.ico")  # Replace "logo.ico" with your actual icon file path
            logging.debug("Icon loaded successfully")
        except tk.TclError:
            logging.error("Icon file 'logo.ico' not found. Please check the file path.")

        # Initialize the SQLite databases
        self.init_db()
        self.init_archive_db()  # Call to initialize archive database

        # Load car options from JSON file
        try:
            with open('car_options.json', 'r') as f:
                self.car_options = json.load(f)
                logging.debug("Car options loaded successfully")
        except FileNotFoundError:
            logging.error("Car options file 'car_options.json' not found.")

        # default light mode
        sv_ttk.use_light_theme()

        # Create main container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(container, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_content = ttk.Frame(container)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.frames = {}
        for F in (HomePage, InventoryPage, AddCarPage, SettingsPage, ArchivePage):
            page_name = F.__name__
            frame = F(parent=self.main_content, controller=self)
            self.frames[page_name] = frame
            logging.debug(f"Frame {page_name} initialized")

        self.add_sidebar_buttons()
        self.show_frame("HomePage")

    def add_sidebar_buttons(self):
        home_button = ttk.Button(self.sidebar, text="Home", command=lambda: self.show_frame("HomePage"))
        home_button.pack(fill="x", pady=10)

        inventory_button = ttk.Button(self.sidebar, text="Inventory", command=lambda: self.show_frame("InventoryPage"))
        inventory_button.pack(fill="x", pady=10)

        archive_button = ttk.Button(self.sidebar, text="Archive", command=lambda: self.show_frame("ArchivePage"))
        archive_button.pack(pady=10, fill="x")

        settings_button = ttk.Button(self.sidebar, text="Settings", command=lambda: self.show_frame("SettingsPage"))
        settings_button.pack(fill="x", pady=10)

    def show_frame(self, page_name, **kwargs):
        logging.debug(f"show_frame called with page_name={page_name} and kwargs={kwargs}")

        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
            if isinstance(frame, InventoryPage) or isinstance(frame, ArchivePage):
                frame.unbind_mousewheel(frame.canvas)

        # Dynamically create or update the requested frame
        if page_name not in self.frames or 'vin' in kwargs:
            # Check if the frame needs to be created or updated with new details
            if page_name == "CarDetailsPage":
                frame = CarDetailsPage(parent=self.main_content, controller=self, **kwargs)
            else:
                frame = self.frames.get(page_name, None)
                if frame is None:
                    # Create other pages normally if not already created
                    frame = self.create_page(
                        page_name)  # You should define create_page method or add specific conditions
            # Store the new or updated frame
            self.frames[page_name] = frame
        else:
            frame = self.frames[page_name]

        # Pack and show the requested frame
        frame.pack(fill="both", expand=True)

        # Optionally call a refresh method if applicable, like for inventory or archive pages
        if page_name in ("InventoryPage", "ArchivePage"):
            frame.update_inventory_list()
            frame.bind_mousewheel(frame.canvas)

    def create_page(self, page_name):
        """
        Dynamically creates a page based on the page_name provided.
        """
        # Import frame classes at the top of your file to avoid circular imports
        from home_page import HomePage
        from inventory_page import InventoryPage
        from add_car_page import AddCarPage
        from settings_page import SettingsPage
        from archive_page import ArchivePage
        from car_details_page import CarDetailsPage

        # Dictionary mapping page names to class constructors
        pages = {
            "HomePage": HomePage,
            "InventoryPage": InventoryPage,
            "AddCarPage": AddCarPage,
            "SettingsPage": SettingsPage,
            "ArchivePage": ArchivePage,
            "CarDetailsPage": CarDetailsPage
        }

        # Get the class from the dictionary and instantiate it
        page_class = pages.get(page_name)
        if page_class:
            return page_class(parent=self.main_content, controller=self)
        else:
            logging.error(f"No page found for {page_name}")
            raise ValueError(f"No page found for {page_name}")

    def init_db(self):
        logging.debug("Initializing database")
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vin TEXT UNIQUE NOT NULL,
                make TEXT,
                model TEXT,
                model_year TEXT,
                series TEXT,
                options TEXT,
                key_features TEXT,
                stock_number TEXT,
                wheel_size TEXT,
                alloy_wheels BOOLEAN,
                two_tone_wheels BOOLEAN,
                chrome_wheels BOOLEAN,
                wheels BOOLEAN,
                custom_wheels TEXT,
                is_wheel_key_feature BOOLEAN
            )
        ''')
        self.conn.commit()
        logging.debug("Database initialized successfully")

    def init_archive_db(self):
        try:
            self.archive_cursor.execute('''
                CREATE TABLE IF NOT EXISTS archived_cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vin TEXT UNIQUE NOT NULL,
                    make TEXT,
                    model TEXT,
                    model_year TEXT,
                    series TEXT,
                    options TEXT,
                    key_features TEXT,
                    stock_number TEXT,
                    wheel_size TEXT,
                    alloy_wheels BOOLEAN,
                    two_tone_wheels BOOLEAN,
                    chrome_wheels BOOLEAN,
                    wheels BOOLEAN,
                    custom_wheels TEXT,
                    is_wheel_key_feature BOOLEAN
                )
            ''')
            self.archive_conn.commit()
            logging.debug("Archive database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Error initializing archive database: {e}")

    def insert_car(self, vin, make, model, model_year, series, options, key_features, stock_number):
        try:
            self.cursor.execute('''
                INSERT INTO inventory (vin, make, model, model_year, series, options, key_features, stock_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vin, make, model, model_year, series, options, key_features, stock_number))
            self.conn.commit()
            logging.debug(f"Inserted car with VIN: {vin}")
        except sqlite3.IntegrityError as e:
            logging.error(f"Error inserting car with VIN {vin}: {e}")
            raise ValueError("Car with this VIN already exists in the inventory.")

    def update_car_options(self, vin, options):
        try:
            self.cursor.execute('''
                UPDATE inventory
                SET options = ?
                WHERE vin = ?
            ''', (options, vin))
            self.conn.commit()
            logging.debug(f"Updated options for car with VIN {vin}")
        except sqlite3.Error as e:
            raise ValueError(f"Failed to update car options: {e}")

    def update_car_details(self, vin, **details):
        query = "UPDATE inventory SET "
        query += ", ".join(f"{key} = ?" for key in details.keys())
        query += " WHERE vin = ?"
        params = list(details.values()) + [vin]
        try:
            logging.debug(f"Executing SQL query: {query} with params {params}")
            self.cursor.execute(query, params)
            self.conn.commit()
            logging.debug("Car details updated successfully")
        except sqlite3.Error as e:
            logging.error(f"Failed to update car details: {e}")
            raise ValueError(f"Failed to update: {e}")

    def fetch_cars(self):
        self.cursor.execute('SELECT * FROM inventory')
        return self.cursor.fetchall()

    def fetch_archived_cars(self):
        self.archive_cursor.execute("SELECT * FROM archived_cars")
        return self.archive_cursor.fetchall()

    def close_db(self):
        self.conn.close()
        self.archive_conn.close()
        logging.debug("Database connections closed")

    def archive_car(self, car):
        vin = car[1]
        car_details = car[1:]

        try:
            self.archive_cursor.execute('''
                INSERT INTO archived_cars (vin, make, model, model_year, series, options, key_features, stock_number, 
                wheel_size, alloy_wheels, two_tone_wheels, chrome_wheels, wheels, custom_wheels, is_wheel_key_feature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', car_details)
            self.archive_conn.commit()
            logging.debug(f"Archived car with VIN: {vin}")
            self.delete_car(vin)
        except sqlite3.Error as e:
            logging.error(f"Error archiving car with VIN {vin}: {e}")
            messagebox.showerror("Error", f"Failed to archive car with VIN {vin}")

    def delete_car(self, vin):
        try:
            self.cursor.execute("DELETE FROM inventory WHERE vin = ?", (vin,))
            self.conn.commit()
            logging.debug(f"Car with VIN {vin} deleted from inventory")
        except sqlite3.Error as e:
            logging.error(f"Error deleting car with VIN {vin}: {e}")
            messagebox.showerror("Error", f"Failed to delete car with VIN {vin}")

    def fetch_car_by_vin(self, vin):
        try:
            self.cursor.execute("SELECT * FROM inventory WHERE vin = ?", (vin,))
            car = self.cursor.fetchone()
            logging.debug(f"Fetched car details for VIN {vin}: {car}")
            return car
        except sqlite3.Error as e:
            logging.error(f"Error fetching car with VIN {vin}: {e}")
            return None

    def insert_car_into_inventory(self, car):
        try:
            self.cursor.execute('''
                INSERT INTO inventory (vin, make, model, model_year, series, options, key_features, stock_number, wheel_size, alloy_wheels, two_tone_wheels, chrome_wheels, wheels, custom_wheels, is_wheel_key_feature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', car[1:])
            self.conn.commit()
            logging.debug(f"Inserted car with VIN: {car[1]} back into inventory")
        except sqlite3.IntegrityError as e:
            logging.error(f"Error inserting car with VIN {car[1]}: {e}")
            raise ValueError("Car with this VIN already exists in the inventory.")

    def delete_car_from_archive(self, vin):
        try:
            self.archive_cursor.execute('''
                DELETE FROM archived_cars WHERE vin = ?
            ''', (vin,))
            self.archive_conn.commit()
            logging.debug(f"Deleted car with VIN: {vin} from archive")
        except sqlite3.Error as e:
            logging.error(f"Error deleting car with VIN {vin} from archive: {e}")
            raise ValueError(f"Failed to delete car from archive: {e}")