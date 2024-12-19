from dataclasses import dataclass
import datetime
import os

@dataclass
class Config:
	SQLALCHEMY_DATABASE_URI: str
	SECRET_KEY: str
	NOTION_DB_ID: str
	UPDATE_INTERVAL = datetime.timedelta(hours=6)
	NOTION_DB_ID = os.environ.get("NOTION_DB_ID")

class DevConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = "dev"

class ProdConfig(Config):
	SQLALCHEMY_DATABASE_URI = "sqlite:///projects.db"
	SECRET_KEY = os.environ.get("SECRET_KEY")