from config import DevConfig, ProdConfig
from flask import Flask
from database import init_db
from routes import calendar

def create_app(config=None):
	app = Flask(__name__)
	
	# Load config
	if config == None:
		config = DevConfig if app.debug else ProdConfig
	app.config.from_object(config)

	# Init database
	init_db(app)

	# Init blueprints
	app.register_blueprint(calendar)
	return app

if __name__ == "__main__":
	app = create_app()
	app.run(debug=True, host="0.0.0.0", port=8080)