from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProjectDTO:
	"""Data Transfer Object for Project"""
	id: str
	name: str
	date_start: datetime
	date_end: datetime
	url: str = ""
	seating: str = ""