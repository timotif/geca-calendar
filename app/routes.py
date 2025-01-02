from flask import Blueprint, current_app, send_from_directory

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
