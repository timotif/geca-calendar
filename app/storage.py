from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from interfaces import StorageInterface
from models import ProjectDb, CalendarHash
from data_transfer_objects import ProjectDTO
from pathlib import Path

class ProjectRepository(StorageInterface):
	def __init__(self, db: SQLAlchemy):
		self.db = db

	def exists(self) -> bool:
		return Path(self.db.engine.url.database).exists()

	def save(self, data: list[dict]):
		"""
		Saves a list of project DTOs to the database.
		This method handles both creation of new projects and updates to existing ones.
		For each project DTO in the input list, it checks if a corresponding project exists
		in the database. If it exists, the project is updated with the new data.
		If it doesn't exist, a new project is created.
		Args:
			data (list[dict]): A list of project DTOs to be saved to the database.
							   Each DTO should contain an 'id' field and other project attributes.
		Note:
			Changes are committed to the database after all projects have been processed.
		"""
		if not self.exists():
			self.db.create_all()
		for project_dto in data:
			project = self.get_by_id(project_dto.id)
			if project:
				self.update_project(project, project_dto)
			else:
				self.create_project(project_dto)
		self.db.session.commit()
	
	def get(self, query: dict) -> list[dict]:
		return ProjectDb.query.filter_by(**query).all()

	def get_all(self):
		return ProjectDb.query.all()
	
	def get_by_id(self, id: str) -> ProjectDb:
		return self.db.session.get(ProjectDb, id)

	def get_by_hash(self, hash: str):
		return self.db.session.query(CalendarHash).filter_by(hash=hash).first()
	
	def get_projects_by_hash(self, hash: str):
		calendar_hash = self.get_by_hash(hash)
		if calendar_hash:
			return calendar_hash.projects
		return []

	def get_all_hashes(self):
		return CalendarHash.query.all()

	def create_project(self, project: ProjectDTO):
		p = ProjectDb(
			id=project.id,
			name=project.name,
			date_start=datetime.strptime(project.date_start, "%Y-%m-%d"),
			date_end=datetime.strptime(project.date_end, "%Y-%m-%d"),
			url=project.url,
			repertoire=project.repertoire,
			seating=project.seating
		)
		self.db.session.add(p)
		return p

	def update_project(self, project: ProjectDb, project_dto: ProjectDTO):
		project.name = project_dto.name
		project.date_start = datetime.strptime(project_dto.date_start, "%Y-%m-%d")
		project.date_end = datetime.strptime(project_dto.date_end, "%Y-%m-%d")
		project.url = project_dto.url
		project.repertoire = project_dto.repertoire
		project.seating = project_dto.seating

	def save_custom_calendar(self, hash: str, project_ids: list[str]):
		calendar = CalendarHash.query.filter_by(hash=hash).first()
		if not calendar:
			calendar = CalendarHash(hash=hash)
			self.db.session.add(calendar)
			for project_id in project_ids:
				project = ProjectDb.query.get(project_id)
				if project:
					calendar.projects.append(project)
		calendar.last_edited = datetime.now()
		self.db.session.commit()
