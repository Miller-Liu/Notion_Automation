# Notion App
import datetime
import json

import requests
import os
import sys
import time
import pyautogui
import keyboard
from google_calendar import get_google_calendar_events
from google_calendar import remove_token_file
from multiprocessing import Process
from multiprocessing import freeze_support
import multiprocessing

# For bundling with pyinstaller into an exe
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
path = os.path.abspath(os.path.join(bundle_dir, 'SECRET.json'))
file = open(path)

# When running on pycharm
# file = open("SECRET.json")

data = json.load(file)

# get values from SECRET.json
TOKEN = data["id"]
DATABASE_IDs = data["database"]
CALENDAR_ID = DATABASE_IDs["calendar"]
TIMELINE_ID = DATABASE_IDs["timeline"]
TO_DO_ID = DATABASE_IDs["to-do"]
TASK_LIST_ID = DATABASE_IDs["to-do-database"]
TO_DO_TOMORROW_ID = DATABASE_IDs["to-do-tomorrow"]
HOME_ID = DATABASE_IDs["Home"]
IMAGE_ID = DATABASE_IDs["Image"]

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
        return f"Name: {self.name}\nID: {self.id}\nDate: {self.date}\n" \
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


def process_result(result):
    if "object" in result.keys():
        if result["object"] == "error":
            print(f"ERROR: {result}")
    else:
        print(f"ERROR: {result}")


def get_database_object(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)
    return jsonify(response.text)


def get_calendar_database_items_today():
    url = f"https://api.notion.com/v1/databases/{CALENDAR_ID}/query"
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
    payload = {"filter": {"and": [{"property": "Date", "date": {"after": f"{begin_time}"}},
                                  {"property": "Date", "date": {"before": f"{end_time}"}}]},
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
            process_result(add_event_to_timeline_view(
                {"Date": {"date": {"start": calendar_page.date[0], "end": calendar_page.date[1]}},
                 "Description": {"rich_text": calendar_page.description}, "Link": {"url": calendar_page.link},
                 "Name": {"title": [{"text": {"content": calendar_page.name}, "plain_text": calendar_page.name}]}}))
        if exist:
            print(f"{calendar_page.name} already exists")


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


def get_to_do_list():
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}"
    response = requests.get(url, headers=headers)
    response = jsonify(response.text)
    to_do_list = ToDoList(response["heading_2"]["text"][0]["plain_text"], response["id"])
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}/children"
    response = requests.get(url, headers=headers)
    response = jsonify(response.text)
    to_do_list.process_from_database(response["results"])
    return to_do_list


def get_to_do_list_tomorrow():
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}"
    response = requests.get(url, headers=headers)
    response = jsonify(response.text)
    to_do_list = ToDoList(response["heading_2"]["text"][0]["plain_text"], response["id"])
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}/children"
    response = requests.get(url, headers=headers)
    response = jsonify(response.text)
    to_do_list.process_from_database(response["results"])
    return to_do_list


def add_to_do_list_to_timeline():
    to_do_list = get_to_do_list()
    timeline_pages = get_timeline_database_items_today()
    for to_do_item in to_do_list.to_do:
        exist = False
        for timeline_page in timeline_pages:
            if to_do_item[0] == timeline_page.name:
                exist = True
        if not exist:
            today = datetime.date.today()
            begin_time = datetime.time(0, 0, 0).strftime('%H:%M:%S')
            begin_time = f"{today.strftime('%Y-%m-%d')}T{begin_time}"
            begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
            end_time = datetime.time(23, 59, 59).strftime('%H:%M:%S')
            end_time = f"{today.strftime('%Y-%m-%d')}T{end_time}"
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S').astimezone().isoformat()
            process_result(add_event_to_timeline_view(
                {"Date": {"date": {"start": begin_time, "end": end_time}},
                 "Name": {"title": [{"text": {"content": to_do_item[0]}, "plain_text": to_do_item[0]}]}}))
        if exist:
            print(f"{to_do_item[0]} already exists")


class Task:
    def __init__(self, name, status, id):
        self.name = name
        self.status = status
        self.id = id

    def __str__(self):
        return f"Name: {self.name}\nStatus: {self.status}\n"


