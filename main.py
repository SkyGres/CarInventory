import logging
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

import json
import pyperclip
import requests
import sv_ttk  # Assuming sv_ttk provides set_theme() function
import time

# Clear the existing log file by opening it in 'w' mode
with open('car_inventory.log', 'w'):
    pass

logging.basicConfig(
    filename='car_inventory.log',  # Log file path
    level=logging.DEBUG,  # Log all debug messages and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)


class CarInventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize main database connection and cursor
        self.conn = sqlite3.connect('car_inventory.db')
        self.cursor = self.conn.cursor()

        # Initialize archive database connection and cursor
        self.archive_conn = sqlite3.connect('car_archive.db')
        self.archive_cursor = self.archive_conn.cursor()

        # Initialize logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logging.debug("Initializing CarInventoryApp")
        self.title("Car Inventory Management")
        self.minsize(800, 600)  # Set a minimum size of 800x600 pixels

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
        for F in (HomePage, InventoryPage, AddCarPage, SettingsPage, CarOptionsPage, ArchivePage):
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

    def show_frame(self, page_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
            if isinstance(frame, InventoryPage) or isinstance(frame, ArchivePage):
                frame.unbind_mousewheel(frame.canvas)

        # Show the requested frame
        frame = self.frames[page_name]
        frame.pack(fill="both", expand=True)

        # Call the refresh method if the frame is InventoryPage or ArchivePage
        if page_name in ("InventoryPage", "ArchivePage"):
            frame.update_inventory_list()
            frame.bind_mousewheel(frame.canvas)

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
                key_features TEXT
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
                    key_features TEXT
                )
            ''')
            self.archive_conn.commit()
            logging.debug("Archive database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Error initializing archive database: {e}")

    def insert_car(self, vin, make, model, model_year, series, options, key_features):
        try:
            self.cursor.execute('''
                INSERT INTO inventory (vin, make, model, model_year, series, options, key_features)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vin, make, model, model_year, series, options, key_features))
            self.conn.commit()
            logging.debug(f"Car with VIN {vin} inserted into inventory")
        except sqlite3.IntegrityError:
            raise ValueError(f"Car with VIN {vin} already exists in the inventory.")

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
                INSERT INTO archived_cars (vin, make, model, model_year, series, options, key_features)
                VALUES (?, ?, ?, ?, ?, ?, ?)
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
            return car
        except sqlite3.Error as e:
            logging.error(f"Error fetching car with VIN {vin}: {e}")


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        try:
            self.logo_image = tk.PhotoImage(file='logo.png').subsample(3)
        except tk.TclError:
            logging.debug("Logo file 'logo.png' not found. Please check the file path.")
            self.logo_image = None

        # Display the logo image if available
        if self.logo_image:
            logo_label = ttk.Label(self, image=self.logo_image)
            logo_label.pack()
            logging.debug("Logo is added successfully")

        # Centered Label
        label = ttk.Label(self, text="Home Page", font=("Arial", 24))
        label.pack(expand=True)
        logging.debug("Home Page label created")

        # Add a New Car Button
        add_car_button = ttk.Button(self, text="Add a New Car", command=lambda: controller.show_frame("AddCarPage"))
        add_car_button.pack(pady=20)
        logging.debug("Add Car button created")


