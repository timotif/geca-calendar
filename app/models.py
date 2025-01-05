from database import db
from data_transfer_objects import ProjectDTO

# Association table for many-to-many relationship between ProjectDb and CalendarHash
custom_calendar = db.Table('custom_calendar',
	db.Column('project_id', db.String(50), db.ForeignKey('project_db.id'), primary_key=True),
	db.Column('calendar_hash_hash', db.String(8), db.ForeignKey('calendar_hash.hash'), primary_key=True),
)

class ProjectDb(db.Model):
	"""
	A database model representing a project in the system.
	This class represents a project entity with various attributes such as name, dates,
	URL, and seating information. It inherits from db.Model for database functionality.
	Attributes:
		id (str): Unique identifier for the project, serves as primary key
		name (str): Name of the project
		date_start (Date): Start date of the project
		date_end (Date): End date of the project
		url (str, optional): URL associated with the project
		seating (str, optional): Seating information for the project
		custom_calendars (relationship): Relationship with CalendarHash through custom_calendar table
	Methods:
		save(): Saves the project instance to the database
		to_project_dto(): Converts the database model to a ProjectDTO object
	Returns:
		str: String representation of the project (project name)
	"""

	id = db.Column(db.String(50), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	date_start = db.Column(db.Date, nullable=False)
	date_end = db.Column(db.Date, nullable=False)
	url = db.Column(db.String(100), nullable=True)
	seating = db.Column(db.String(5000), nullable=True)
	custom_calendars = db.relationship(
		"CalendarHash", 
		secondary=custom_calendar, 
		back_populates='projects'
		)
	last_edited = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
	
	def __repr__(self):
		return self.name
	
	def save(self) -> None:
		db.session.add(self)
		db.session.commit()

	def to_project_dto(self) -> ProjectDTO:
		return ProjectDTO(
			id = self.id,
			name = self.name,
			date_start=self.date_start,
			date_end=self.date_end,
			url=self.url,
			seating=self.seating
		)

class CalendarHash(db.Model):
	"""
	A SQLAlchemy model representing a calendar hash and its associated projects.
	This class manages the relationship between calendar hashes and projects 
	through a many-to-many relationship using the custom_calendar association table.
	Attributes:
		hash (str): The primary key hash string, limited to 8 characters
		projects (list): List of ProjectDb objects associated with this calendar hash
	Methods:
		save(): Persists the calendar hash instance to the database
	"""

	hash = db.Column(db.String(8), primary_key= True)
	projects = db.relationship(
		"ProjectDb", 
		secondary=custom_calendar, 
		back_populates='custom_calendars'
		)
	last_edited = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
	
	def save(self):
		db.session.add(self)
		db.session.commit()