def get_task_list():
    url = f"https://api.notion.com/v1/databases/{TASK_LIST_ID}/query"
    response = requests.post(url, headers=headers)
    response = jsonify(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append(Task(item["properties"]["Name"]["title"][0]["plain_text"],
                              item["properties"]["Status"]["select"]["name"],
                              item["id"]))
    return pages


def add_event_to_task_list(event_data):
    url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": TASK_LIST_ID}, "properties": event_data}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    return response


def add_event_to_to_do_list(event_data):
    url = f"https://api.notion.com/v1/blocks/{TO_DO_ID}/children"
    payload = {"children": [event_data]}
    response = requests.patch(url, json=payload, headers=headers)
    response = jsonify(response.text)
    return response


def add_event_to_to_do_list_tomorrow(event_data):
    url = f"https://api.notion.com/v1/blocks/{TO_DO_TOMORROW_ID}/children"
    payload = {"children": [event_data]}
    response = requests.patch(url, json=payload, headers=headers)
    response = jsonify(response.text)
    return response


def sync_to_do_list_and_task_list():
    to_do_list = get_to_do_list()
    task_list = get_task_list()
    to_do_list_id = {to_do_list.to_do[i][0]: to_do_list.ids[i] for i in range(len(to_do_list.to_do))}
    to_do_list_status = {to_do_list.to_do[i][0]: to_do_list.to_do[i][1] for i in range(len(to_do_list.to_do))}
    to_do_list = [item[0] for item in to_do_list.to_do]
    task_list_id = {item.name: item.id for item in task_list}
    task_list_status = {item.name: item.status for item in task_list}
    task_list = [item.name for item in task_list]
    temp_boolean = True
    # print(to_do_list_id, to_do_list_status, task_list_id, task_list_status)
    for to_do_item in to_do_list:
        if to_do_item not in task_list:
            temp_boolean = False
            process_result(add_event_to_task_list(
                {"Status": {"select": {"name": "To Do"}},
                 "Name": {"title": [{"text": {"content": to_do_item}, "plain_text": to_do_item}]}}))
        else:
            if to_do_list_status[to_do_item] == True and \
                    (task_list_status[to_do_item] == "To Do" or task_list_status[to_do_item] == "Doing"):
                url = f"https://api.notion.com/v1/pages/{task_list_id[to_do_item]}"
                response = requests.patch(url, json={"properties": {"Status": {"select": {"name": "Done 🙌"}}}},
                                          headers=headers)
    if temp_boolean:
        print("All items in to-do list is in task list")
    temp_boolean = True
    for task_item in task_list:
        if task_item not in to_do_list:
            temp_boolean = False
            process_result(add_event_to_to_do_list(
                {"to_do": {"text": [{"text": {"content": task_item}, "plain_text": task_item}]}}))
        else:
            if task_list_status[task_item] == "Done 🙌" and to_do_list_status[task_item]== False:
                url = f"https://api.notion.com/v1/blocks/{to_do_list_id[task_item]}"
                response = requests.delete(url, headers=headers)
                process_result(add_event_to_to_do_list(
                    {"to_do": {"checked": True, "text": [{"text": {"content": task_item}, "plain_text": task_item}]}}))
    if temp_boolean:
        print("All items in task-list is in to-do list")


def daily_reset():
    to_do_list = get_to_do_list()
    today = datetime.date.today().strftime('%m/%d')
    if to_do_list.name[7:-2] == today:
        print("To do list is up to date")
    else:
        for item in to_do_list.ids:
            url = f"https://api.notion.com/v1/blocks/{item}"
            response = requests.delete(url, headers=headers)
            # print(response.text)
        url = f"https://api.notion.com/v1/blocks/{to_do_list.block_id}"
        response = requests.patch(url, json={"heading_2": {
            "rich_text": [{"text": {"content": f"To Do ({today}):"}, "plain_text": f"To Do ({today}):"}]}},
                                  headers=headers)
        # print(response.text)
        task_list = get_task_list()
        for item in task_list:
            url = f"https://api.notion.com/v1/pages/{item.id}"
            response = requests.patch(url, json={"archived": True}, headers=headers)
            # print(response.text)
        to_do_list_tomorrow = get_to_do_list_tomorrow()
        if to_do_list_tomorrow.name[15:-2] == today:
            for event in to_do_list_tomorrow.to_do:
                process_result(add_event_to_to_do_list(
                    {"to_do": {"text": [{"text": {"content": event[0]}, "plain_text": event[0]}]}}))
        else:
            process_result(add_event_to_to_do_list({"to_do": {"text": []}}))
        url = f"https://api.notion.com/v1/blocks/{to_do_list_tomorrow.block_id}"
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow = tomorrow.strftime('%m/%d')
        response = requests.patch(url, json={"heading_2": {
            "rich_text": [{"text": {"content": f"Planned To Do ({tomorrow}):"},
                           "plain_text": f"Planned To Do ({tomorrow}):"}]}}, headers=headers)
        # print(response.text)
        for item in to_do_list_tomorrow.ids:
            url = f"https://api.notion.com/v1/blocks/{item}"
            response = requests.delete(url, headers=headers)
            # print(response.text)
        process_result(add_event_to_to_do_list_tomorrow({"to_do": {"text": []}}))
        add_events_to_timeline_view()
        add_to_do_list_to_timeline()
        sync_to_do_list_and_task_list()


def sync_google_calendar():
    today = datetime.datetime.today()
    begin_date = today.replace(day=1)
    end_date = begin_date + datetime.timedelta(days=32)
    end_date = end_date.replace(day=1)
    begin_date = begin_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    url = f"https://api.notion.com/v1/databases/{CALENDAR_ID}/query"
    print(begin_date, end_date)
    payload = {"filter": {"and": [{"property": "Date", "date": {"on_or_after": f"{begin_date}"}},
                                  {"property": "Date", "date": {"before": f"{end_date}"}}]},
               "sorts": [{"property": "Time", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = jsonify(response.text)
    pages = []
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            pages.append((item["properties"]["Name"]["title"][0]["plain_text"],
                          item["properties"]["Time"]["date"]["start"][:10]))
    print(pages)
    calendar = get_google_calendar_events()
    for calendar_event in calendar:
        temp = True
        for event in pages:
            if calendar_event[0] == event[0] and calendar_event[1][:10] == calendar_event[2][:10] == event[1]:
                temp = False
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
            response = jsonify(response.text)
    return response


def fun_home_page(last_time):
    now = datetime.datetime.now().time()
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    url_list = [["https://s3.us-west-2.amazonaws.com/secure.notion-static.com/26e9a635-1a71-44e0-a8a3-5f4cbebcd305/1-1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193420Z&X-Amz-Expires=3600&X-Amz-Signature=2cb561e94b5519d70ef3219de7ed8c29856ee165a9dac3be66c430579e77a78d&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/095c13ed-2786-46c5-aab0-1916ae90cb62/3-2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T192932Z&X-Amz-Expires=3600&X-Amz-Signature=ba72f6e1659b5cc50e148a837a5aa901fe713848d388eb619fc7516b14c16350&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/1faa89b9-98a1-4320-8c7a-7613d82959c1/1-3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193455Z&X-Amz-Expires=3600&X-Amz-Signature=5c86687a84304253fa76764117130bf7b33aeea9b7f25ba5d2da75cb49b97c4b&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/6855024a-e092-4c83-82c5-38a230016cb5/1-4.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193537Z&X-Amz-Expires=3600&X-Amz-Signature=46b8342c92f14f621abaa54392ae9555861bdffdb2347f3df784c31c87d4cb5e&X-Amz-SignedHeaders=host&x-id=GetObject"],
                ["https://s3.us-west-2.amazonaws.com/secure.notion-static.com/902caecb-6175-4869-907c-aa7093fc1ca4/2-1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193656Z&X-Amz-Expires=3600&X-Amz-Signature=71c7ded9bb342c63fab32c559a877beff29357c7d1c11309a88c207814033e1e&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/8c810358-78a4-4024-b7d5-0dbfdbf60e64/2-2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193934Z&X-Amz-Expires=3600&X-Amz-Signature=5a144ea01ca3e4cc130733c8f5d67d37e6d578420c366734e100565f826dde9c&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7fb9b891-9422-46c4-aac1-9815034568fc/2-3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193951Z&X-Amz-Expires=3600&X-Amz-Signature=c167bf7ca9ca4d21e739f290217599f72cbdf0717a3aff32dcdaf6dd54ac78f1&X-Amz-SignedHeaders=host&x-id=GetObject",
                 "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/ca9cbcc3-6665-4218-948b-133834dfe6fd/2-4.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T194016Z&X-Amz-Expires=3600&X-Amz-Signature=e6738d218339f6eaa444d5bf8543390e7135e819ed7dba17e13464a10fe39e51&X-Amz-SignedHeaders=host&x-id=GetObject"]]
    url = f"https://api.notion.com/v1/pages/{HOME_ID}"
    block_url = f"https://api.notion.com/v1/blocks/{IMAGE_ID}"
    block_url_list = ["https://s3.us-west-2.amazonaws.com/secure.notion-static.com/f1cb7ecd-9405-4e66-8772-51802d2823d2/1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220535Z&X-Amz-Expires=3600&X-Amz-Signature=e5198c47e5bb3b741161ae20c885e319422a04900bb973563fabc53054ba118a&X-Amz-SignedHeaders=host&x-id=GetObject",
                      "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7d960cca-6136-48c0-9e04-b8a0f69be048/2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220604Z&X-Amz-Expires=3600&X-Amz-Signature=a599f15b17b1215f5da8d59d542ec606714c713bac575a9598cc12d42d3154c8&X-Amz-SignedHeaders=host&x-id=GetObject",
                      "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/e809329e-30c8-4554-9512-ad5b6862e6d6/3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220650Z&X-Amz-Expires=3600&X-Amz-Signature=468e5fe9f7759053bc14fae9b748a82d1f664826a65e94293073b88c790b71ed&X-Amz-SignedHeaders=host&x-id=GetObject"]
    if datetime.time(hour=5) <= now <= datetime.time(hour=9, minute=30) and last_time != 0:
        payload = {"cover": {"external": {"url": url_list[day_of_year % 2][0]}}}
        response = requests.patch(url=url, json=payload, headers=headers)
        block_payload = {"image": {"external": {"url": block_url_list[0]}}}
        block_response = requests.patch(url=block_url, json=block_payload, headers=headers)
        return 0
    elif datetime.time(hour=9, minute=30) <= now <= datetime.time(hour=13, minute=5) and last_time != 1:
        payload = {"cover": {"external": {"url": url_list[day_of_year % 2][1]}}}
        response = requests.patch(url=url, json=payload, headers=headers)
        block_payload = {"image": {"external": {"url": block_url_list[1]}}}
        block_response = requests.patch(url=block_url, json=block_payload, headers=headers)
        return 1
    elif datetime.time(hour=13, minute=5) <= now <= datetime.time(hour=19) and last_time != 2:
        payload = {"cover": {"external": {"url": url_list[day_of_year % 2][2]}}}
        response = requests.patch(url=url, json=payload, headers=headers)
        block_payload = {"image": {"external": {"url": block_url_list[1]}}}
        block_response = requests.patch(url=block_url, json=block_payload, headers=headers)
        return 2
    elif datetime.time(hour=19) <= now or now <= datetime.time(hour=5) and last_time != 3:
        payload = {"cover": {"external": {"url": url_list[day_of_year % 2][3]}}}
        response = requests.patch(url=url, json=payload, headers=headers)
        block_payload = {"image": {"external": {"url": block_url_list[2]}}}
        block_response = requests.patch(url=block_url, json=block_payload, headers=headers)
        return 3
    return last_time


def run_periodically(global_var, last_time):
    while True:
        if global_var.value:
            last_time = fun_home_page(last_time)
        time.sleep(60)


def switch_periodic_function(global_var):
    global_var.value = not global_var.value


def specific_functions():
    specific_functions_dict = {"1": add_events_to_timeline_view, "2": sync_to_do_list_and_task_list,
                               "3": add_to_do_list_to_timeline}
    print(
        f'''
Below are the specific functions available to execute:
    Add calendar events to timeline view: 1
    Sync to do list and to do database: 2
    Add to do list items to timeline view: 3
        '''
    )
    specific_functions_choice = input("Please enter your choice: ")
    if specific_functions_choice in specific_functions_dict.keys():
        win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
        win.minimize()
        specific_functions_dict[specific_functions_choice]()
    else:
        if specific_functions_choice != "q":
            print("Invalid entry")
            specific_functions()


def bug_fix():
    remove_token_file()
    get_google_calendar_events()


def controller(global_var):
    controller_dict = {"1": sync_google_calendar, "2": daily_reset, "3": specific_functions,
                       "4": switch_periodic_function, "5": bug_fix}
    print(
        f'''
Below are the shortcuts corresponding with each action:
    Sync google calendar with calendar view: 1
    Daily update: 2
    Specific functions: 3
    Switch periodic functions to {not global_var.value}: 4
    Fix if #1 doesn't work: 5
        '''
    )
    sys.stdin = open(0)
    choice = input("Please enter your choice: ")
    if choice in controller_dict.keys():
        if choice != "3":
            win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
            win.minimize()
        if choice == "4":
            controller_dict[choice](global_var)
        else:
            controller_dict[choice]()
    else:
        if choice != "q":
            print("Invalid entry")
            controller(global_var)


def activated(global_var):
    win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
    win.maximize()
    controller(global_var)
    print("finished")
    win.maximize()
    time.sleep(3)
    win.minimize()


def wait_for_hotkey(global_var):
    win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
    win.maximize()
    win.minimize()
    keyboard.add_hotkey("ctrl+shift+alt+space", activated, args=(global_var,))
    keyboard.wait()


if __name__ == '__main__':
    freeze_support()
    variable = multiprocessing.Value("i", True)
    p1 = Process(target=wait_for_hotkey, args=(variable,))
    p1.start()
    p2 = Process(target=run_periodically, args=(variable, 0,))
    p2.start()
    p1.join()
    p2.join()

# url = f"https://api.notion.com/v1/blocks/{IMAGE_ID}"
# response = requests.get(url, headers=headers)
# print(response.text)

