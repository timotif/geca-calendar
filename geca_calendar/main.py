import os
import dotenv

loaded_env = False
if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_DB_ID") or not os.getenv("NOTION_TOKEN"):
	loaded_env = dotenv.load_dotenv(".env")

from flask import Flask, send_file, render_template
from logging_config import logger
from notion_interface import read_database, create_calendar, TOKEN
import datetime
import json

if loaded_env:
	logger.debug("Environment variables loaded from .env file")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'

FILENAME = 'geca2425.ics'
LAST_UPDATE = None
UPDATE_EVERY = datetime.timedelta(hours=6)

@app.route('/update')
def update_calendar():
	global LAST_UPDATE
	data = read_database(database_id, TOKEN)
	projects = create_calendar(data, FILENAME)
	LAST_UPDATE = datetime.datetime.now()
	return send_file(FILENAME)

@app.route('/')
def get_events():
	if LAST_UPDATE is None or \
		datetime.datetime.now() - LAST_UPDATE > UPDATE_EVERY or\
		not os.path.exists(FILENAME):
			update_calendar()
	return send_file(FILENAME)

@app.route('/download/<path:filename>')
def download_calendar(filename):
	return send_file(filename)

@app.route('/list')
def list_projects():
	global LAST_UPDATE
	if os.path.exists('projects.json') and LAST_UPDATE != None and datetime.datetime.now() - LAST_UPDATE < UPDATE_EVERY:
		with open('projects.json', 'r') as file:
			projects = json.load(file)
	else:
		data = read_database(database_id, TOKEN)
		projects = create_calendar(data, save_to_calendar=False, save_to_json=True)
		LAST_UPDATE = datetime.datetime.now()
	return render_template('index.html', projects=projects)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
