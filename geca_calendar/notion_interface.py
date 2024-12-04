import requests
from ics import Calendar, Event
import json
import logging
import os
from models import ProjectDb, CalendarHash
import datetime

logger = logging.getLogger("geca_calendar")

TOKEN = os.getenv('NOTION_TOKEN')
HEADERS = {
	'Authorization': 'Bearer ' + TOKEN,
	'Notion-Version': '2022-06-28',
	'Content-Type': 'application/json',
}

def read_database(database_id):
	"""Given a database_id and the secret token it returns a json of the database"""
	logger.info("Fetching data")
	read_url = f"https://api.notion.com/v1/databases/{database_id}/query"
	response = requests.request("POST", read_url, headers=HEADERS)
	data = response.json()
	logger.debug(f"Status code: {response.status_code}")
	return data

def fetch_seating_blocks(data: json) -> dict:
	"""It returns repertoire->page_id pairs from the data"""
	seating_blocks = {}
	for i in range(len(data['results'])):
		if data['results'][i]['type'] == 'paragraph' and \
			len(data['results'][i]['paragraph']['rich_text']) != 0 and \
			(data['results'][i]['paragraph']['rich_text'][0]['plain_text'].lower() == "seating positions" or \
			data['results'][i]['paragraph']['rich_text'][0]['plain_text'].lower() == "seating position"):
			# Seating is set up
			logger.debug("Seating positions found")
			i += 1
			# Going until the divider to fetch page ids
			while (i < len(data['results']) and data['results'][i]['type'] != 'divider'):
				try:
					key = data['results'][i]['child_page']['title']
				except KeyError as e:
					if e.args[0] == 'child_page':
						logger.debug("Empty block found")
						i += 1
						continue
				value = data['results'][i]['id']
				logger.debug(f"Adding {key} with id {value}")
				seating_blocks[key] = value
				i += 1
			break
	return seating_blocks

def fetch_seating_order(seating_blocks: dict, data: json) -> str:
	"""Appends to a string the seating order of each page"""
	seating_parsed = ""
	for key, value in seating_blocks.items():
		# Searching in each seating page
		page_id = value
		response = requests.request("GET", f"https://api.notion.com/v1/blocks/{page_id}/children", headers=HEADERS)
		data = response.json()
		seating = ""
		for i in range(len(data['results'])):
			# Searching the blocks of the seating page
			block = data['results'][i]
			type = block['type']
			if type == 'heading_3': # Section name
				seating += block[type]['rich_text'][0]['plain_text'] + ":\n"
			elif block['type'] == 'paragraph' and len(block['paragraph']['rich_text']) != 0:
				seating += block['paragraph']['rich_text'][0]['plain_text'] + "\n" # Section list
		seating_parsed += f"{key}\n{seating}\n"
	return seating_parsed
	
def get_seating_positions(page_id: str, token: str) -> str:
	# Checking a project page
	logger.debug(f"Fetching seating positions for page {page_id}")
	endpoint = f"https://api.notion.com/v1/blocks/{page_id}/children"
	response = requests.request("GET", endpoint, headers=HEADERS)
	data = response.json()
	logger.debug(f"Status code: {response.status_code}")
	seating_blocks = fetch_seating_blocks(data) # repertoire->page_id pairs
	return fetch_seating_order(seating_blocks, data)
	
class Project:
	""""""
	def __init__(self, event_id, name, date_start, date_end, url=None, seating=None):
		self.name = name
		self.date_start = date_start
		self.date_end = date_end
		self.id = event_id
		self.url = url
		self.seating = seating

	def save_to_calendar(self, calendar, filename='my.ics'):
		"""The method saves the project on the given calendar as a new event with all_day property. Default filename
		is 'my.ics' """
		c = calendar
		e = Event()
		e.name = self.name
		e.begin = self.date_start
		e.end = self.date_end
		e.url = self.url
		e.description = str(self.seating)
		e.make_all_day()
		c.events.add(e)
		with open(f'./{filename}', 'w') as my_file:
			my_file.writelines(c)
	
	def save_to_db(self):
		"""Saves the project to the database"""
		start = datetime.datetime.strptime(self.date_start, "%Y-%m-%d")
		end = datetime.datetime.strptime(self.date_end, "%Y-%m-%d")
		# Checking if the project exists
		existing_project = ProjectDb.query.get(self.id)
		if existing_project:
			logger.debug(f"Project {self.name} already exists in the database. Updating...")
			existing_project.name = self.name
			existing_project.start_date = start
			existing_project.end_date = end
			existing_project.url = self.url
			existing_project.seating = self.seating
			existing_project.save()
			return
		project = ProjectDb(
			id=self.id,
			name=self.name,
			start_date=start,
			end_date=end,
			url=self.url,
			seating=self.seating
		)
		project.save()

