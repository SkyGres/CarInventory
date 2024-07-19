import logging
from car_inventory_app import CarInventoryApp

# Clear the existing log file by opening it in 'w' mode
with open('car_inventory.log', 'w'):
    pass

# Create a custom logger
logger = logging.getLogger()

# Set the minimum log level
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('car_inventory.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

if __name__ == "__main__":
    logger.debug("Starting Car Inventory application.")
    try:
        app = CarInventoryApp()
        app.mainloop()
        logger.debug("Application main loop running.")
    except Exception as e:
        logger.exception("An error occurred while running the application.")
    logger.debug("Application closed.")
