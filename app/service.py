import os
from datetime import datetime
import hashlib
import base64
from app.config import UPDATE_EVERY, DIRECTORY
from app.logging_config import logger

LAST_UPDATE = None

class CalendarService():
	"""Calendar Service for managing and generating calendar files.
	This service handles calendar data management, updates, and file generation. It interfaces
	with a data source for retrieving calendar information, a database for storage, and an
	ICS handler for calendar file creation.
	Attributes:
		data_source: Source object for fetching calendar data
		db: Database interface for storing and retrieving calendar data
		ics_handler: Handler for ICS file operations
		last_update: Datetime of the last calendar update
		directory: String path to the calendar files directory
	Methods:
		create_full_calendar(): Generates a complete calendar file
		create_custom_calendar(project_ids): Creates a calendar file for specific projects
	"""

	def __init__(self, data_source, db, ics_handler):
		self.data_source = data_source
		self.db = db
		self.ics_handler = ics_handler
		self.last_update = LAST_UPDATE
		self.directory = DIRECTORY
	
	def is_calendar_up_to_date(self):
		return self.last_update is not None and datetime.now() - self.last_update < UPDATE_EVERY

	def __is_project_up_to_date(self, project):
		last_edited = self.data_source.project_last_updated(project)
		project_db = self.db.get_by_id(project['id'])
		return project_db and project_db.last_edited >= last_edited

	def update_projects(self, projects: list) -> tuple[list, list]:
		updated_projects = []
		fetched_projects = []
		for p in projects:
			if not self.__is_project_up_to_date(p):
				self.data_source.fetch_project(p)
				updated_projects.append(self.data_source.to_project_dto(p))
			else:
				fetched_projects.append(self.db.get_by_id(p['id']).to_project_dto())
		# Save updated projects to database
		self.db.save(updated_projects)
		return updated_projects, fetched_projects

	def update_custom_calendars(self,  hashes: list[str]=None):
		if not self.is_calendar_up_to_date():
			self.update_calendar()
		custom_calendars = self.db.get_all_hashes() if not hashes \
			else [self.db.get_by_hash(hash) for hash in hashes]
		for hash in custom_calendars:
			projects = self.db.get_projects_by_hash(hash.hash)
			for project in projects:
				if project.last_edited > hash.last_edited:
					logger.debug(f"Updating calendar {hash.hash}")
					self.create_custom_calendar([p.id for p in projects])
					break

	def update_calendar(self):
		# Fetch projects from notion calendar
		projects = self.data_source.fetch_projects()
		logger.debug(f"Fetched {len(projects)} projects")
		# Identify outdated or missing projects and fetch just those 
		outdated_projects, data = self.update_projects(projects)
		assert len(outdated_projects) + len(data) == len(projects)
		logger.debug(f"Outdated projects: {len(outdated_projects)}")
		data += outdated_projects
		self.last_update = datetime.now()
		return data
	
	def __generate_hashed_filename(self, selected_project_ids: str) -> str:
		"""From a list of project ids, generate a hashed filename"""
		input_str = ' '.join(map(str, selected_project_ids))
		hashed = hashlib.sha256(input_str.encode())
		hash_base64 = base64.urlsafe_b64encode(hashed.digest())
		return hash_base64.decode()[:8]
	
	def create_full_calendar(self) -> tuple[str, str]:
		path = os.path.join(self.directory, self.ics_handler.filename)
		if not (self.is_calendar_up_to_date() and os.path.exists(path)):
			data = self.update_calendar()
			self.ics_handler.generate(data, path)
		return self.directory, self.ics_handler.filename

	def create_custom_calendar(self, project_ids: list[str]) -> str:
		if not project_ids:
			return ""
		if not self.is_calendar_up_to_date():
			self.update_calendar()
		hash = self.__generate_hashed_filename(project_ids)
		filename = f"{hash}.ics"
		file_path = os.path.join(self.directory, filename)
		
		# Try to get existing projects from DB first
		projects_db = self.db.get_projects_by_hash(hash) or [
			self.db.get_by_id(project_id) for project_id in project_ids
		]
		
		# Return early if no projects found
		if not projects_db:
			return ""
			
		# Convert DB objects to DTOs and update if needed
		projects = [p.to_project_dto() for p in projects_db if p]
		
		# Generate calendar file
		self.ics_handler.generate(projects, file_path)
		
		# Save calendar metadata
		self.db.save_custom_calendar(hash, project_ids)
		
		return filename