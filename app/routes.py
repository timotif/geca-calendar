from flask import Blueprint

calendar = Blueprint("main", __name__)

@calendar.route("/")
def index():
	return "Hello world"