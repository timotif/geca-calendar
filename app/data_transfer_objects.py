from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date

@dataclass
class ProjectDTO:
	"""Data Transfer Object for Project.

	A class to represent project data for transfer between different parts of the application.

	Attributes:
		id (str): Unique identifier for the project
		name (str): Name of the project
		date_start (date): Start date of the project in date format
		date_end (date): End date of the project in date format
		url (str, optional): URL associated with the project. Defaults to empty string
		repertoire (str, optional): Repertoire information for the project. Defaults to empty string
		seating (str, optional): Seating information for the project. Defaults to empty string

	Raises:
		ValueError: If dates are not in valid format (must be date object or YYYY-MM-DD string)
		ValueError: If date_end is earlier than date_start

	"""
	id: str
	name: str
	date_start: date
	date_end: date
	url: Optional[str] = None
	repertoire: Optional[str] = None
	seating: Optional[str] = None

	def __post_init__(self):
		"""Validate dates after initialization"""
		dates = [self.date_start, self.date_end]
		for d in dates:
			if not isinstance(d, date):
				try:
					if len(str(d)) > 10:
						d = datetime.fromisoformat(str(d)).date()
					else:
						d = datetime.strptime(str(d), '%Y-%m-%d').date()
				except ValueError:
					raise ValueError("Date must be a date object or string in YYYY-MM-DD or ISO format")
		if self.date_end < self.date_start:
			raise ValueError("End date cannot be earlier than start date")