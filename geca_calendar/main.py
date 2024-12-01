import os
import dotenv
from logging_config import logger

loaded_env = False
if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_DB_ID") or not os.getenv("NOTION_TOKEN"):
	loaded_env = dotenv.load_dotenv(".env")
	if not loaded_env:
		raise Exception("Environment variables not found")
	else:
		logger.debug("Environment variables loaded from .env file")

from flask import Flask, send_file, render_template, request, jsonify
from notion_interface import read_database, fetch_projects, create_calendar, create_custom_project_list, json_to_projects
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'

FILENAME = 'geca2425.ics'
LAST_UPDATE = None
LAST_UPDATE = datetime.datetime.now() # TODO: remove
UPDATE_EVERY = datetime.timedelta(hours=6)

@app.route('/update')
def update_calendar():
	global LAST_UPDATE
	data = read_database(database_id)
	project_list = fetch_projects(data)
	create_calendar(project_list, FILENAME)
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

@app.route('/fetch_projects')
def fetch_projects_api():
	global LAST_UPDATE
	if os.path.exists('projects.json') and LAST_UPDATE != None and datetime.datetime.now() - LAST_UPDATE < UPDATE_EVERY:
		with open('projects.json', 'r') as file:
			project_json = json.load(file)
			project_list = json_to_projects(project_json)
	else:
		data = read_database(database_id)
		project_list = fetch_projects(data)
		create_calendar(project_list, save_to_calendar=False, save_to_json=True)
	LAST_UPDATE = datetime.datetime.now()
	return jsonify([project.__dict__ for project in project_list])

@app.route('/list', methods=['GET', 'POST'])
def list_projects():
	# GET method
	if request.method == 'GET':
		return render_template('projects.html')
	# POST method
	# print(request.form.getlist('selected_projects')) # edit from index.html what is sent back to the backend
	filename = 'custom_calendar.ics'
	selected_project_ids = request.form.getlist('selected_projects')
	with open('projects.json', 'r') as file:
		projects = json.load(file)
	project_list = create_custom_project_list(selected_project_ids, projects)
	create_calendar(project_list, filename=filename)
	return send_file(filename)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080, debug=True)
