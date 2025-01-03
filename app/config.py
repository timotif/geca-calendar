from dataclasses import dataclass
import datetime
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = os.path.join(APP_ROOT, 'calendars')
FILENAME = 'geca2425.ics'
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