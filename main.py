import logging
import tkinter as tk
from car_inventory_app import CarInventoryApp

# Clear the existing log file by opening it in 'w' mode
with open('car_inventory.log', 'w'):
    pass

logging.basicConfig(
    filename='car_inventory.log',  # Log file path
    level=logging.DEBUG,  # Log all debug messages and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

if __name__ == "__main__":
    logging.debug("Starting Car Inventory application.")
    try:
        app = CarInventoryApp()
        app.mainloop()
        logging.debug("Application main loop running.")
    except Exception as e:
        logging.exception("An error occurred while running the application.")
    logging.debug("Application closed.")