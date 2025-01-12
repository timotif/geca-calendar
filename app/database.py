from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
	db.init_app(app)
	migrate.init_app(app, db)
	with app.app_context():
		db.create_all()

def get_db(app) -> SQLAlchemy:
	"""
	Retrieves the database instance after initializing it.
	This function ensures the database is properly initialized before returning
	the database instance for use.
	Args:
		app: The Flask application instance.
	Returns:
		SQLAlchemy: The initialized database instance.
	"""

	init_db(app)
	return db