def fetch_projects(data) -> list[Project]:
	project_list = []
	for ev in data['results']:
		project = Project(
			event_id=ev['id'],
			name=ev['properties']['Name']['title'][0]['text']['content'],
			date_start=ev['properties']['Date']['date']['start'],
			date_end=ev['properties']['Date']['date']['end'],
		)
		try:
			project.seating = get_seating_positions(ev['id'], os.getenv('NOTION_TOKEN'))
		except Exception as e:
			logger.error(f"Error fetching seating positions: {type(e).__name__} {e}")
		project.url = ev['url']
		# print(project.__dict__)
		project_list.append(project)
	project_list.sort(key=lambda x: x.date_start)
	return project_list

def create_calendar(project_list: json, filename='geca_calendar.ics' , save=True, save_to_json=False) -> None:
	"""Given a json and a filename it iterates through the results, creates instances of the Project class, saves them as events in a
	ics calendar and returns a list of Projects. Default filename is geca_calendar.ics. Optionally it saves the data in a json file"""
	project_calendar = Calendar()
	if save:
		for project in project_list:
			project.save_to_calendar(project_calendar, filename=filename)
	if save_to_json:
		projects_json = [project.__dict__ for project in project_list]
		save_json(projects_json, name='projects.json')

def find_project_by_id(project_id: str, projects: json) -> dict | None:
	"""Given a project_id and a list of projects it returns the project with the given id"""
	for p in projects:
		# print("Type of p: ", type(p))
		if project_id == p['id']:
			return p
	return None

def add_hash_to_db(hash: str, projects: list[Project]):
	"""Add a hash to the database"""
	logger.debug(f"Creating custom calendar with hash {hash}")
	existing_hash = CalendarHash.query.filter_by(hash=hash).first()
	if existing_hash:
		logger.debug(f"Hash {hash} already exists in the database. Skipping...")
		return # TODO: handle this case better
	hash_obj = CalendarHash(hash=hash)
	for project in projects:
		project_db_obj = ProjectDb.query.get(project.id)
		if not project_db_obj:
			logger.debug(f"Project {project.name} not found in the database. Skipping...")
			continue # TODO: handle this case better
		hash_obj.projects.append(project_db_obj)
		logger.debug(f"Adding project {project.name} to the custom calendar {hash}")
	logger.info("Saving custom calendar hash to the database")
	hash_obj.save()

def create_custom_project_list(selected_project_ids: str, projects: json) -> list[Project]:
	"""Given a list of project ids and a list of projects it returns a list of projects with the given ids"""
	project_list = []
	for id in selected_project_ids:
		project_dict = find_project_by_id(id, projects)
		project = Project(
			event_id=project_dict['id'],
			name=project_dict['name'],
			date_start=project_dict['date_start'],
			date_end=project_dict['date_end'],
			url = project_dict['url'],
			seating = project_dict['seating']
		)
		project_list.append(project)
	return project_list

def save_json(data, path='./', name='db.json'):
	logger.info("Saving json")
	with open(path + name, 'w', encoding='utf8') as f:
		json.dump(data, f, ensure_ascii=False)

def json_to_projects(data: json) -> list[Project]:
	project_list = []
	for project in data:
		# print(project)
		p = Project(
			project['id'], 
			project['name'], 
			project['date_start'], 
			project['date_end'], 
			project['url'], 
			project['seating']
			)
		project_list.append(p)
	return project_list