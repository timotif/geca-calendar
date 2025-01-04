from flask import Blueprint, current_app, render_template, send_from_directory, jsonify, request, url_for
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

@calendar.route("/projects", methods=["GET", "POST"])
def custom_calendar():
	if request.method == "GET":
		return render_template("projects.html")
	# POST method
	calendar_file = current_app.calendar.create_custom_calendar(request.form.getlist('selected_projects'))
	if calendar_file:
		full_url = url_for("calendar.get_custom_calendar", filename=calendar_file, _external=True)
		return render_template("custom.html", url=full_url)
	return bad_request()

@calendar.route("/<path:filename>")
def get_custom_calendar(filename):
	if not filename.endswith(".ics"):
		return auth_required()
	try:
		current_app.calendar.update_custom_calendars([filename[:-4]])
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