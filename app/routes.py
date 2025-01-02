from flask import Blueprint, current_app, render_template, send_from_directory, jsonify, request

calendar = Blueprint("calendar", __name__)

"""
"/": sends the general calendar
"<hash>": sends the custom hash calendar
"/fetch_projects": api endpoint
"/list": shows the projects to pick 
"""

@calendar.route("/")
def get_general_calendar():
	dir, calendar_file = current_app.calendar.create_full_calendar()
	return send_from_directory(dir, calendar_file)

@calendar.route("/fetch_projects")
def fetch_projects():
	projects = current_app.calendar.data_source.fetch_data()
	return jsonify(projects)

@calendar.route("/list", methods=["GET", "POST"])
def custom_calendar():
	if request.method == "GET":
		return render_template("projects.html")
	# POST method
	dir, calendar_file = current_app.calendar.create_custom_calendar(request.form.getlist('selected_projects'))
	return send_from_directory(dir, calendar_file)