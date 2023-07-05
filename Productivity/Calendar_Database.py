# Functions related to the calendar database in the calendar page
import requests
import json
from Productivity.Google_Calendar import *


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
        return f"Name: {self.name}\nID: {self.id}\nDate: {self.date}\n" \
               f"Description: {self.description}\nLink: {self.link}\n"


def get_calendar_database_items_today(IDS):
    TOKEN, CALENDAR_ID = IDS["id"], IDS["calendar_page"]["calendar-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/databases/{CALENDAR_ID}/query"
    payload = {"filter": {"property": "Date", "date": {"equals": f"{datetime.date.today()}"}},
               "sorts": [{"property": "Time", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(CalendarDatabasePage(item["properties"]["Name"]["title"][0]["plain_text"], item["id"]))
            pages[-1].process_from_database(item["properties"])
    return pages


def sync_google_calendar(IDS):
    TOKEN, CALENDAR_ID = IDS["id"], IDS["calendar_page"]["calendar-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    today = datetime.datetime.today()
    begin_date = today.replace(day=1)
    end_date = begin_date + datetime.timedelta(days=32)
    end_date = end_date.replace(day=1)
    begin_date = begin_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    url = f"https://api.notion.com/v1/databases/{CALENDAR_ID}/query"
    # print(begin_date, end_date)
    payload = {"filter": {"and": [{"property": "Date", "date": {"on_or_after": f"{begin_date}"}},
                                  {"property": "Date", "date": {"before": f"{end_date}"}}]},
               "sorts": [{"property": "Time", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append((item["properties"]["Name"]["title"][0]["plain_text"],
                          item["properties"]["Time"]["date"]["start"][:10]))
    # print(pages)
    calendar = get_google_calendar_events(IDS)
    holiday = []
    for calendar_event in calendar:
        if calendar_event[-1] != "Holiday":
            temp = True
            # print(calendar_event)
            for event in pages:
                if calendar_event[0] == event[0] and calendar_event[1][:10] == calendar_event[2][:10] == event[1]:
                    temp = False
                    break
            if not temp:
                print(f"{calendar_event[0]} is already in calendar")
            else:
                print(f"{calendar_event[0]} added to calendar")
                url = "https://api.notion.com/v1/pages"
                payload = {"parent": {"database_id": CALENDAR_ID},
                           "properties": {"Date": {"date": {"start": calendar_event[1][:10]}},
                                          "Time": {"date": {"start": calendar_event[1],
                                                            "end": calendar_event[2]}}, "Name": {
                                   "title": [{"text": {"content": calendar_event[0]}, "plain_text": calendar_event[0]}]}}}
                response = requests.post(url, json=payload, headers=headers)
                response = json.loads(response.text)
        if calendar_event[-1] == "Holiday":
            holiday.append(calendar_event)
    return holiday


def bug_fix(IDS):
    remove_token_file()
    get_google_calendar_events(IDS)
