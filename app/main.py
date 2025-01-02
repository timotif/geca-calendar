from config import DevConfig, ProdConfig, ConfigError, validate_config
from flask import Flask
from database import get_db
from routes import calendar
from notion_client import NotionDataSource
from storage import ProjectRepository
from calendar_generator import ICSCalendarGenerator
from service import CalendarService
import sys
from logging_config import logger

def create_app(config=None):
	try:
		app = Flask(__name__)
		
		# Load config
		if config == None:
			config = DevConfig if app.debug else ProdConfig
		app.config.from_object(config)

		validate_config(config)

		# Get database
		db = get_db(app)

		# Init blueprints
		app.register_blueprint(calendar)

		# Create dependencies
		notion = NotionDataSource(
			app.config["NOTION_TOKEN"], 
			app.config["NOTION_DB_ID"]
		)
		repo = ProjectRepository(db)
		ics = ICSCalendarGenerator()

		# Link to app context
		app.calendar = CalendarService(
			notion, repo, ics
		)

		logger.info("Application started")
		return app
	
	except ConfigError as e:
		logger.error(f"Configuration error: {e}")
		sys.exit(1)

if __name__ == "__main__":
	app = create_app()
	app.run(debug=True, host="0.0.0.0", port=8080)