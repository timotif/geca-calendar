import os
from datetime import datetime
from config import UPDATE_EVERY, DIRECTORY

LAST_UPDATE = None
# LAST_UPDATE = datetime.datetime.now() # TODO: remove

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

	def create_full_calendar(self):
		path = f"{self.directory}/{self.ics_handler.filename}" if self.directory != "" else self.ics_handler.filename
		if self.is_up_to_date() and os.path.exists(path):
			return self.ics_handler.filename
		data = self.update_calendar()
		self.ics_handler.generate(data, path)
		return self.directory, self.ics_handler.filename

