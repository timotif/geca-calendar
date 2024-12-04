import os
import dotenv
from logging_config import logger
import hashlib
import base64

loaded_env = False
if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_DB_ID") or not os.getenv("NOTION_TOKEN"):
	loaded_env = dotenv.load_dotenv(".env")
	if not loaded_env:
		raise Exception("Environment variables not found")
	else:
		logger.debug("Environment variables loaded from .env file")

from flask import Flask, send_from_directory, render_template, request, jsonify 
from notion_interface import read_database, fetch_projects, create_calendar, create_custom_project_list, json_to_projects
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'

DIRECTORY = 'calendars'
FILENAME = 'geca2425.ics'
LAST_UPDATE = None
# LAST_UPDATE = datetime.datetime.now() # TODO: remove
UPDATE_EVERY = datetime.timedelta(hours=6)

@app.errorhandler(403)
def authorization_required():
	return "You're not authorized to get this file", 403

@app.errorhandler(404)
def page_not_found():
	return "I couldn't find the requested resource", 404

@app.route('/update')
def update_calendar():
	global LAST_UPDATE
	data = read_database(database_id)
	project_list = fetch_projects(data)
	create_calendar(project_list, f"{DIRECTORY}/{FILENAME}")
	LAST_UPDATE = datetime.datetime.now()
	return send_from_directory(DIRECTORY, FILENAME)

@app.route('/')
def get_events():
	if LAST_UPDATE is None or \
		datetime.datetime.now() - LAST_UPDATE > UPDATE_EVERY or\
		not os.path.exists(f"{DIRECTORY}/{FILENAME}"):
			update_calendar()
	return send_from_directory(DIRECTORY, FILENAME)

@app.route('/<path:filename>')
def download_calendar(filename):
	if filename[-4:] != ".ics":
		return authorization_required()
	try:
		return send_from_directory(DIRECTORY, filename)
	except FileNotFoundError:
		return page_not_found()

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

def generate_hashed_filename(selected_project_ids: str) -> str:
	"""From a list of project ids, generate a hashed filename"""
	input_str = ' '.join(map(str, selected_project_ids))
	hashed = hashlib.sha256(input_str.encode())
	hash_base64 = base64.urlsafe_b64encode(hashed.digest())
	return hash_base64.decode()[:8]

@app.route('/list', methods=['GET', 'POST'])
def list_projects():
	# GET method
	if request.method == 'GET':
		return render_template('projects.html')
	# POST method
	selected_project_ids = request.form.getlist('selected_projects')
	with open('projects.json', 'r') as file:
		projects = json.load(file)
	# filename = 'custom_calendar.ics'
	filename = f"{generate_hashed_filename(selected_project_ids)}.ics"
	project_list = create_custom_project_list(selected_project_ids, projects)
	create_calendar(project_list, filename=f"{DIRECTORY}/{filename}")
	return render_template("custom.html", filename=filename)

if __name__ == "__main__":
	if not os.path.exists(DIRECTORY):
		os.makedirs(DIRECTORY)
	app.run(host='0.0.0.0', port=8080, debug=True)
