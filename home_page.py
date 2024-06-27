import logging
import tkinter as tk
from tkinter import ttk, messagebox

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