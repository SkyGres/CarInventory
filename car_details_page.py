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
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[field.lower().replace(' ', '_')] = entry_var  # key used in update and save methods

        # Text field for options
        ttk.Label(self.scrollable_frame, text="Options:").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
        self.options_text = tk.Text(self.scrollable_frame, height=10)
        self.options_text.grid(row=len(fields), column=1, padx=10, pady=5, sticky="ew")

        # Text field for key features
        ttk.Label(self.scrollable_frame, text="Key Features:").grid(row=len(fields) + 1, column=0, padx=10, pady=5, sticky="e")
        self.key_features_text = tk.Text(self.scrollable_frame, height=10)
        self.key_features_text.grid(row=len(fields) + 1, column=1, padx=10, pady=5, sticky="ew")

        # Wheels section
        row = len(fields) + 2
        ttk.Label(self.scrollable_frame, text="Wheels:").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        wheels_frame = ttk.Frame(self.scrollable_frame)
        wheels_frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        self.wheel_size_var = tk.StringVar()
        self.wheel_material_var = tk.StringVar(value="None")
        self.wheel_custom_var = tk.StringVar()
        self.wheel_key_feature_var = tk.BooleanVar()

        ttk.Label(wheels_frame, text="Size:").grid(row=0, column=0, padx=5, pady=2)
        size_combobox = ttk.Combobox(wheels_frame, textvariable=self.wheel_size_var, values=[f"{i}\"" for i in range(14, 23)])
        size_combobox.grid(row=0, column=1, padx=5, pady=2)
        size_combobox.bind("<Enter>", lambda e: self.unbind_mousewheel(self.canvas))
        size_combobox.bind("<Leave>", lambda e: self.bind_mousewheel(self.canvas))
        size_combobox.bind("<MouseWheel>", lambda e: "break")

        ttk.Label(wheels_frame, text="Material:").grid(row=1, column=0, padx=5, pady=2)
        materials = ["None", "ALLOY WHEELS", "CHROME WHEELS", "TWO-TONE WHEELS", "WHEELS"]
        material_frame = ttk.Frame(wheels_frame)
        material_frame.grid(row=1, column=1, padx=5, pady=2)
        for material in materials:
            ttk.Radiobutton(material_frame, text=material, variable=self.wheel_material_var, value=material).pack(anchor="w")

        ttk.Label(wheels_frame, text="Custom:").grid(row=2, column=0, padx=5, pady=2)
        custom_entry = ttk.Entry(wheels_frame, textvariable=self.wheel_custom_var)
        custom_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Checkbutton(wheels_frame, text="Key Feature", variable=self.wheel_key_feature_var, command=self.update_key_features_text).grid(row=3, column=0, columnspan=2, pady=5)

        # Checkbox options with category frames
        row += 1
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

        # Save Changes Button
        ttk.Button(self.scrollable_frame, text="Save Changes", command=self.save_changes).grid(row=row + 1, column=0, columnspan=2, pady=10)

    def update_options_text(self):
        selected_options = [option for option, var in self.vars.items() if var.get()]
        wheel_description = self.generate_wheel_description()
        if wheel_description:
            selected_options.append(wheel_description)
        self.options_text.delete("1.0", tk.END)
        self.options_text.insert("1.0", ", ".join(selected_options))

    def update_key_features_text(self):
        selected_key_features = [option for option, var in self.key_feature_vars.items() if var.get()]

        # Handle special cases for moonroofs
        moonroof_mappings = {
            "POWER WINDOWS, LOCKS AND SEAT": "POWER SEAT",
            "POWER WINDOWS, LOCKS, SEAT AND MOONROOF": "MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND MOONROOF": "MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND DUAL MOONROOF": "DUAL MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND PANORAMIC MOONROOF": "PANORAMIC MOONROOF"
        }

        for long_key, short_key in moonroof_mappings.items():
            if long_key in selected_key_features:
                selected_key_features.remove(long_key)
                if short_key not in selected_key_features:
                    selected_key_features.append(short_key)

        if self.wheel_key_feature_var.get():
            wheel_description = self.generate_wheel_description()
            if wheel_description:
                selected_key_features.append(wheel_description)

        self.key_features_text.delete("1.0", tk.END)
        self.key_features_text.insert("1.0", ", ".join(selected_key_features))

    def generate_wheel_description(self):
        wheel_size = self.wheel_size_var.get()
        wheel_material = self.wheel_material_var.get()
        wheel_custom = self.wheel_custom_var.get()
        if wheel_material == "None":
            wheel_material = ""
        wheel_description = f"{wheel_size} {wheel_material} {wheel_custom}".strip()
        return wheel_description if wheel_description != "" else None

    def bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda event: widget.bind_all("<MouseWheel>", self.on_mousewheel))
        widget.bind("<Leave>", lambda event: widget.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

    def unbind_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")

    def save_changes(self):
        try:
            updated_details = {
                'make': self.entries['make'].get(),
                'model': self.entries['model'].get(),
                'model_year': self.entries['year'].get(),
                'series': self.entries['series'].get(),
                'options': self.options_text.get("1.0", tk.END).strip(),
                'key_features': self.key_features_text.get("1.0", tk.END).strip(),
                'wheel_size': self.wheel_size_var.get(),
                'alloy_wheels': self.wheel_material_var.get() == "ALLOY WHEELS",
                'two_tone_wheels': self.wheel_material_var.get() == "TWO-TONE WHEELS",
                'chrome_wheels': self.wheel_material_var.get() == "CHROME WHEELS",
                'wheels': self.wheel_material_var.get() == "WHEELS",
                'custom_wheels': self.wheel_custom_var.get(),
                'is_wheel_key_feature': self.wheel_key_feature_var.get()
            }
            self.controller.update_car_details(self.car_details[1], **updated_details)
            messagebox.showinfo("Success", "Details updated successfully!")
            self.controller.show_frame("InventoryPage")  # Redirect to the inventory frame
        except KeyError as e:
            messagebox.showerror("Error", f"Missing field: {str(e)}")
            logging.error(f"Missing field: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
            logging.error(f"Failed to save changes: {str(e)}")

    def update_details(self, new_details):
        # Clear existing values
        for field in self.entries.values():
            field.set("")
        self.options_text.delete("1.0", tk.END)
        self.key_features_text.delete("1.0", tk.END)
        self.wheel_size_var.set("")
        self.wheel_material_var.set("None")
        self.wheel_custom_var.set("")
        self.wheel_key_feature_var.set(False)

        if new_details:
            self.car_details = new_details
            # Log the car details
            logging.debug(f"New car details: {self.car_details}")
            # Update the entries with the new details
            for i, field in enumerate(['make', 'model', 'year', 'series']):
                if field in self.entries:
                    logging.debug(f"Setting {field} to {self.car_details[i + 2]}")
                    self.entries[field].set(self.car_details[i + 2])
            self.options_text.insert("1.0", self.car_details[6] if len(self.car_details) > 6 else "")
            self.key_features_text.insert("1.0", self.car_details[7] if len(self.car_details) > 7 else "")
            self.update_options_checkboxes()
            self.update_key_features_checkboxes()
            self.update_wheels_section()

    def update_options_checkboxes(self):
        options_text = self.car_details[6] if len(self.car_details) > 6 else ""
        options_list = [opt.strip() for opt in options_text.split(',')]

        # Special cases that require exact matching with commas
        special_cases = [
            "POWER WINDOWS, LOCKS AND MIRRORS",
            "POWER WINDOWS, LOCKS AND SEAT",
            "POWER WINDOWS, LOCKS AND SEATS",
            "POWER WINDOWS, LOCKS, SEAT AND MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND DUAL MOONROOF",
            "POWER WINDOWS, LOCKS, SEATS AND PANORAMIC MOONROOF"
        ]

        # Clear all checkboxes first
        for option, var in self.vars.items():
            var.set(False)

        # Set checkboxes based on options_list and special cases
        for option in self.vars.keys():
            # Check if the exact option is in the options list or matches a special case
            if option in options_list or option in special_cases and option in options_text:
                self.vars[option].set(True)

    def update_key_features_checkboxes(self):
        key_features_text = self.car_details[7] if len(self.car_details) > 7 else ""
        for option, var in self.key_feature_vars.items():
            var.set(option in key_features_text)

    def update_wheels_section(self):
        self.wheel_size_var.set(self.car_details[9] if len(self.car_details) > 9 else "")
        if self.car_details[10]:
            self.wheel_material_var.set("ALLOY WHEELS")
        elif self.car_details[11]:
            self.wheel_material_var.set("TWO-TONE WHEELS")
        elif self.car_details[12]:
            self.wheel_material_var.set("CHROME WHEELS")
        elif self.car_details[13]:
            self.wheel_material_var.set("WHEELS")
        else:
            self.wheel_material_var.set("None")
        self.wheel_custom_var.set(self.car_details[14] if len(self.car_details) > 14 else "")
        wheel_description = self.generate_wheel_description()
        key_features_text = self.car_details[7] if len(self.car_details) > 7 else ""
        self.wheel_key_feature_var.set(wheel_description in key_features_text)

# Add logging configuration
logging.basicConfig(level=logging.DEBUG)
