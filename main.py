from flask import Flask, render_template, send_file
from notion_interface import read_database, create_calendar
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

token = os.environ.get("NOTION_TOKEN")
database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'

FILENAME = 'geca2425.ics'

@app.route('/')
def get_events():
    data = read_database(database_id, token)
    projects = create_calendar(data, FILENAME, True)
    return send_file(FILENAME)

@app.route('/download/<path:filename>')
def download_calendar(filename):
    return send_file(filename)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)
