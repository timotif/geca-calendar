import os
from datetime import datetime
from config import UPDATE_EVERY, DIRECTORY
import hashlib
import base64

LAST_UPDATE = None

class CalendarService():
	def __init__(self, data_source, db, ics_handler):
		self.data_source = data_source
		self.db = db
		self.ics_handler = ics_handler
		self.last_update = LAST_UPDATE
		self.directory = DIRECTORY
	
	def is_up_to_date(self):
		return self.last_update is not None and datetime.now() - self.last_update < UPDATE_EVERY

	def update_calendar(self):
		data = self.data_source.fetch_data()
		self.db.save(data)
		self.last_update = datetime.now()
		return data
	
	def generate_hashed_filename(self, selected_project_ids: str) -> str:
		"""From a list of project ids, generate a hashed filename"""
		input_str = ' '.join(map(str, selected_project_ids))
		hashed = hashlib.sha256(input_str.encode())
		hash_base64 = base64.urlsafe_b64encode(hashed.digest())
		return hash_base64.decode()[:8]
	
	def create_full_calendar(self):
		path = os.path.join(self.directory, self.ics_handler.filename)
		if not (self.is_up_to_date() and os.path.exists(path)):
			data = self.update_calendar()
			self.ics_handler.generate(data, path)
		return self.directory, self.ics_handler.filename

	def create_custom_calendar(self, project_ids: list[str]):
		hash = self.generate_hashed_filename(project_ids)
		hash_db = self.db.get_by_hash(hash)
		print(hash_db)
		projects = [self.db.get_by_id(project).to_project_dto() for project in project_ids]
		self.ics_handler.generate(projects, os.path.join(self.directory, f"{hash}.ics"))
		self.db.save_calendar(hash, project_ids)
		return self.directory, f"{hash}.ics"