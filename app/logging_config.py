import logging
from logging.handlers import RotatingFileHandler
import os
from config import APP_ROOT

LOG_DIR = os.path.join(APP_ROOT, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'geca_calendar.log')
LOG_FORMAT = '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'

def setup_logging(debug_mode=False):
	if not os.path.exists(LOG_DIR):
		os.makedirs(LOG_DIR)

	# Create shared file handler with rotation
	file_handler = RotatingFileHandler(
		LOG_FILE,
		maxBytes=10 * 1024 * 1024,  # 10MB
		backupCount=5
	)

	# logger = logging.getLogger("geca_calendar")

	# Create handlers
	file_handler = logging.FileHandler(LOG_FILE)
	stream_handler = logging.StreamHandler()

	# Create formatters and add it to handlers
	formatter = logging.Formatter(LOG_FORMAT)
	file_handler.setFormatter(formatter)
	stream_handler.setFormatter(formatter)

	# Dynamically setting logger level
	logger_level = logging.DEBUG if debug_mode else logging.INFO
	# logger.setLevel(logger_level)

	# Component loggers with their config levels
	loggers_config = {
		"geca_calendar_app": logger_level,
		"calendar_service": logger_level,
		"calendar_generator": logger_level,
		"notion_client": logger_level,
		"sql_database": logger_level,
	}

	# Set up each logger
	for logger_name, level in loggers_config.items():
		logger = logging.getLogger(logger_name)
		logger.setLevel(level)
		logger.handlers.clear()
		logger.addHandler(file_handler)
		logger.addHandler(stream_handler)

app_logger = logging.getLogger("geca_calendar_app")
notion_logger = logging.getLogger("notion_client")
calendar_generator_logger = logging.getLogger("calendar_generator")
calendar_service_logger = logging.getLogger("calendar_service")
sql_logger = logging.getLogger("sql_database")
