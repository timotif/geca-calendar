from app.config import DevConfig, ProdConfig, ConfigError, validate_config
from flask import Flask
from app.database import get_db
from app.routes import calendar
from app.notion_client import NotionDataSource
from app.storage import ProjectRepository
from app.calendar_generator import ICSCalendarGenerator
from app.service import CalendarService
import sys
from app.logging_config import logger

def create_app(config=None):
	"""
	Creates and configures a Flask application with calendar functionality.
	This factory function initializes a Flask application with the necessary dependencies,
	configurations, and blueprints for the calendar service. It sets up connections to
	Notion API, database storage, and ICS calendar generation.
	Args:
		config: Configuration object (DevConfig or ProdConfig). If None, uses DevConfig 
			for debug mode or ProdConfig for production.
	Returns:
		Flask: Configured Flask application instance with calendar service attached.
	Raises:
		ConfigError: If there are issues with the configuration parameters.
	Example:
		app = create_app()  # Creates app with default config
		app = create_app(DevConfig)  # Creates app with development config
	"""
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

# Local mode
if __name__ == "__main__":
	app = create_app()
	app.run(host="0.0.0.0", port=8080)