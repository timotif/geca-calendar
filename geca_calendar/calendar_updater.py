import os
import dotenv
from notion_interface import read_database, fetch_projects, create_calendar
from logging_config import logger

ENV_FILE = ".env"

def main():
	if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DB_ID"):
		logger.info("Environment loaded") if dotenv.load_dotenv(ENV_FILE) else logger.info("Environment not loaded")
	try:
		data = read_database(database_id=os.environ.get("NOTION_DB_ID"))
		project_list = fetch_projects(data)
		create_calendar(project_list, save_to_json=True if os.getenv("DEBUG") == '1' else False)
		logger.info("Calendar updated")
	except KeyboardInterrupt:
		logger.info("Exiting")
		exit(0)

if __name__ == "__main__":
	main()