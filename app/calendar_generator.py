from ics import Calendar, Event
from app.interfaces import CalendarGeneratorInterface
from app.logging_config import logger
from app.config import FILENAME

class ICSCalendarGenerator(CalendarGeneratorInterface):
	def __init__(self, filename: str=FILENAME):
		self.filename = filename
		self.events = set()
		self.calendar = Calendar()

	def add_event(self, event: dict):
		e = Event()
		e.name = event.name
		e.begin = event.date_start
		e.end = event.date_end
		e.url = event.url
		e.description = str(event.seating)
		e.make_all_day()
		self.events.add(e)
		return e

	def add_to_calendar(self, event: Event):
		self.calendar.events.add(event)

	def save(self, filename=""):
		if not filename:
			filename = self.filename
		logger.info(f"Saving calendar to {filename}")
		with open(f'{filename}', 'w') as my_file:
			my_file.writelines(self.calendar)

	def generate(self, events: list[dict], filename: str=""):
		if not filename:
			filename = self.filename
		for event in events:
			new_event = self.add_event(event)
			self.add_to_calendar(new_event)
		self.save(filename)

