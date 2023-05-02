# Notion App
import datetime
import json
import requests
import pytz
import time
import os
import sys

# For bundling with pyinstaller into an exe
# bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
# path = os.path.abspath(os.path.join(bundle_dir, 'SECRET.json'))
# print(path)
# file = open(path)

# When running on pycharm: file = open("SECRET.json")
file = open("SECRET.json")
data = json.load(file)

# get values from SECRET.json
TOKEN = data["id"]
DATABASE_IDs = data["database"]
Calendar_ID = DATABASE_IDs["calendar"]
TIMELINE_ID = DATABASE_IDs["timeline"]
# print(data)

file.close()

# Headers
headers = {
    'Authorization': f'Bearer {TOKEN}',
    "accept": "application/json",
    'Content-Type': 'application/json',
    'Notion-Version': '2021-08-16'
}


class CalendarDatabasePage:
    def __init__(self, name, page_id):
        self.name = name
        self.id = page_id
        self.date = ""
        self.description = ""
        self.link = ""

    def process_from_database(self, page_properties):
        self.description = page_properties["Description"]["rich_text"]
        self.date = (page_properties["Time"]["date"]["start"], page_properties["Time"]["date"]["end"])
        self.link = page_properties["Link"]["url"]

    def __str__(self):
        return f"Name: {self.name}\nID: {self.id}]nDate: {self.date}\n" \
               f"Description: {self.description}\nLink: {self.link}\n"


class TimelineDatabasePage:
    def __init__(self, name, page_id):
        self.name = name
        self.id = page_id
        self.status = ""
        self.date = ""
        self.description = ""
        self.link = ""

    def process_from_database(self, page_properties):
        self.status = page_properties["Status"]["status"]["name"]
        self.description = page_properties["Description"]["rich_text"]
        self.date = (page_properties["Date"]["date"]["start"], page_properties["Date"]["date"]["end"])
        self.link = page_properties["Link"]["url"]

    def __str__(self):
        return f"Name: {self.name}\nID: {self.id}\nStatus: {self.status}\n" \
               f"Date: {self.date}\nDescription: {self.description}\nLink: {self.link}\n"


def jsonify(text):
    return json.loads(text)


def get_database_object(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)
    return jsonify(response.text)


def get_calendar_database_items_today():
    url = f"https://api.notion.com/v1/databases/{Calendar_ID}/query"
    payload = {"filter": {"property": "Date", "date": {"equals": f"{datetime.date.today()}"}},
               "sorts": [{"property": "Time", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(CalendarDatabasePage(item["properties"]["Name"]["title"][0]["plain_text"], item["id"]))
            pages[-1].process_from_database(item["properties"])
    return pages


def get_timeline_database_items_today():
    url = f"https://api.notion.com/v1/databases/{TIMELINE_ID}/query"
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    zero_time = datetime.time(0, 0, 0).strftime('%H:%M:%S')
    begin_time = f"{today.strftime('%Y-%m-%d')}T{zero_time}"
    begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
    end_time = f"{tomorrow.strftime('%Y-%m-%d')}T{zero_time}"
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
    payload = {"filter": {"property": "Date", "date": {"after": f"{begin_time}", "before": f"{end_time}"}},
               "sorts": [{"property": "Date", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(TimelineDatabasePage(item["properties"]["Name"]["title"][0]["plain_text"], item["id"]))
            pages[-1].process_from_database(item["properties"])
    return pages


def add_event_to_timeline_view(event_data):
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": TIMELINE_ID}, "properties": event_data}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    return response


def add_events_to_timeline_view():
    calendar_pages = get_calendar_database_items_today()
    timeline_pages = get_timeline_database_items_today()
    for calendar_page in calendar_pages:
        exist = False
        for timeline_page in timeline_pages:
            if calendar_page.name == timeline_page.name and calendar_page.date == timeline_page.date:
                exist = True
        if not exist:
            print(add_event_to_timeline_view({"Date": {"date": {"start": calendar_page.date[0], "end": calendar_page.date[1]}}, "Description": {"rich_text": calendar_page.description}, "Link": {"url": calendar_page.link}, "Name": {"title": [{"text": {"content": calendar_page.name}, "plain_text": calendar_page.name}]}}))
        if exist:
            print(f"{calendar_page.name} already exists")



# json_object = json.dumps(get_timeline_database_items_today(), indent=4)

# # Writing to sample.json
# with open("Out.json", "w") as outfile:
#     outfile.write(json_object)


# TZ_LA = pytz.timezone('America/Los_Angeles')
# a = datetime.datetime.now(TZ_LA)
# print(a)
# print(add_event_to_timeline_view({"Date": {"date": {"start": a.isoformat(), "end": None}}}))

add_events_to_timeline_view()

# input()
