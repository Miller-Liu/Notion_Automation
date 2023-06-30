import datetime
import requests
import json


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
    TOKEN, CALENDAR_ID = IDS["id"], IDS["calendar_page"]["calendar_database"]
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
