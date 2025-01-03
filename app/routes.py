from flask import Blueprint, current_app, render_template, send_from_directory, jsonify, request
from app.config import DIRECTORY
calendar = Blueprint("calendar", __name__)

@calendar.route("/")
def get_general_calendar():
	dir, calendar_file = current_app.calendar.create_full_calendar()
	return send_from_directory(dir, calendar_file)

@calendar.route("/fetch_projects")
def fetch_projects():
	projects = current_app.calendar.update_calendar()
	projects.sort(key=lambda x: x.date_start)
	return jsonify(projects)

@calendar.route("/list", methods=["GET", "POST"])
def custom_calendar():
	if request.method == "GET":
		return render_template("projects.html")
	# POST method
	dir, calendar_file = current_app.calendar.create_custom_calendar(request.form.getlist('selected_projects'))
	if dir and calendar_file:
		return send_from_directory(dir, calendar_file)
	return bad_request()

@calendar.route("/<path:filename>")
def get_custom_calendar(filename):
	if not filename.endswith(".ics"):
		return auth_required()
	try:
		return send_from_directory(DIRECTORY, filename)
	except FileNotFoundError:
		return page_not_found()

@calendar.errorhandler(400)
def bad_request():
		return "Bad request", 400

@calendar.errorhandler(403)
def auth_required():
		return "You're not authorized to get this file", 403

@calendar.errorhandler(404)
def page_not_found():
	return "I couldn't find the requested resource", 404