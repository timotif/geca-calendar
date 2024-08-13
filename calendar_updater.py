import os
from notion_interface import read_database, create_calendar

import dotenv
def main():
    if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DB_ID"):
        print("Environment loaded") if dotenv.load_dotenv("notion_2425.env") else print("Environment not loaded")

    data = read_database(database_id=os.environ.get("NOTION_DB_ID"), token=os.environ.get("NOTION_TOKEN"))
    create_calendar(data)

if __name__ == "__main__":
    main()