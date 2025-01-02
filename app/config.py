from dataclasses import dataclass
import datetime
import os

DIRECTORY = 'calendars'
FILENAME = 'geca2425.ics'
UPDATE_EVERY = datetime.timedelta(hours=6)

@dataclass
class Config:
	SQLALCHEMY_DATABASE_URI: str
	SECRET_KEY: str
	UPDATE_INTERVAL = UPDATE_EVERY
	NOTION_DB_ID = os.environ.get("NOTION_DB_ID")
	NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

class DevConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = "dev"

class ProdConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = os.environ.get("SECRET_KEY")