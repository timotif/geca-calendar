from database import db
from data_transfer_objects import ProjectDTO

# Association table for many-to-many relationship between ProjectDb and CalendarHash
custom_calendar = db.Table('custom_calendar',
	db.Column('project_id', db.String(50), db.ForeignKey('project_db.id'), primary_key=True),
	db.Column('calendar_hash_hash', db.String(8), db.ForeignKey('calendar_hash.hash'), primary_key=True),
)

class ProjectDb(db.Model):
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
	
	def __repr__(self):
		return self.name
	
	def save(self):
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
	hash = db.Column(db.String(8), primary_key= True)
	projects = db.relationship(
		"ProjectDb", 
		secondary=custom_calendar, 
		back_populates='custom_calendars'
		)
	
	def save(self):
		db.session.add(self)
		db.session.commit()