class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.notification_frame = NotificationFrame(self)

        # Create a Canvas widget to hold the scrollable area
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the inventory list
        self.inventory_container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inventory_container, anchor="nw")

        # Bind the canvas to make it scrollable with mouse wheel
        self.bind_mousewheel(self.canvas)

        # Configure event for updating scroll region
        self.inventory_container.bind("<Configure>",
                                      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.update_inventory_list()

    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        # Perform vertical scrolling with mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def unbind_mousewheel(self, widget):
        self.unbind_all("<MouseWheel>")

    def update_inventory_list(self):
        # Clear the previous inventory list
        for widget in self.inventory_container.winfo_children():
            widget.destroy()
        logging.debug("Previous inventory list cleared")

        cars = self.controller.fetch_cars()
        for car in cars:
            car_frame = ttk.Frame(self.inventory_container, borderwidth=2, relief="groove")
            car_frame.pack(fill="x", padx=10, pady=5, expand=True)
            logging.debug(f"Created frame for car: {car}")

            # Main clickable area representing the car
            car_button = ttk.Button(car_frame,
                                    text=f"{car[2]} {car[3]} ({car[4]}) - {car[5]}",
                                    command=lambda c=car: self.show_car_details(c))
            car_button.pack(side="left", fill="both", expand=True)
            logging.debug(f"Added main clickable area for car: {car}")

            # Frame for quick action buttons
            action_frame = ttk.Frame(car_frame)
            action_frame.pack(side="right", fill="y")
            logging.debug(f"Created frame for quick action buttons for car: {car}")

            # Copy Text button
            copy_button = ttk.Button(action_frame, text="Copy Text", command=lambda c=car: self.copy_text(c))
            copy_button.pack(fill="x", pady=5)

            # Archive button
            archive_button = ttk.Button(action_frame, text="Archive", command=lambda c=car: self.archive_car(c))
            archive_button.pack(fill="x", pady=5)

            delete_button = ttk.Button(action_frame, text="Delete", command=lambda c=car: self.delete_car(c))
            delete_button.pack(fill="x", pady=5)
            logging.debug(f"Added Delete button for car: {car}")

    def show_car_details(self, car):
        self.controller.show_car_details(car)
        logging.debug(f"Showing details for car: {car}")

    def copy_text(self, car):
        car_details = f"{car[2]} {car[3]} ({car[4]}) - {car[5]}"
        pyperclip.copy(car_details)
        logging.debug(f"Copied car details to clipboard: {car_details}")
        self.notification_frame.add_notification("Car details copied to clipboard!")

    def archive_car(self, car):
        # Implement archive functionality here
        logging.debug(f"Archiving car: {car}")
        self.controller.archive_car(car)
        self.update_inventory_list()  # Update the inventory list after archiving

    def delete_car(self, car):
        # Implement delete functionality here
        vin = car[1]
        print(f"Deleting car: {car}")
        logging.debug(f"Deleting car: {car}")

        # Confirm deletion
        if messagebox.askyesno("Delete Car", f"Are you sure you want to delete the car with VIN: {vin}?"):
            self.controller.delete_car(vin)
            logging.debug(f"Deleted car with VIN: {vin}")
            self.update_inventory_list()
            self.notification_frame.add_notification(f"Car with VIN {vin} deleted successfully!")


class ArchivePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.notification_frame = NotificationFrame(self)

        # Create a Canvas widget to hold the scrollable area
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the archive list
        self.archive_container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.archive_container, anchor="nw")

        # Bind the canvas to make it scrollable with mouse wheel
        self.bind_mousewheel(self.canvas)

        # Configure event for updating scroll region
        self.archive_container.bind("<Configure>",
                                    lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.update_inventory_list()

    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        # Perform vertical scrolling with mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def unbind_mousewheel(self, widget):
        self.unbind_all("<MouseWheel>")

    def update_inventory_list(self):
        # Clear the previous inventory list
        for widget in self.archive_container.winfo_children():
            widget.destroy()

        cars = self.controller.fetch_archived_cars()
        for car in cars:
            car_frame = ttk.Frame(self.archive_container, borderwidth=2, relief="groove")
            car_frame.pack(fill="x", padx=10, pady=5, expand=True)

            # Main clickable area representing the car
            car_button = ttk.Button(car_frame,
                                    text=f"{car[2]} {car[3]} ({car[4]}) - {car[5]}",
                                    command=lambda c=car: self.show_car_details(c))
            car_button.pack(side="left", fill="both", expand=True)

            # Frame for quick action buttons
            action_frame = ttk.Frame(car_frame)
            action_frame.pack(side="right", fill="y")

            # Copy Text button
            copy_button = ttk.Button(action_frame, text="Copy Text", command=lambda c=car: self.copy_text(c))
            copy_button.pack(fill="x", pady=5)

    def show_car_details(self, car):
        self.controller.show_car_details(car)

    def copy_text(self, car):
        car_details = f"{car[2]} {car[3]} ({car[4]}) - {car[5]}"
        pyperclip.copy(car_details)
        self.notification_frame.add_notification("Car details copied to clipboard!")
        logging.debug(f"Copied car details to clipboard: {car_details}")


class AddCarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Centered Label
        label = ttk.Label(self, text="Add Car Page", font=("Arial", 24))
        label.pack(expand=True)
        logging.debug("Add Car Page initialized")

        # VIN Entry
        vin_label = ttk.Label(self, text="Enter VIN:")
        vin_label.pack(pady=10)
        logging.debug("VIN label created")

        self.vin_entry = ttk.Entry(self)
        self.vin_entry.pack()
        logging.debug("VIN entry field created")
        # Bind the Enter key to trigger enter_vin method when the Entry widget has focus
        self.vin_entry.bind("<Return>", lambda event: self.enter_vin())

        # Enter Button
        enter_button = ttk.Button(self, text="Enter", command=self.enter_vin)
        enter_button.pack(pady=20)
        logging.debug("Enter button created")

        # Button to go back to home page
        button = ttk.Button(self, text="Go to Home Page", command=lambda: controller.show_frame("HomePage"))
        button.pack(pady=20)
        logging.debug("Go to Home Page button created")


    def enter_vin(self):
        vin = self.vin_entry.get().upper()  # Convert VIN to uppercase for consistency
        logging.debug(f"Entered VIN: {vin}")

        # Check for invalid characters in the VIN
        if any(char in vin for char in "IOQ"):
            messagebox.showerror("Error", "VIN cannot contain the characters I, O, or Q.")
            logging.debug("Invalid VIN characters detected")
            return

        # Check if the VIN exceeds 17 characters
        if len(vin) > 17 or len(vin) < 11:
            messagebox.showerror("Error", "VIN cannot be less than 11 or exceed 17 characters.")
            logging.debug("Invalid VIN length detected")
            return

        url = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
        post_fields = {'format': 'json', 'data': vin}
        r = requests.post(url, data=post_fields)
        logging.debug("API request sent to decode VIN")

        # Parse the JSON response
        response_data = r.json()

        # Extract specific fields
        if response_data["Count"] > 0:
            result = response_data["Results"][0]
            make = result.get("Make", "N/A")
            model = result.get("Model", "N/A")
            model_year = result.get("ModelYear", "N/A")
            series = result.get("Series", "N/A")

            # Insert car data into the database
            try:
                self.controller.insert_car(vin, make, model, model_year, series, "", "")
                logging.debug("Car data inserted into the database")

                # Print the extracted fields
                logging.debug(f"Make: {make}")
                logging.debug(f"Model: {model}")
                logging.debug(f"Model Year: {model_year}")
                logging.debug(f"Series: {series}")

                # Show the CarOptionsPage with the VIN passed
                self.controller.frames['CarOptionsPage'].set_vin(vin)
                self.controller.show_frame("CarOptionsPage")

            except ValueError as e:
                messagebox.showerror("Error", str(e))
                logging.error(f"Error inserting car data: {e}")

        else:
            messagebox.showerror("Error", "No results found for the entered VIN.")
            logging.debug("No results found for the entered VIN")


class CarOptionsPage(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vin = None
        self.controller = controller

        logging.debug("Initializing CarOptionsPage")

        # Create a canvas widget and a vertical scrollbar
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Frame to contain all the checkboxes
        self.options_frame = ttk.Frame(self.canvas)

        # Use a window to scroll the frame
        self.options_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.options_frame,
            anchor="nw"
        )

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        # Bind the canvas to make it scrollable with mouse wheel
        self.bind_mousewheel(self.canvas)

        # Create the label inside options_frame
        label = ttk.Label(self.options_frame, text="Select Car Options", font=("Arial", 24))
        label.pack(expand=True, pady=10, padx=10)
        logging.debug("Car options label created")

        # Create checkboxes dynamically based on car options loaded from JSON
        self.checkboxes = {}
        for category, options in controller.car_options.items():
            category_frame = ttk.LabelFrame(self.options_frame, text=category)
            category_frame.pack(pady=10, padx=10, fill="both", expand=True)
            logging.debug(f"Created category frame for: {category}")

            for option in options:
                var = tk.BooleanVar(value=False)
                checkbox = ttk.Checkbutton(category_frame, text=option, variable=var)
                checkbox.pack(anchor="w", padx=10)
                self.checkboxes[option] = var
                logging.debug(f"Created checkbox for option: {option}")

        # Enter Button
        enter_button = ttk.Button(self.options_frame, text="Enter", command=self.save_options)
        enter_button.pack(pady=20)
        logging.debug("Enter button created")

        # Button to go back to home page
        button = ttk.Button(self.options_frame, text="Go to Home Page",
                            command=lambda: controller.show_frame("HomePage"))
        button.pack(pady=20)
        logging.debug("Go to Home Page button created")

    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        # Perform vertical scrolling with mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def unbind_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")

    def set_vin(self, vin):
        self.vin = vin
        logging.debug(f"VIN set to: {vin}")

    def save_options(self):
        selected_options = [option for option, var in self.checkboxes.items() if var.get()]
        logging.debug(f"Selected options: {selected_options}")

        options_text = ", ".join(selected_options)
        self.controller.update_car_options(self.vin, options_text)
        logging.debug(f"Updated car options for VIN {self.vin} with: {options_text}")

        messagebox.showinfo("Success", "Car options updated successfully!")
        self.controller.show_frame("HomePage")
        logging.debug("Car options saved and user redirected to HomePage")


class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        logging.debug("Initializing SettingsPage")

        label = ttk.Label(self, text="Settings", font=("Arial", 24))
        label.pack(pady=10)
        logging.debug("Settings label created")

        # Load categories and features from JSON file
        try:
            with open('car_options.json', 'r') as f:
                self.car_options = json.load(f)
                logging.debug("Loaded car_options.json successfully")
        except FileNotFoundError:
            logging.error("car_options.json not found")
            self.car_options = {}

        # Dropdown menu for feature categories
        categories_label = ttk.Label(self, text="Choose Category:")
        categories_label.pack(pady=5)
        logging.debug("Category label created")

        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self, textvariable=self.category_var)
        self.category_dropdown['values'] = list(self.car_options.keys())
        self.category_dropdown.pack()
        logging.debug("Category dropdown created")

        # Dropdown menu for features
        features_label = ttk.Label(self, text="Enter Feature:")
        features_label.pack(pady=5)
        logging.debug("Feature label created")

        self.feature_var = tk.StringVar()
        self.feature_input = ttk.Entry(self, textvariable=self.feature_var)
        self.feature_input.pack()
        logging.debug("Feature input created")

        # Button to save feature
        save_button = ttk.Button(self, text="Save Feature", command=self.save_feature)
        save_button.pack(pady=20)
        logging.debug("Save button created")

        button = ttk.Button(self, text="Toggle theme", command=sv_ttk.toggle_theme)
        button.pack(pady=10)
        logging.debug("Toggle theme button created")

    def save_feature(self):
        selected_category = self.category_var.get()
        selected_feature = self.feature_var.get()
        logging.debug(f"Saving feature: {selected_feature} to category: {selected_category}")

        if selected_category in self.car_options:
            self.car_options[selected_category].append(selected_feature)
            logging.debug(f"Feature '{selected_feature}' added to '{selected_category}'")
        else:
            self.car_options[selected_category] = [selected_feature]
            logging.debug(f"Created new category '{selected_category}' and added feature '{selected_feature}'")

        # Save updated car features back to JSON file
        try:
            with open('car_options.json', 'w') as f:
                json.dump(self.car_options, f, indent=4)
                logging.debug("Saved updated car_options.json successfully")
        except IOError as e:
            logging.error(f"Failed to save car_options.json: {e}")

        # Clear feature entry after saving
        self.feature_input.delete(0, tk.END)
        logging.debug("Cleared feature input field")


class NotificationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightgray", height=50)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self.notifications = []

    def add_notification(self, message):
        notification_label = ttk.Label(self, text=message, background="lightgreen", anchor="center", padding=(5, 2))
        notification_label.pack(fill=tk.X)
        self.notifications.append(notification_label)

        # Automatically remove the notification after 3 seconds
        self.after(3000, lambda: self.remove_notification(notification_label))

    def remove_notification(self, notification_label):
        notification_label.destroy()
        self.notifications.remove(notification_label)


if __name__ == "__main__":
    logging.debug("Starting Car Inventory application.")
    try:
        app = CarInventoryApp()
        app.mainloop()
        logging.debug("Application main loop running.")
    except Exception as e:
        logging.exception("An error occurred while running the application.")
    logging.debug("Application closed.")
