from flask import Blueprint, current_app, render_template, send_from_directory, jsonify, request, url_for, flash
from config import DIRECTORY
from logging_config import app_logger as logger

calendar = Blueprint("calendar", __name__)

@calendar.route("/")
def index():
	try:
		return render_template("index.html")
	except Exception as e:
		logger.error(e)
		return internal_error()

@calendar.route("/all")
def get_general_calendar():
	try:
		dir, calendar_file = current_app.calendar.create_full_calendar()
		return send_from_directory(dir, calendar_file)
	except Exception as e:
		logger.error(e)
		return internal_error()

@calendar.route("/update")
def force_update():
	try:
		projects = current_app.calendar.update_calendar(force_update=True)
		dir, calendar_file = current_app.calendar.create_full_calendar()
		flash("Calendar updated successfully!", "success")
	except Exception as e:
		logger.error(e)
		flash("Failed to update calendar.", "error")
	return render_template("index.html")

@calendar.route("/rebuild")
def rebuild_custom_calendars():
	try:
		current_app.calendar.update_custom_calendars()
		flash("Custom calendars rebuilt successfully!", "success")
	except Exception as e:
		logger.error(e)
		flash("Failed to rebuild custom calendars.", "error")
	return render_template("index.html")

@calendar.route("/fetch_projects")
def fetch_projects():
	try:
		projects = current_app.calendar.update_calendar()
		projects.sort(key=lambda x: x.date_start)
		return jsonify(projects)
	except Exception as e:
		logger.error(e)
		return internal_error()

@calendar.route("/projects", methods=["GET", "POST"])
def custom_calendar():
	try:
		if request.method == "GET":
			return render_template("projects.html")
		# POST method
		calendar_file = current_app.calendar.create_custom_calendar(request.form.getlist('selected_projects'))
		if calendar_file:
			full_url = url_for("calendar.get_custom_calendar", filename=calendar_file, _scheme='https', _external=True)
			return render_template("custom.html", url=full_url)
		return bad_request()
	except Exception as e:
		logger.error(e)
		return internal_error()

@calendar.route("/<path:filename>")
def get_custom_calendar(filename):
	if not filename.endswith(".ics"):
		return auth_required()
	try:
		current_app.calendar.update_custom_calendars([filename[:-4]])
		return send_from_directory(DIRECTORY, filename)
	except FileNotFoundError as e:
		logger.error(e)
		return page_not_found()
	except Exception as e:
		logger.error(e)
		return internal_error()

@calendar.errorhandler(400)
def bad_request():
	return render_template('error_pages/400.html'), 400

@calendar.errorhandler(403)
def auth_required():
	return render_template('error_pages/403.html'), 403

@calendar.errorhandler(404)
def page_not_found():
	return render_template('error_pages/404.html'), 404

@calendar.errorhandler(500)
def internal_error():
	return render_template('error_pages/500.html'), 500