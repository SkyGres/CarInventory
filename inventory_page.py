import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import PyPDF2
from PyPDF2.generic import NameObject, TextStringObject, BooleanObject, IndirectObject
import webbrowser

from car_details_page import CarDetailsPage


class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.inventory_container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inventory_container, anchor="nw")
        self.bind_mousewheel(self.canvas)
        self.inventory_container.bind("<Configure>",
                                      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.update_inventory_list()
        self.create_print_button()

    def create_print_button(self):
        print_button = ttk.Button(self, text="Print Selected Cars", command=self.print_selected_cars)
        print_button.pack(side="top", pady=10)

        self.skip_fields_var = tk.IntVar(value=0)
        tk.Label(self, text="Skip fields:").pack(side="top")
        ttk.Spinbox(self, from_=0, to=3, textvariable=self.skip_fields_var, width=5).pack(side="top")

    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def unbind_mousewheel(self, widget):
        self.unbind_all("<MouseWheel>")

    def update_inventory_list(self):
        for widget in self.inventory_container.winfo_children():
            widget.destroy()
        logging.debug("Previous inventory list cleared")

        cars = self.controller.fetch_cars()
        self.car_check_vars = {}
        for car in cars:
            car_frame = ttk.Frame(self.inventory_container, borderwidth=2, relief="groove")
            car_frame.pack(fill="x", padx=10, pady=5)
            logging.debug(f"Created frame for car: {car}")

            button_text = f"{car[8]}\n{car[4]} {car[2]} {car[3]}"
            car_button = tk.Button(car_frame, text=button_text, command=lambda c=car: self.show_car_details(c),
                                   bg="#f0f0f0", fg="black", font=("Arial", 12), relief="raised", bd=2)
            car_button.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            car_button.config(width=50, height=5)
            logging.debug(f"Added main clickable area for car: {car}")

            action_frame = ttk.Frame(car_frame)
            action_frame.pack(side="right", fill="y", padx=10, pady=5)
            logging.debug(f"Created frame for quick action buttons for car: {car}")

            car_var = tk.BooleanVar()
            car_check = ttk.Checkbutton(action_frame, variable=car_var)
            car_check.pack(fill="x", pady=5)
            self.car_check_vars[car] = car_var

            copy_button = ttk.Button(action_frame, text="Copy Text", command=lambda c=car: self.copy_text(c))
            copy_button.pack(fill="x", pady=5)
            vin_button = ttk.Button(action_frame, text="Copy VIN", command=lambda c=car: self.copy_vin(c))
            vin_button.pack(fill="x", pady=5)
            archive_button = ttk.Button(action_frame, text="Archive", command=lambda c=car: self.archive_car(c))
            archive_button.pack(fill="x", pady=5)
            delete_button = ttk.Button(action_frame, text="Delete", command=lambda c=car: self.delete_car(c))
            delete_button.pack(fill="x", pady=5)
            print_guide_button = ttk.Button(action_frame, text="Print Guide", command=lambda c=car: self.print_guide(c))
            print_guide_button.pack(fill="x", pady=5)
            logging.debug(f"Added Delete button for car: {car}")

    def show_car_details(self, car):
        vin = car[1]
        try:
            car_details = self.controller.fetch_car_by_vin(vin)
            if car_details:
                if "CarDetailsPage" in self.controller.frames:
                    self.controller.frames["CarDetailsPage"].update_details(car_details)
                else:
                    details_page = CarDetailsPage(parent=self.controller.main_content, controller=self.controller,
                                                  car_details=car_details)
                    self.controller.frames["CarDetailsPage"] = details_page
                self.controller.show_frame("CarDetailsPage")
            else:
                logging.error(f"No car found with VIN: {vin}")
                messagebox.showerror("Error", f"No car details found for VIN: {vin}")
        except Exception as e:
            logging.error(f"An error occurred while fetching details for VIN {vin}: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def copy_text(self, car):
        try:
            car_details = self.controller.fetch_car_by_vin(car[1])
            if car_details:
                year = car_details[4]
                make = car_details[2]
                model = car_details[3]
                series = car_details[5]
                options = car_details[6]
                key_features = car_details[7].replace(", ", ", <br />") + "!"
                text_to_copy = f'''
                <div style="text-align: center;"><strong><span style="font-size: 36px;">{year} {make} {model} {series},<br />
                <br />
                <span style="font-size: 28px;"><span style="font-size: 24px;">LOW NO HAGGLE PRICE,<br />
                AUTOCHECK CERTIFIED,<br />
                LOW RATE FINANCING AVAILABLE,<br />
                NATIONWIDE SHIPPING!<br />
                <br />
                {key_features}</span></span></span></strong><br />
                <br />
                <span style="font-size: 36px;"><span style="font-size: 28px;"><span style="font-size: 24px;"><span style="font-size: 18px;">THIS {year} {make} {model} {series} IS IN VERY NICE SHAPE IN AND OUT!<br />
                THE EXTERIOR IS VERY NICE AND GLOSSY ALL AROUND.<br />
                THE INTERIOR IS VERY CLEAN.<br />
                THIS VEHICLE RUNS AND HANDLES EXCELLENT.<br />
                BUY WITH CONFIDENCE!<br />
                <br />
                <strong>OPTIONS: </strong>{options}.</span></span></span></span><br />
                &nbsp;</div>
                '''
                pyperclip.copy(text_to_copy)
                messagebox.showinfo("Success", "Car details copied to clipboard.")
            else:
                messagebox.showerror("Error", "Failed to fetch car details.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {str(e)}")
            logging.error(f"Failed to copy text: {str(e)}")

    def copy_vin(self, car):
        car_details = car[1]
        pyperclip.copy(car_details)
        logging.debug(f"Copied car VIN details to clipboard: {car_details}")

    def archive_car(self, car):
        logging.debug(f"Archiving car: {car}")
        self.controller.archive_car(car)
        self.update_inventory_list()

    def delete_car(self, car):
        vin = car[1]
        logging.debug(f"Deleting car: {car}")
        if messagebox.askyesno("Delete Car", f"Are you sure you want to delete the car with VIN: {vin}?"):
            self.controller.delete_car(vin)
            logging.debug(f"Deleted car with VIN: {vin}")
            self.update_inventory_list()

    def print_selected_cars(self):
        selected_cars = [car for car, var in self.car_check_vars.items() if var.get()]
        logging.debug(f"Selected cars for printing: {selected_cars}")

        if not selected_cars:
            messagebox.showerror("Error", "Please select at least one car to print.")
            return

        skip_fields = self.skip_fields_var.get()

        try:
            pdf_reader = PyPDF2.PdfReader(open("template_form.pdf", "rb"))
            pdf_writer = PyPDF2.PdfWriter()

            field_mappings = [
                ("car_name_first", "car_options_first"),
                ("car_name_second", "car_options_second"),
                ("car_name_third", "car_options_third"),
                ("car_name_first_two", "car_options_first_two"),
                ("car_name_second_two", "car_options_second_two"),
                ("car_name_third_two", "car_options_third_two"),
                ("car_name_first_three", "car_options_first_three"),
                ("car_name_second_three", "car_options_second_three"),
                ("car_name_third_three", "car_options_third_three")
            ]

            total_pages_needed = (len(selected_cars) + 2 + skip_fields) // 3
            for page_num in range(total_pages_needed):
                pdf_writer.add_page(pdf_reader.pages[page_num % len(pdf_reader.pages)])

            current_field_index = skip_fields

            for i, car in enumerate(selected_cars):
                car_name = f"{car[4]} {car[2]} {car[3]} - {car[8]} {car[5]}"
                car_options = car[6]
                field_name, field_options = field_mappings[current_field_index]

                page_index = current_field_index // 3
                page = pdf_writer.pages[page_index]

                for field_key in page["/Annots"]:
                    field = field_key.get_object()
                    field_name_in_page = field.get("/T")
                    if field_name_in_page == field_name:
                        logging.debug(f"Updating field {field_name} with value {car_name}")
                        field.update({NameObject("/V"): TextStringObject(car_name)})
                    elif field_name_in_page == field_options:
                        logging.debug(f"Updating field {field_options} with value {car_options}")
                        field.update({NameObject("/V"): TextStringObject(car_options)})

                current_field_index += 1

            self.set_need_appearances_writer(pdf_writer)

            with open("filled_form.pdf", "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            logging.debug("Filled PDF saved to filled_form.pdf")
            self.open_pdf_with_default_app("filled_form.pdf")
        except Exception as e:
            logging.error(f"Failed to fill and save PDF form: {e}")
            messagebox.showerror("Error", f"Failed to fill and save PDF form: {str(e)}")

    def print_guide(self, car):
        try:
            pdf_reader = PyPDF2.PdfReader(open("buyers_guide_orig.pdf", "rb"))
            pdf_writer = PyPDF2.PdfWriter()

            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            field_values = {
                "make": car[2],
                "model": car[3],
                "year": car[4],
                "vin": car[1],
                "stock_number": car[8]
            }

            for page in pdf_writer.pages:
                if "/Annots" not in page:
                    continue

                for field_key in page["/Annots"]:
                    field = field_key.get_object()
                    field_name = field.get("/T")
                    if field_name and field_name in field_values:
                        logging.debug(f"Updating field {field_name} with value {field_values[field_name]}")
                        field.update({NameObject("/V"): TextStringObject(field_values[field_name])})

            self.set_need_appearances_writer(pdf_writer)

            with open("filled_guide.pdf", "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            logging.debug("Filled PDF saved to filled_guide.pdf")
            self.open_pdf_with_default_app("filled_guide.pdf")
        except Exception as e:
            logging.error(f"Failed to fill and save PDF form: {e}")
            messagebox.showerror("Error", f"Failed to fill and save PDF form: {str(e)}")

    def set_need_appearances_writer(self, writer):
        try:
            catalog = writer._root_object
            if "/AcroForm" not in catalog:
                writer._root_object.update(
                    {
                        NameObject("/AcroForm"): IndirectObject(
                            len(writer._objects), 0, writer
                        )
                    }
                )

            need_appearances = NameObject("/NeedAppearances")
            writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
            return writer

        except Exception as e:
            logging.error(f"set_need_appearances_writer() exception: {repr(e)}")
            return writer

    def open_pdf_with_default_app(self, pdf_file_path):
        try:
            webbrowser.open_new(pdf_file_path)
            logging.debug(f"PDF opened with default application: {pdf_file_path}")
        except Exception as e:
            logging.error(f"Failed to open PDF with default application: {e}")
            messagebox.showerror("Error", f"Failed to open PDF with default application: {str(e)}")


class MainController:
    def fetch_cars(self):
        return [
            (1, "VIN1", "Make1", "Model1", "Year1", "Series1", "Options1", "KeyFeatures1", "StockNumber1"),
            (2, "VIN2", "Make2", "Model2", "Year2", "Series2", "Options2", "KeyFeatures2", "StockNumber2"),
        ]

    def fetch_car_by_vin(self, vin):
        for car in self.fetch_cars():
            if car[1] == vin:
                return car
        return None

    def archive_car(self, car):
        pass

    def delete_car(self, vin):
        pass

    def show_frame(self, frame_name):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    controller = MainController()
    page = InventoryPage(root, controller)
    page.pack(fill="both", expand=True)
    root.mainloop()
