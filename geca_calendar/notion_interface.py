import requests
from ics import Calendar, Event
import json
from logging_config import logger
import os

TOKEN = os.getenv('NOTION_TOKEN')
HEADERS = {
    'Authorization': 'Bearer ' + TOKEN,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
}

def read_database(database_id, token):
    """Given a database_id and the secret token it returns a json of the database"""
    logger.info("Fetching data")
    read_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.request("POST", read_url, headers=HEADERS)
    data = response.json()
    logger.debug(f"Status code: {response.status_code}")
    return data

def fetch_seating_blocks(data: json) -> dict:
    """It returns repertoire->page_id pairs from the data"""
    seating_blocks = {}
    for i in range(len(data['results'])):
        if data['results'][i]['type'] == 'paragraph' and \
            len(data['results'][i]['paragraph']['text']) != 0 and \
            data['results'][i]['paragraph']['text'][0]['plain_text'].lower() == "seating positions":
            # Seating is set up
            i += 1
            # Going until the divider to fetch page ids
            while (i < len(data['results']) and data['results'][i]['type'] != 'divider'):
                key = data['results'][i]['child_page']['title']
                value = data['results'][i]['id']
                seating_blocks[key] = value
                i += 1
            break
    return seating_blocks

def fetch_seating_order(seating_blocks: dict, data: json) -> str:
    """Appends to a string the seating order of each page"""
    seating_parsed = ""
    for key, value in seating_blocks.items():
        # Searching in each seating page
        page_id = value
        response = requests.request("GET", f"https://api.notion.com/v1/blocks/{page_id}/children", headers=HEADERS)
        data = response.json()
        seating = ""
        for i in range(len(data['results'])):
            # Searching the blocks of the seating page
            block = data['results'][i]
            type = block['type']
            if type == 'heading_3': # Section name
                seating += block[type]['text'][0]['plain_text'] + ":\n"
            elif block['type'] == 'paragraph' and len(block['paragraph']['text']) != 0:
                seating += block['paragraph']['text'][0]['plain_text'] + "\n" # Section list
        seating_parsed += f"{key}\n{seating}\n"
    return seating_parsed
    
def get_seating_positions(page_id: str, token: str) -> str:
    # Checking a project page
    endpoint = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.request("GET", endpoint, headers=HEADERS)
    data = response.json()
    logger.debug(f"Status code: {response.status_code}")
    seating_blocks = fetch_seating_blocks(data) # repertoire->page_id pairs
    return fetch_seating_order(seating_blocks, data)
    
class Project:
    """"""
    def __init__(self, event_id, name, date_start, date_end):
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        self.id = event_id
    url = str
    seating = str

    def save_to_calendar(self, calendar, filename='my.ics'):
        """The method saves the project on the given calendar as a new event with all_day property. Default filename
        is 'my.ics' """
        c = calendar
        e = Event()
        e.name = self.name
        e.begin = self.date_start
        e.end = self.date_end
        e.url = self.url
        e.description = str(self.seating)
        e.make_all_day()
        c.events.add(e)
        with open(f'./{filename}', 'w') as my_file:
            my_file.writelines(c)


def create_calendar(data, filename='geca_calendar.ics' , save_to_json=False):
    """Given a json and a filename it iterates through the results, creates instances of the Project class, saves them as events in a
    ics calendar and returns a list of Projects. Default filename is geca_calendar.ics. Optionally it saves the data in a json file"""
    project_list = []
    project_calendar = Calendar()
    for ev in data['results']:
        project = Project(
            event_id=ev['id'],
            name=ev['properties']['Name']['title'][0]['text']['content'],
            date_start=ev['properties']['Date']['date']['start'],
            date_end=ev['properties']['Date']['date']['end'],
        )
        try:
            project.seating = get_seating_positions(ev['id'], os.getenv('NOTION_TOKEN'))
        except Exception as e:
            logger.error(f"Error fetching seating positions: {e}")
        project.url = ev['url']
        project_list.append(project)
        project.save_to_calendar(project_calendar, filename=filename)
    if save_to_json:
        save_json(data, name='geca_calendar.json')
    return project_list


def save_json(data, path='./', name='db.json'):
    logger.info("Saving json")
    with open(path + name, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)