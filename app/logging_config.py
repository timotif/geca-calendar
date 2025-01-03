import logging
import os

# TODO: Add log rotation
# TODO: Integrate with config.py

LOG_DIR = './log'

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, 'geca_calendar.log')
logger = logging.getLogger("geca_calendar")

# Create handlers
file_handler = logging.FileHandler(log_file)
stream_handler = logging.StreamHandler()

# Create formatters and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Dynamically setting logger level
logger_level = logging.DEBUG if os.getenv('DEBUG') == '1' else logging.INFO
logger.setLevel(logger_level)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
