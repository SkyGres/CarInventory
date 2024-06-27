import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

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