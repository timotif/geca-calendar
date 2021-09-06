from flask import Flask, render_template, send_file
from notion_interface import read_database, create_calendar
import os

# TODO Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# TODO token, db_id, endpoint url, headers
token = os.environ.get("NOTION_TOKEN")
database_id = os.environ.get("NOTION_DB_ID")
get_url = 'https://api.notion.com/v1/databases/'


# TODO Basic app.route

@app.route('/')
def get_events():
    data = read_database(database_id, token)
    projects = create_calendar(data)
    return render_template('index.html', projects=projects)


@app.route('/download/<path:filename>')
def download_calendar(filename):
    return send_file(filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
