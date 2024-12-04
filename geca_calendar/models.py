from database import db

# Association table for many-to-many relationship between ProjectDb and CalendarHash
custom_calendar = db.Table('custom_calendar',
	db.Column('project_id', db.String(50), db.ForeignKey('project_db.id')),
	db.Column('calendar_hash_id', db.Integer, db.ForeignKey('calendar_hash.id'))
)

class ProjectDb(db.Model):
	id = db.Column(db.String(50), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	start_date = db.Column(db.Date, nullable=False)
	end_date = db.Column(db.Date, nullable=False)
	url = db.Column(db.String(100), nullable=True)
	seating = db.Column(db.String(5000), nullable=True)
	calendar_hashes = db.relationship('CalendarHash', secondary=custom_calendar, backref=db.backref('project_list', lazy=True), overlaps="projects, calendar_hashes_list")

	def __repr__(self):
		return self.name
	
	def save(self):
		db.session.add(self)
		db.session.commit()

class CalendarHash(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	hash = db.Column(db.String(8), nullable=False, unique=True)
	projects = db.relationship('ProjectDb', secondary=custom_calendar, backref=db.backref('calendar_hashes_list', lazy=True), overlaps="calendar_hashes, project_list")

	def save(self):
		db.session.add(self)
		db.session.commit()