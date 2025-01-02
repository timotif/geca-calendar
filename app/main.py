from config import DevConfig, ProdConfig
from flask import Flask
from database import get_db
from routes import calendar
from notion_client import NotionDataSource
from storage import ProjectRepository
from calendar_generator import ICSCalendarGenerator
from service import CalendarService

def create_app(config=None):
	app = Flask(__name__)
	
	# Load config
	if config == None:
		config = DevConfig if app.debug else ProdConfig
	app.config.from_object(config)

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

	return app

if __name__ == "__main__":
	app = create_app()
	app.run(debug=True, host="0.0.0.0", port=8080)