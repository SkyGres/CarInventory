import logging
import tkinter as tk
from tkinter import ttk, messagebox

class CarOptionsPage(tk.Frame):
    def __init__(self, parent, controller, vin=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vin = vin
        logging.debug(f"CarOptionsPage initialized with VIN: {self.vin}")
        self.controller = controller
        self.entries = {}  # Ensure this is initialized in __init__

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content_frame = ttk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.bind_mousewheel(self.canvas)

        # Create entry fields for Make, Model, and Series
        self.create_entry_fields()

        ttk.Label(self.content_frame, text="Make:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.make_entry = ttk.Entry(self.content_frame)
        self.make_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.content_frame, text="Model:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.model_entry = ttk.Entry(self.content_frame)
        self.model_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.content_frame, text="Series:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.series_entry = ttk.Entry(self.content_frame)
        self.series_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.content_frame, text="Select Car Options", font=("Arial", 24)).grid(row=3, column=0, columnspan=2, pady=10)

        self.options_text = tk.Text(self.content_frame, height=5)
        self.options_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        row = 5
        self.checkboxes = {}
        self.vars = {}
        for category, options in controller.car_options.items():
            category_frame = ttk.LabelFrame(self.content_frame, text=category)
            category_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
            option_row = 0
            option_col = 0
            for option in options:
                var = tk.BooleanVar(value=False)
                checkbox = ttk.Checkbutton(category_frame, text=option, variable=var, command=self.update_options_text)
                checkbox.grid(row=option_row, column=option_col, sticky="w", padx=10, pady=2)
                self.checkboxes[option] = checkbox
                self.vars[option] = var
                option_col += 1
                if option_col == 2:
                    option_col = 0
                    option_row += 1
            row += 1

        ttk.Button(self.content_frame, text="Enter", command=self.save_options).grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(self.content_frame, text="Go to Home Page", command=lambda: controller.show_frame("HomePage")).grid(row=row + 1, column=0, columnspan=2, pady=20)

        if self.vin:
            logging.debug(f"VIN is set: {self.vin}. Fetching details.")
            self.fetch_and_fill_car_details()
        else:
            logging.error("VIN is not set at the time of page initialization.")

    def create_entry_fields(self):
        labels = ["Make", "Model", "Series"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(self.content_frame, text=f"{label}:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry_var = tk.StringVar()
            entry = ttk.Entry(self.content_frame, textvariable=entry_var)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[label.lower()] = entry_var  # Use StringVar for easier management

    def update_options_text(self):
        selected_options = [option for option, var in self.vars.items() if var.get()]
        self.options_text.delete("1.0", tk.END)
        self.options_text.insert("1.0", ", ".join(selected_options))

    def fetch_and_fill_car_details(self):
        if not self.vin:
            logging.error("No VIN provided to fetch details.")
            messagebox.showerror("Error", "No VIN provided.")
            return

        logging.debug(f"Attempting to fetch details for VIN: {self.vin}")
        current_details = self.controller.fetch_car_by_vin(self.vin)
        if current_details:
            logging.debug(f"Details fetched: {current_details}")
            self.update_entries(current_details)
        else:
            logging.error(f"Car with VIN {self.vin} not found.")
            messagebox.showerror("Error", f"Car with VIN {self.vin} not found.")

    def update_entries(self, details):
        try:
            self.entries['make'].set(details[2])  # Assuming 'make' is at index 2
            self.entries['model'].set(details[3])  # Assuming 'model' is at index 3
            self.entries['series'].set(details[5])  # Assuming 'series' is at index 4
            logging.debug("Entries updated successfully.")
        except IndexError as e:
            logging.error(f"Error updating entries: {e}")
            messagebox.showerror("Error", "Failed to update entries because of an index error.")


    def bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda event: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel))
        widget.bind("<Leave>", lambda event: self.canvas.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def save_options(self):
        options_text = self.options_text.get("1.0", tk.END).strip()
        if options_text:
            self.controller.update_car_options(self.vin, options_text)
            messagebox.showinfo("Success", "Car options updated successfully!")
            self.controller.show_frame("HomePage")
