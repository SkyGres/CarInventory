import logging
import tkinter as tk
from tkinter import ttk, messagebox

class CarOptionsPage(tk.Frame):
    def __init__(self, parent, controller, vin=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.vin = vin
        self.controller = controller

        # Configure grid weights to make the frame expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a canvas widget and a vertical scrollbar for car options
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Frame to contain all the elements
        self.content_frame = ttk.Frame(self.canvas)

        # Use a window to scroll the frame
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor="nw"
        )

        # Pack canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind the canvas to make it scrollable with mouse wheel
        self.bind_mousewheel(self.canvas)

        # Create entry fields for Make, Model, Series
        make_label = ttk.Label(self.content_frame, text="Make:")
        make_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.make_entry = ttk.Entry(self.content_frame)
        self.make_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        model_label = ttk.Label(self.content_frame, text="Model:")
        model_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.model_entry = ttk.Entry(self.content_frame)
        self.model_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        series_label = ttk.Label(self.content_frame, text="Series:")
        series_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.series_entry = ttk.Entry(self.content_frame)
        self.series_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Create the label inside content_frame
        label = ttk.Label(self.content_frame, text="Select Car Options", font=("Arial", 24))
        label.grid(row=3, column=0, columnspan=2, pady=10)
        logging.debug("Car options label created")

        # Create checkboxes dynamically based on car options loaded from JSON
        self.checkboxes = {}
        row = 4
        for category, options in controller.car_options.items():
            category_frame = ttk.LabelFrame(self.content_frame, text=category)
            category_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
            logging.debug(f"Created category frame for: {category}")

            option_row = 0
            option_col = 0
            for option in options:
                var = tk.BooleanVar(value=False)
                checkbox = ttk.Checkbutton(category_frame, text=option, variable=var)
                checkbox.grid(row=option_row, column=option_col, sticky="w", padx=10, pady=2)
                self.checkboxes[option] = var
                logging.debug(f"Created checkbox for option: {option}")

                option_col += 1
                if option_col == 2:
                    option_col = 0
                    option_row += 1

            row += 1

        # Enter Button
        enter_button = ttk.Button(self.content_frame, text="Enter", command=self.save_options)
        enter_button.grid(row=row, column=0, columnspan=2, pady=20)
        logging.debug("Enter button created")

        # Button to go back to home page
        button = ttk.Button(self.content_frame, text="Go to Home Page",
                            command=lambda: controller.show_frame("HomePage"))
        button.grid(row=row + 1, column=0, columnspan=2, pady=20)
        logging.debug("Go to Home Page button created")

        # Fetch car details if VIN is provided
        if self.vin:
            self.fetch_and_fill_car_details()

    def fetch_and_fill_car_details(self):
        current_details = self.controller.fetch_car_by_vin(self.vin)
        if current_details:
            make_value, model_value, series_value = current_details[2], current_details[3], current_details[5]
            self.make_entry.insert(0, make_value)
            self.model_entry.insert(0, model_value)
            self.series_entry.insert(0, series_value)
        else:
            logging.error(f"Car with VIN {self.vin} not found in the database.")
            messagebox.showerror("Error", f"Car with VIN {self.vin} not found in the database.")
            self.controller.show_frame("HomePage")

    def bind_mousewheel(self, widget):
        widget.bind("<Enter>", self._bind_mousewheel)
        widget.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        # Perform vertical scrolling with mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def save_options(self):
        selected_options = [option for option, var in self.checkboxes.items() if var.get()]
        logging.debug(f"Selected options: {selected_options}")

        options_text = ", ".join(selected_options)
        self.controller.update_car_options(self.vin, options_text)
        logging.debug(f"Updated car options for VIN {self.vin} with: {options_text}")

        messagebox.showinfo("Success", "Car options updated successfully!")
        self.controller.show_frame("HomePage")
        logging.debug("Car options saved and user redirected to HomePage")
