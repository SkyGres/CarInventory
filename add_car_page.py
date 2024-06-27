import logging
import tkinter as tk
from tkinter import ttk, messagebox

import requests


class AddCarPage(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # VIN Entry
        self.vin_entry = ttk.Entry(self)
        self.vin_entry.grid(row=0, column=1, padx=10, pady=10)

        # VIN Label
        ttk.Label(self, text="Enter VIN:").grid(row=0, column=0, padx=10, pady=10)

        # Enter VIN Button
        ttk.Button(self, text="Enter", command=self.enter_vin).grid(row=0, column=2, padx=10, pady=10)

        # Bind return key (Enter key) to enter_vin method
        self.vin_entry.bind('<Return>', lambda event: self.enter_vin())

        # Other initialization code...

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

        # Calculate the stock number as the last 4 characters of the VIN
        stock_number = vin[-4:]
        logging.debug(f"Calculated stock number: {stock_number}")

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
                self.controller.insert_car(vin, make, model, model_year, series, "", "", stock_number)
                logging.debug("Car data inserted into the database")

                # Print the extracted fields
                logging.debug(f"Make: {make}")
                logging.debug(f"Model: {model}")
                logging.debug(f"Model Year: {model_year}")
                logging.debug(f"Series: {series}")

                messagebox.showinfo("Success", "Car added successfully!")
                # Show the CarOptionsPage with the VIN passed
                self.controller.show_frame("CarOptionsPage", vin=vin)

            except ValueError as e:
                messagebox.showerror("Error", str(e))
                logging.error(f"Error inserting car data: {e}")

        else:
            messagebox.showerror("Error", "No results found for the entered VIN.")
            logging.debug("No results found for the entered VIN")