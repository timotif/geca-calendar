from app.interfaces import DataSourceInterface
import requests
from app.logging_config import logger
from app.data_transfer_objects import ProjectDTO 
class NotionReader():
	"""Base class for Notion API readers"""
	def __init__(self, token: str):
		self.headers = {
			'Authorization': 'Bearer ' + token,
			'Notion-Version': '2022-06-28',
			'Content-Type': 'application/json',
		}

class NotionDatabaseReader(NotionReader, DataSourceInterface):
	"""Reads a Notion database
	@param token: Notion API token
	@param database_id: Database ID"""
	def __init__(self, token, database_id: str):
		NotionReader.__init__(self, token)
		self.url = f"https://api.notion.com/v1/databases/{database_id}/query"

	def fetch_data(self):
		logger.debug("Fetching data from database")
		response = requests.request("POST", self.url, headers=self.headers)
		data = response.json()
		logger.debug(f"Status code: {response.status_code}")
		return data.get('results', [])

class NotionBlockChildrenReader(NotionReader, DataSourceInterface):
	"""Reads children of a block
	@param token: Notion API token
	@param page_id: Page ID of the block"""
	def __init__(self, token: str, page_id: str):
		NotionReader.__init__(self, token)
		self.url = f"https://api.notion.com/v1/blocks/{page_id}/children"

	def fetch_data(self) -> list[dict]:
		logger.debug("Fetching data from block")
		response = requests.request("GET", self.url, headers=self.headers)
		data = response.json()
		logger.debug(f"Status code: {response.status_code}")
		return data.get('results', [])

class NotionDataSource(DataSourceInterface):
	"""Reads a Notion database and fetches seating positions"""
	def __init__(self, token: str, database_id: str):
		self.database_reader = NotionDatabaseReader(token, database_id)
		self.token = token
	
	def is_seating_block(self, block: dict) -> bool: # TODO: error handling
		return block['type'] == 'paragraph' and \
			len(block['paragraph']['rich_text']) != 0 and \
			(block['paragraph']['rich_text'][0]['plain_text'].lower() == "seating positions" or \
			block['paragraph']['rich_text'][0]['plain_text'].lower() == "seating position")

	def is_divider(self, block: dict) -> bool: # TODO: error handling
		return block['type'] == 'divider'

	def fetch_project_blocks(self, project: dict) -> list[dict]:
		return NotionBlockChildrenReader(self.token, project['id']).fetch_data()
	
	def process_seating_section(self, blocks: iter) -> dict:
		seating = {}
		block = next(blocks, None)
		while block and not self.is_divider(block):
			try:
				key = block['child_page']['title']
			except KeyError as e:
				if e.args[0] == 'child_page':
					logger.debug("Empty block found")
			value = block['id']
			logger.debug(f"Adding seating to {key} with id {value}")
			seating[key] = NotionBlockChildrenReader(self.token, value).fetch_data()
			block = next(blocks, None)
		return seating

	def parse_seating(self, data: list[dict]) -> str:
		if len(data) == 0:
			return "Seating positions: TBD"
		seating = ""
		for repertoire in data:
			seating += f"{repertoire}\n"
			for block in data[repertoire]:
				type = block['type']
				if type == 'paragraph' and len(block['paragraph']['rich_text']) != 0:
					text = "\n".join([t['plain_text'] for t in block['paragraph']['rich_text']])
					seating += text + "\n" # Section list
			seating += "\n"
		return seating
	
	def extract_seating_from_blocks(self, project_blocks: list[dict]) -> dict:
		seating = {}
		blocks = iter(project_blocks)
		for block in blocks:
			if self.is_seating_block(block):
				logger.debug("Seating positions found")
				# Seating is set up
				seating = self.process_seating_section(blocks)
				break
		return seating

	def to_project_dto(self, project: dict) -> ProjectDTO:
		return ProjectDTO(
			id = project['id'],
			name = project['properties']['Name']['title'][0]['text']['content'],
			date_start=project['properties']['Date']['date']['start'],
			date_end=project['properties']['Date']['date']['end'],
			url=project['url'],
			seating=self.parse_seating(project['seating'])
		)
	
	def fetch_data(self) -> list[ProjectDTO]:
		logger.info("Fetching data")
		projects_data = self.database_reader.fetch_data() # Projects in calendar
		if not projects_data:
			logger.error("No projects found")
			return []
		for project in projects_data:
			project['blocks'] = self.fetch_project_blocks(project) # Blocks in project
			project['seating'] = self.extract_seating_from_blocks(project['blocks']) # Parse blocks to find seating
		projects = [self.to_project_dto(project) for project in projects_data]
		projects.sort(key=lambda x: x.date_start)
		return projects