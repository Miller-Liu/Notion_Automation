import requests
import json


class ToDoList:
    def __init__(self, name, block_id):
        self.name = name
        self.to_do = []
        self.ids = []
        self.block_id = block_id

    def process_from_database(self, page_properties):
        for item in page_properties:
            if len(item["to_do"]["text"]) == 1:
                self.to_do.append([item["to_do"]["text"][0]["plain_text"], item["to_do"]["checked"]])
                self.ids.append(item["id"])

    def __str__(self):
        return f"Name: {self.name}\nTo-do: {self.to_do}\nIDs: {self.ids}\n"


def get_to_do_list(IDS):
    TOKEN, TO_DO_ID = IDS["id"], IDS["calendar_page"]["to-do"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}"
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    to_do_list = ToDoList(response["heading_2"]["text"][0]["plain_text"], response["id"])
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}/children"
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    to_do_list.process_from_database(response["results"])
    return to_do_list


def get_to_do_list_tomorrow(IDS):
    TOKEN, TO_DO_TOMORROW_ID = IDS["id"], IDS["calendar_page"]["to-do-tomorrow"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}"
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    to_do_list = ToDoList(response["heading_2"]["text"][0]["plain_text"], response["id"])
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}/children"
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    to_do_list.process_from_database(response["results"])
    return to_do_list


def add_event_to_to_do_list(event_data, IDS):
    TOKEN, TO_DO_ID = IDS["id"], IDS["calendar_page"]["to-do"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}/children"
    payload = {"children": [event_data]}
    response = requests.patch(url, json=payload, headers=headers)
    response = json.loads(response.text)
    return response


def add_event_to_to_do_list_tomorrow(event_data, IDS):
    TOKEN, TO_DO_TOMORROW_ID = IDS["id"], IDS["calendar_page"]["to-do-tomorrow"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}/children"
    payload = {"children": [event_data]}
    response = requests.patch(url, json=payload, headers=headers)
    response = json.loads(response.text)
    return response

