from ics import Calendar, Event
from interfaces import CalendarGeneratorInterface
from logging_config import calendar_generator_logger as logger
from config import FILENAME

class ICSCalendarGenerator(CalendarGeneratorInterface):
	"""Calendar generator implementation for ICS format.
	This class implements the CalendarGeneratorInterface to create ICS calendar files.
	It handles the creation, modification and storage of calendar events in the ICS format.
	Attributes:
		filename (str): The name of the file where the calendar will be saved
		events (set): A set containing all Event objects
		calendar (Calendar): The main calendar object that holds all events
	Methods:
		generate(events, filename=""): Creates and saves a calendar with the provided events
		__add_event(event): Creates an Event object from event dictionary
		__add_to_calendar(event): Adds an event to the calendar
		__save(filename=""): Saves the calendar to a file
	Args:
		filename (str, optional): Name of the file where calendar will be saved. 
			Defaults to FILENAME constant.
	"""
	
	def __init__(self, filename: str=FILENAME):
		self.filename = filename
		self.events = set()

	def __populate_description(self, event: dict, repertoire: bool, seating: bool) -> str:
		description = f"{event.url}\n\n"
		if repertoire:
			description += f"{str(event.repertoire)}\n\n"
		if seating:
			description += f"{str(event.seating)}"
		return description

	def __add_event(self, event: dict, repertoire=True, seating=True) -> Event:
		e = Event()
		e.name = event.name
		e.begin = event.date_start
		e.end = event.date_end
		e.url = event.url
		e.description = self.__populate_description(event, repertoire, seating)
		e.make_all_day()
		self.events.add(e)
		return e

	def __save(self, calendar: Calendar, filename="") -> None:
		if not filename:
			filename = self.filename
		logger.info(f"Saving calendar to {filename}")
		with open(filename, 'w') as my_file:
			my_file.writelines(calendar.serialize_iter())

	def generate(self, events: list[dict], filename: str="") -> None:
		calendar = Calendar()
		if not filename:
			filename = self.filename
		for event in events:
			new_event = self.__add_event(event)
			calendar.events.add(new_event)
		self.__save(calendar, filename)

