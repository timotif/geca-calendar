import os
from notion_interface import read_database, create_calendar
from logging_config import logger

ENV_FILE = ".env"

import dotenv
def main():
    if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DB_ID"):
        logger.info("Environment loaded") if dotenv.load_dotenv(ENV_FILE) else logger.info("Environment not loaded")

    data = read_database(database_id=os.environ.get("NOTION_DB_ID"), token=os.environ.get("NOTION_TOKEN"))
    create_calendar(data)

if __name__ == "__main__":
    main()