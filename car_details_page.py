import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging

class CarDetailsPage(tk.Frame):
    def __init__(self, parent, controller, car_details=None):
        super().__init__(parent)
        self.controller = controller
        self.car_details = car_details  # This is a tuple
        self.entries = {}  # Dictionary to keep track of the Entry widgets
        self.vars = {}  # Dictionary to keep track of BooleanVars for checkboxes
        self.key_feature_vars = {}  # Dictionary to keep track of BooleanVars for key feature checkboxes
        self.load_options()
        self.create_scrollable_ui()
        if self.car_details:
            self.update_details(self.car_details)

    def load_options(self):
        with open('car_options.json', 'r') as file:
            self.car_options = json.load(file)

    def create_scrollable_ui(self):
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.bind_mousewheel(self.canvas)

        self.create_details_ui()

    def create_details_ui(self):
        fields = ['Make', 'Model', 'Year', 'Series']
        for i, field in enumerate(fields):
            label = ttk.Label(self.scrollable_frame, text=f"{field}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry_var = tk.StringVar()
            entry = ttk.Entry(self.scrollable_frame, textvariable=entry_var)
            if self.car_details:
                entry_var.set(self.car_details[i+2])  # Adjust indices based on your tuple structure
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[field.lower().replace(' ', '_')] = entry_var  # key used in update and save methods

        # Text field for options
        ttk.Label(self.scrollable_frame, text="Options:").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
        self.options_text = tk.Text(self.scrollable_frame, height=5)
        self.options_text.grid(row=len(fields), column=1, padx=10, pady=5, sticky="ew")

        # Text field for key features
        ttk.Label(self.scrollable_frame, text="Key Features:").grid(row=len(fields) + 1, column=0, padx=10, pady=5, sticky="e")
        self.key_features_text = tk.Text(self.scrollable_frame, height=5)
        self.key_features_text.grid(row=len(fields) + 1, column=1, padx=10, pady=5, sticky="ew")

        # Checkbox options with category frames
        row = len(fields) + 2
        for category, options in self.car_options.items():
            category_frame = ttk.LabelFrame(self.scrollable_frame, text=category)
            category_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
            option_row = 0
            option_col = 0
            for option in options:
                var = tk.BooleanVar()
                key_var = tk.BooleanVar()
                chk = ttk.Checkbutton(category_frame, text=option, variable=var, command=self.update_options_text)
                chk.grid(row=option_row, column=option_col, sticky="w", padx=10, pady=2)
                key_chk = ttk.Checkbutton(category_frame, variable=key_var, command=self.update_key_features_text)
                key_chk.grid(row=option_row, column=option_col + 1, sticky="w", padx=2, pady=2)
                self.vars[option] = var
                self.key_feature_vars[option] = key_var
                option_col += 2
                if option_col >= 4:
                    option_col = 0
                    option_row += 1
            row += 1

        # Wheels section
        ttk.Label(self.scrollable_frame, text="Wheels:").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        wheels_frame = ttk.Frame(self.scrollable_frame)
        wheels_frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        self.wheel_size_var = tk.StringVar()
        self.wheel_material_var = tk.StringVar()
        self.wheel_custom_var = tk.StringVar()

        ttk.Label(wheels_frame, text="Size:").grid(row=0, column=0, padx=5, pady=2)
        ttk.Combobox(wheels_frame, textvariable=self.wheel_size_var, values=[f"{i}\"" for i in range(14, 23)]).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(wheels_frame, text="Material:").grid(row=1, column=0, padx=5, pady=2)
        ttk.Combobox(wheels_frame, textvariable=self.wheel_material_var, values=["ALLOY WHEELS", "CHROME WHEELS", "TWO-TONE WHEELS", "WHEELS"]).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(wheels_frame, text="Custom:").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(wheels_frame, textvariable=self.wheel_custom_var).grid(row=2, column=1, padx=5, pady=2)

        ttk.Checkbutton(wheels_frame, text="Key Feature", variable=tk.BooleanVar(), command=self.update_key_features_text).grid(row=3, column=0, columnspan=2, pady=5)

        # Save Changes Button
        ttk.Button(self.scrollable_frame, text="Save Changes", command=self.save_changes).grid(row=row + 1, column=0, columnspan=2, pady=10)

    def update_options_text(self):
        selected_options = [option for option, var in self.vars.items() if var.get()]
        self.options_text.delete("1.0", tk.END)
        self.options_text.insert("1.0", ", ".join(selected_options))

    def update_key_features_text(self):
        selected_key_features = [option for option, var in self.key_feature_vars.items() if var.get()]
        self.key_features_text.delete("1.0", tk.END)
        self.key_features_text.insert("1.0", ", ".join(selected_key_features))

    def bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda event: widget.bind_all("<MouseWheel>", self.on_mousewheel))
        widget.bind("<Leave>", lambda event: widget.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

    def save_changes(self):
        try:
            updated_details = {
                'make': self.entries['make'].get(),
                'model': self.entries['model'].get(),
                'model_year': self.entries['year'].get(),
                'series': self.entries['series'].get(),
                'options': self.options_text.get("1.0", tk.END).strip(),
                'key_features': self.key_features_text.get("1.0", tk.END).strip()
            }

            # Add wheels details to options
            wheel_size = self.wheel_size_var.get()
            wheel_material = self.wheel_material_var.get()
            wheel_custom = self.wheel_custom_var.get()
            wheel_description = f"{wheel_size} {wheel_material} {wheel_custom}".strip()
            if wheel_description:
                updated_details['options'] += f", {wheel_description}"

            self.controller.update_car_details(self.car_details[1], **updated_details)  # Assuming [1] is the VIN
            messagebox.showinfo("Success", "Details updated successfully!")
            self.controller.show_frame("InventoryPage")  # Redirect to the inventory frame
        except KeyError as e:
            messagebox.showerror("Error", f"Missing field: {str(e)}")
            logging.error(f"Missing field: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
            logging.error(f"Failed to save changes: {str(e)}")

    def update_details(self, new_details):
        if new_details:
            self.car_details = new_details
            for i, field in enumerate(['make', 'model', 'model_year', 'series']):
                if field in self.entries:
                    self.entries[field].set(self.car_details[i + 2])
            self.options_text.delete("1.0", tk.END)
            self.options_text.insert("1.0", self.car_details[6] if len(self.car_details) > 6 else "")
            self.key_features_text.delete("1.0", tk.END)
            self.key_features_text.insert("1.0", self.car_details[7] if len(self.car_details) > 7 else "")
            self.update_options_checkboxes()
            self.update_key_features_checkboxes()

    def update_options_checkboxes(self):
        options_text = self.car_details[6] if len(self.car_details) > 6 else ""
        for option, var in self.vars.items():
            if option in options_text:
                var.set(True)
            else:
                var.set(False)

    def update_key_features_checkboxes(self):
        key_features_text = self.car_details[7] if len(self.car_details) > 7 else ""
        for option, var in self.key_feature_vars.items():
            if option in key_features_text:
                var.set(True)
            else:
                var.set(False)
