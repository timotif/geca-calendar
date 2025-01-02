import os
import dotenv
from logging_config import logger
from notion_client import NotionDataSource
from calendar_generator import ICSCalendarGenerator
from config import DIRECTORY, FILENAME

ENV_FILE = ".env"

def main():
	if not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DB_ID"):
		logger.info("Environment loaded") if dotenv.load_dotenv(ENV_FILE) else logger.info("Environment not loaded")
	try:
		notion = NotionDataSource(os.getenv("NOTION_TOKEN"), os.getenv("NOTION_DB_ID"))
		ics = ICSCalendarGenerator(os.path.join(DIRECTORY, FILENAME))
		data = notion.fetch_data()
		ics.generate(data)
		logger.info("Calendar updated")
	except KeyboardInterrupt:
		logger.info("Exiting...")
		exit(0)

if __name__ == "__main__":
	main()