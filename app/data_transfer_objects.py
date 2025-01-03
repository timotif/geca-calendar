from dataclasses import dataclass

@dataclass
class ProjectDTO:
	"""Data Transfer Object for Project"""
	id: str
	name: str
	date_start: str
	date_end: str
	url: str = ""
	seating: str = ""