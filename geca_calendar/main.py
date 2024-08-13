from flask import Flask, send_file
from notion_interface import read_database, create_calendar
import os
import dotenv
from logging_config import logger

if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DB_ID"):
	logger.info("Environment loaded") if dotenv.load_dotenv("notion_2425.env") else logger.error("Environment not loaded")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

token = os.environ.get("NOTION_TOKEN")
database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'

FILENAME = 'geca2425.ics'

@app.route('/')
def get_events():
    data = read_database(database_id, token)
    projects = create_calendar(data, FILENAME, True)
    return send_file(FILENAME)

@app.route('/download/<path:filename>')
def download_calendar(filename):
    return send_file(filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
