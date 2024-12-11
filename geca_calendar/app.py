import os
import dotenv
from logging_config import logger
import hashlib
import base64
from database import db

loaded_env = False
if not os.getenv("SECRET_KEY") or not os.getenv("NOTION_DB_ID") or not os.getenv("NOTION_TOKEN"):
	loaded_env = dotenv.load_dotenv(".env")
	if not loaded_env:
		raise Exception("Environment variables not found")
	else:
		logger.debug("Environment variables loaded from .env file")

from flask import Flask, send_from_directory, render_template, request, jsonify 
from notion_interface import read_notion_database, fetch_projects, create_calendar, create_custom_project_list, json_to_projects, add_hash_to_db
import datetime
import json
from models import CalendarHash, ProjectDb

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projects.db" # TODO: update when dockerize
db.init_app(app)

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

def add_projects_to_db(projects):
	logger.info("Adding projects to the database")
	for project in projects:
		logger.debug(f"Adding project {project.name} to the database")
		project.save_to_db()
	logger.info("Projects added to the database")

def is_up_to_date():
	return LAST_UPDATE is not None and datetime.datetime.now() - LAST_UPDATE < UPDATE_EVERY

def update_calendar():
	global LAST_UPDATE
	data = read_notion_database(database_id)
	project_list = fetch_projects(data)
	add_projects_to_db(project_list)
	create_calendar(project_list, f"{DIRECTORY}/{FILENAME}")
	db_projects = CalendarHash.query.all()
	for hash in db_projects:
		logger.debug(f"Fetching projects for hash {hash.hash}")
		projects = [project.id for project in hash.projects]
		logger.debug(f"Projects: {projects}")
	LAST_UPDATE = datetime.datetime.now()

@app.route('/')
def get_events():
	if not is_up_to_date() or not os.path.exists(f"{DIRECTORY}/{FILENAME}"):
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
		data = read_notion_database(database_id)
		project_list = fetch_projects(data)
		create_calendar(project_list, save=False, save_to_json=True)
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
	hash = generate_hashed_filename(selected_project_ids)
	filename = f"{hash}.ics"
	project_list = create_custom_project_list(selected_project_ids, projects)
	create_calendar(project_list, filename=f"{DIRECTORY}/{filename}")
	add_hash_to_db(hash, project_list)
	return render_template("custom.html", filename=filename)

if __name__ == "__main__":
	if not os.path.exists(DIRECTORY):
		os.makedirs(DIRECTORY)
	with app.app_context():
		db.create_all()
	app.run(host='0.0.0.0', port=8080, debug=True) # TODO: remove debug=True
