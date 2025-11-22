# setup logging
# ------------
# This file should contain the logging configuration.
# It should be imported at the start of the main application.
# it will create a logger object that can be used to log messages.
#  it willl create logs folder and save the logs in it according to the date and have formatting according to level

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler which logs even debug messages
fh = logging.FileHandler("logs/app.log")
fh.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# Log some messages
logger.debug("Logger setup complete")
logger.info("Logger setup complete")
logger.warning("Logger setup complete")
logger.error("Logger setup complete")
logger.critical("Logger setup complete")

