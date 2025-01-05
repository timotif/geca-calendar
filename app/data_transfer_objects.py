from dataclasses import dataclass

@dataclass
class ProjectDTO:
	"""Data Transfer Object for Project.

	A class to represent project data for transfer between different parts of the application.

	Attributes:
		id (str): Unique identifier for the project
		name (str): Name of the project
		date_start (str): Start date of the project in string format
		date_end (str): End date of the project in string format
		url (str, optional): URL associated with the project. Defaults to empty string
		seating (str, optional): Seating information for the project. Defaults to empty string
	"""
	id: str
	name: str
	# TODO: Handle date format through the app
	date_start: str
	date_end: str
	url: str = ""
	seating: str = ""