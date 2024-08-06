import requests
from ics import Calendar, Event
import os
import json


def read_database(database_id, token):
    """Given a database_id and the secret token it returns a json of the database"""
    headers = {
        'Authorization': 'Bearer ' + token,
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json',
    }
    read_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.request("POST", read_url, headers=headers)
    data = response.json()
    print(response.status_code)
    return data


class Project:
    """"""
    def __init__(self, event_id, name, date_start, date_end):
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        self.id = event_id
    url = str

    def save_to_calendar(self, calendar, filename='my.ics'):
        """The method saves the project on the given calendar as a new event with all_day property. Default filename
        is 'my.ics' """
        c = calendar
        e = Event()
        e.name = self.name
        e.begin = self.date_start
        e.end = self.date_end
        e.url = self.url
        e.make_all_day()
        c.events.add(e)
        with open(f'./{filename}', 'w') as my_file:
            my_file.writelines(c)


def create_calendar(data, save_to_json=False):
    """Given a json it iterates through the results, creates instances of the Project class, saves them as events in a
    ics calendar and returns a list of Projects. Optionally it saves the data in a json file"""
    project_list = []
    project_calendar = Calendar()
    for ev in data['results']:
        project = Project(
            event_id=ev['id'],
            name=ev['properties']['Name']['title'][0]['text']['content'],
            date_start=ev['properties']['Date']['date']['start'],
            date_end=ev['properties']['Date']['date']['end'],
        )
        project.url = ev['url']
        project_list.append(project)
        project.save_to_calendar(project_calendar, filename='geca_calendar.ics')
        # print(project_calendar.events)
    return project_list


data = read_database(database_id=os.environ.get("NOTION_DB_ID"), token=os.environ.get("NOTION_TOKEN"))
create_calendar(data)
