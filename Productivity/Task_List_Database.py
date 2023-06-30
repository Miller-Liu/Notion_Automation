import requests
import json


class Task:
    def __init__(self, name, status, id):
        self.name = name
        self.status = status
        self.id = id

    def __str__(self):
        return f"Name: {self.name}\nStatus: {self.status}\n"


def get_task_list(IDS):
    TOKEN, TASK_LIST_ID = IDS["id"], IDS["task_list_page"]["to-do-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/databases/{TASK_LIST_ID}/query"
    response = requests.post(url, headers=headers)
    response = json.loads(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(Task(item["properties"]["Name"]["title"][0]["plain_text"],
                              item["properties"]["Status"]["select"]["name"],
                              item["id"]))
    return pages


def add_event_to_task_list(event_data, IDS):
    TOKEN, TASK_LIST_ID = IDS["id"], IDS["task_list_page"]["to-do-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": TASK_LIST_ID}, "properties": event_data}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    return response