import logging
from car_options_page import CarOptionsPage
import tkinter as tk
from tkinter import ttk, messagebox
from notification_frame import NotificationFrame
import json
import pyperclip
import requests
import sv_ttk  # Assuming sv_ttk provides set_theme() function
import time


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
