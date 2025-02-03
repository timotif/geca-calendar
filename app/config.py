from dataclasses import dataclass
import datetime
import os

# the use of __file__ guarantees that the path is relative to the file's location
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = os.path.join(APP_ROOT, 'calendars')
FILENAME = 'geca2425.ics'
JSON_DUMP = 'data.json'
UPDATE_EVERY = datetime.timedelta(hours=6)

# TODO: remove in production
import dotenv
ENV_FILE = "../.env"
env = dotenv.load_dotenv(ENV_FILE)

class ConfigError(Exception):
	pass

@dataclass
class Config:
	SQLALCHEMY_DATABASE_URI: str
	SECRET_KEY: str
	UPDATE_INTERVAL = UPDATE_EVERY
	NOTION_DB_ID = os.environ.get("NOTION_DB_ID")
	NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
	DEBUG = os.environ.get("DEBUG") == "1"

class DevConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = "dev"

class ProdConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = os.environ.get("SECRET_KEY")

def validate_config(config: Config) -> bool:
	"""
	Validates the configuration settings by checking required environment variables and directory existence.
	Args:
		config (Config): Configuration object containing required settings.
	Returns:
		bool: True if validation passes.
	Raises:
		ConfigError: If any required environment variables are missing.
	The function checks for the following required variables:
		- NOTION_DB_ID
		- NOTION_TOKEN 
		- SECRET_KEY
	Also ensures that the DIRECTORY path exists, creating it if necessary.
	"""

	required_vars = {
		'NOTION_DB_ID': config.NOTION_DB_ID,
		'NOTION_TOKEN': config.NOTION_TOKEN,
		'SECRET_KEY': config.SECRET_KEY,
	}
	missing = [key for key, value in required_vars.items() if not value]
	if missing:
		raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")
	if not os.path.exists(DIRECTORY):
		os.makedirs(DIRECTORY)