import requests
from datetime import timezone
import dateutil.parser
from dateutil import tz
from interfaces import DataSourceInterface
from logging_config import logger
from data_transfer_objects import ProjectDTO

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

	def fetch_data(self) -> list[dict]:
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
	"""A data source implementation that fetches project data from Notion.
	This class implements the DataSourceInterface to read project data from a Notion database,
	including seating position information stored in child pages.
	Attributes:
		database_reader (NotionDatabaseReader): Reader for the main Notion database
		token (str): Authentication token for Notion API access
	Args:
		token (str): Authentication token for Notion API
		database_id (str): ID of the Notion database to read from
	Returns:
		list[ProjectDTO]: List of projects with their associated data
	Example:
		>>> notion_source = NotionDataSource("token", "database_id") 
		>>> projects = notion_source.fetch_data()
		>>> print(projects[0].name)
		'Project Name'
	"""
	def __init__(self, token: str, database_id: str):
		self.database_reader = NotionDatabaseReader(token, database_id)
		self.token = token
	
	def __is_seating_block(self, block: dict) -> bool: # TODO: error handling
		return block['type'] == 'paragraph' and \
			len(block['paragraph']['rich_text']) != 0 and \
			(block['paragraph']['rich_text'][0]['plain_text'].lower() == "seating positions" or \
			block['paragraph']['rich_text'][0]['plain_text'].lower() == "seating position")

	def __is_repertoire_block(self, block: dict) -> bool: 
		program_headers = ["program", "programme", "programs", "repertoire"]
		return block['type'] == 'paragraph' and \
			len(block['paragraph']['rich_text']) != 0 and \
			block['paragraph']['rich_text'][0]['plain_text'].lower() in program_headers

	def __is_divider(self, block: dict) -> bool: # TODO: error handling
		return block['type'] == 'divider'

	def __fetch_project_blocks(self, project: dict) -> list[dict]:
		return NotionBlockChildrenReader(self.token, project['id']).fetch_data()
	
	def __process_seating_section(self, blocks: iter) -> dict:
		seating = {}
		block = next(blocks, None)
		while block and not self.__is_divider(block):
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

	def __parse_seating(self, data: list[dict]) -> str:
		if len(data) == 0 :
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
	
	def __extract_seating_from_blocks(self, project_blocks: list[dict]) -> dict:
		seating = {}
		blocks = iter(project_blocks)
		for block in blocks:
			if self.__is_seating_block(block):
				logger.debug("Seating positions found")
				# Seating is set up
				seating = self.__process_seating_section(blocks)
				break
		return seating

	def to_project_dto(self, project: dict) -> ProjectDTO:
		return ProjectDTO(
			id = project['id'],
			name = project['properties']['Name']['title'][0]['text']['content'],
			date_start=project['properties']['Date']['date']['start'],
			date_end=project['properties']['Date']['date']['end'],
			url=project['url'],
			seating=self.__parse_seating(project.get('seating'))
		)
	
	def project_last_updated(self, project: dict):
		"""
		Convert project's last edited time from UTC to local timezone.
		Args:
			project (dict): A dictionary containing project information including 'last_edited_time' key
						   with UTC timestamp in ISO 8601 format.
		Returns:
			datetime.datetime: Local datetime of when the project was last edited, with timezone info removed.
		"""
		
		# Parse UTC timestamp to datetime object and convert to local timezone
		last_edited_utc = dateutil.parser.parse(project['last_edited_time'])
		local_tz = tz.tzlocal()
		# Discarding timezone info to allow comparison with location naive datetime in ProjectService.__is_project_up_to_date
		return last_edited_utc.astimezone(local_tz).replace(tzinfo=None)
	
	def __extract_repertoire_from_blocks(self, project_blocks: list[dict]) -> str:
		repertoire = ""
		blocks = iter(project_blocks)
		for block in blocks:
			if self.__is_repertoire_block(block):
				type = block['type']
				print("Repertoire found")
				text = [t['plain_text'] for t in block[type]['rich_text']]
				# Extract rep from blocks
				repertoire = "\n".join(text) + "\n"
				block = next(blocks, None)
				while block and not self.__is_divider(block):
					type = block['type']
					try:
						repertoire += " ".join([t['plain_text'] for t in block[type]['rich_text'] if not self.__is_divider(block)]) + "\n"
					except KeyError:
						print("KeyError triggered. Type: ", type)
					block = next(blocks, None)
		return repertoire

	def fetch_project(self, project: dict):
		"""
		Fetches and processes project information from Notion.
		This method enriches the given project dictionary with additional information:
		- Fetches all blocks within the project
		- Extracts seating information from the blocks
		Args:
			project (dict): Dictionary containing project information
		Returns:
			None: The method modifies the project dictionary in-place by adding:
				- 'blocks': List of blocks contained in the project
				- 'seating': Seating information extracted from blocks
		"""

		project['blocks'] = self.__fetch_project_blocks(project) # Blocks in project
		project['repertoire'] = self.__extract_repertoire_from_blocks(project['blocks'])
		project['seating'] = self.__extract_seating_from_blocks(project['blocks']) # Parse blocks to find seating

	def fetch_projects(self):
		"""
		Fetches projects from the Notion database.
		This method retrieves all projects stored in the Notion calendar database
		using the database reader instance.
		Returns:
			list: A list of projects from the Notion calendar database.
		"""

		return self.database_reader.fetch_data()

	def fetch_data(self) -> list[ProjectDTO]:
		"""
		Fetches and processes project data from Notion.
		This method performs the following operations:
		1. Retrieves all projects from Notion
		2. For each project, fetches additional project-specific data
		3. Converts the raw data into ProjectDTO objects
		Returns:
			list[ProjectDTO]: A sorted list of ProjectDTO objects representing projects.
							 Returns an empty list if no projects are found.
		"""

		logger.info("Fetching data")
		projects_data = self.fetch_projects() # Projects in calendar
		if not projects_data:
			logger.error("No projects found")
			return []
		for project in projects_data:
			self.fetch_project(project) # Enriches projects with blocks and seating
		projects = [self.to_project_dto(project) for project in projects_data] # Convert to DTO
		return projects