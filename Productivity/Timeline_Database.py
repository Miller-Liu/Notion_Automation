import datetime
import json
import requests


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


def get_timeline_database_items_today(IDS):
    TOKEN, TIMELINE_ID = IDS["id"], IDS["task_list_page"]["timeline-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/databases/{TIMELINE_ID}/query"
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    zero_time = datetime.time(0, 0, 0).strftime('%H:%M:%S')
    begin_time = f"{today.strftime('%Y-%m-%d')}T{zero_time}"
    begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
    end_time = f"{tomorrow.strftime('%Y-%m-%d')}T{zero_time}"
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
    payload = {"filter": {"and": [{"property": "Date", "date": {"after": f"{begin_time}"}},
                                  {"property": "Date", "date": {"before": f"{end_time}"}}]},
               "sorts": [{"property": "Date", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(TimelineDatabasePage(item["properties"]["Name"]["title"][0]["plain_text"], item["id"]))
            pages[-1].process_from_database(item["properties"])
    return pages


def add_event_to_timeline_view(event_data, IDS):
    TOKEN, TIMELINE_ID = IDS["id"], IDS["task_list_page"]["timeline-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": TIMELINE_ID}, "properties": event_data}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    return response
