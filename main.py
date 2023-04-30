# Notion App
import datetime
import json
import requests

file = open('SECRET.json')
data = json.load(file)

# get values from SECRET.json
TOKEN = data["id"]
DATABASE_IDs = data["database"]
Calendar_ID = DATABASE_IDs["calendar"]
# print(data)

file.close()

# Headers
headers = {
    'Authorization': f'Bearer {TOKEN}',
    "accept": "application/json",
    'Content-Type': 'application/json',
    'Notion-Version': '2021-08-16'
}


# def create_page(data: dict):
#     create_url = "https://api.notion.com/v1/pages"
#
#     payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}
#
#     res = requests.post(create_url, headers=headers, json=payload)
#     # print(res.status_code)
#     return res


class DatabasePage:
    def __init__(self, name):
        self.name = name
        self.status = ""
        self.date = ""
        self.description = ""

    def process_from_database(self, page_properties):
        self.status = page_properties["Status"]["status"]["name"]
        self.description = page_properties["Description"]["rich_text"]
        start_time = datetime.datetime.fromisoformat(page_properties["Time"]["date"]["start"])
        end_time = datetime.datetime.fromisoformat(page_properties["Time"]["date"]["end"])
        self.date = (
            (start_time.hour, start_time.minute), (end_time.hour, end_time.minute),
            start_time.day, start_time.month, start_time.year)

    def __str__(self):
        return f"Name: {self.name}\nStatus: {self.status}\nDate: {self.date}\nDescription: {self.description}\n"


def jsonify(text):
    return json.loads(text)


def get_database_object(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)
    return jsonify(response.text)


def get_database_items_today():
    url = f"https://api.notion.com/v1/databases/{Calendar_ID}/query"
    payload = {"filter": {"property": "Date", "date": {"equals": f"{datetime.date.today()}"}},
               "sorts": [{"property": "Time", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(DatabasePage(item["properties"]["Name"]["title"][0]["plain_text"]))
            pages[-1].process_from_database(item["properties"])
    for page in pages:
        print(page)
    return response


json_object = json.dumps(get_database_items_today(), indent=4)

# Writing to sample.json
with open("Out.json", "w") as outfile:
    outfile.write(json_object)
