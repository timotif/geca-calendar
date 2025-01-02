from interfaces import StorageInterface
from flask_sqlalchemy import SQLAlchemy
from models import ProjectDb, CalendarHash
from data_transfer_objects import ProjectDTO
from datetime import datetime

class ProjectRepository(StorageInterface):
	def __init__(self, db: SQLAlchemy):
		self.db = db

	def save(self, data: list[dict]):
		for project_dto in data:
			project = ProjectDb.query.get(project_dto.id)
			if project:
				self.db.session.add(project) # TODO: Test
				self.update_project(project, project_dto)
			else:
				self.create_project(project_dto)
		self.db.session.commit()
	
	def get(self, query: dict) -> list[dict]:
		return ProjectDb.query.filter_by(**query).all()

	def get_all(self):
		return ProjectDb.query.all()
	
	def get_by_id(self, id: str) -> dict:
		return ProjectDb.query.get(id).__dict__

	def create_project(self, project: ProjectDTO):
		p = ProjectDb(
			id=project.id,
			name=project.name,
			date_start=datetime.strptime(project.date_start, "%Y-%m-%d"),
			date_end=datetime.strptime(project.date_end, "%Y-%m-%d"),
			url=project.url,
			seating=project.seating
		)
		self.db.session.add(p)
		return p

	def update_project(self, project: ProjectDb, project_dto: ProjectDTO):
		project.name = project_dto.name
		project.date_start = datetime.strptime(project_dto.date_start, "%Y-%m-%d")
		project.date_end = datetime.strptime(project_dto.date_end, "%Y-%m-%d")
		project.url = project_dto.url
		project.seating = project_dto.seating

	def save_calendar(self, hash: str, project_ids: list[str]):
		calendar = CalendarHash.query.filter_by(hash=hash).first()
		if not calendar:
			calendar = CalendarHash(hash=hash)
		self.db.session.add(calendar)
		for project_id in project_ids:
			project = ProjectDb.query.get(project_id)
			if project:
				calendar.projects.append(project)
		self.db.session.commit()
