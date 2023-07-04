# Control center for everything in Calendar Page
from Productivity.Calendar_Database import *
from Productivity.Planner_Database import *
from Productivity.Task_List_Database import *
from Productivity.Timeline_Database import *
from Productivity.To_Do_Lists import *


def process_result(result):
    if "object" in result.keys():
        if result["object"] == "error":
            print(f"ERROR: {result}")
    else:
        print(f"ERROR: {result}")


def update_timeline_from_calendar(IDS):
    calendar_pages = get_calendar_database_items_today(IDS)
    timeline_pages = get_timeline_database_items_today(IDS)
    if len(calendar_pages) == 0:
        print("no events today")
    else:
        for calendar_page in calendar_pages:
            exist = False
            for timeline_page in timeline_pages:
                if calendar_page.name == timeline_page.name and calendar_page.date == timeline_page.date:
                    exist = True
            if not exist:
                process_result(add_event_to_timeline_view(
                    {"Date": {"date": {"start": calendar_page.date[0], "end": calendar_page.date[1]}},
                     "Description": {"rich_text": calendar_page.description}, "Link": {"url": calendar_page.link},
                     "Name": {"title": [{"text": {"content": calendar_page.name}, "plain_text": calendar_page.name}]}},
                    IDS))
            if exist:
                print(f"{calendar_page.name} already exists")


def update_timeline_from_planner(IDS):
    planner_pages = get_planner_database_items_today(IDS)
    timeline_pages = get_timeline_database_items_today(IDS)
    print('test')
    if len(planner_pages) == 0:
        print("no events today")
    else:
        for planner_pages in planner_pages:
            exist = False
            for timeline_page in timeline_pages:
                if planner_pages.name == timeline_page.name and planner_pages.date == timeline_page.date:
                    exist = True
            if not exist:
                process_result(add_event_to_timeline_view(
                    {"Date": {"date": {"start": planner_pages.date[0], "end": planner_pages.date[1]}},
                     "Description": {"rich_text": planner_pages.description},
                     "Name": {"title": [{"text": {"content": planner_pages.name}, "plain_text": planner_pages.name}]}},
                    IDS))
            if exist:
                print(f"{planner_pages.name} already exists")


def sync_to_do_list_and_task_list(IDS):
    TOKEN = IDS["id"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    to_do_list = get_to_do_list(IDS)
    task_list = get_task_list(IDS)
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
                 "Name": {"title": [{"text": {"content": to_do_item}, "plain_text": to_do_item}]}}, IDS))
        else:
            if to_do_list_status[to_do_item] is True and \
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
                {"to_do": {"text": [{"text": {"content": task_item}, "plain_text": task_item}]}}, IDS))
        else:
            if task_list_status[task_item] == "Done 🙌" and to_do_list_status[task_item] is False:
                url = f"https://api.notion.com/v1/blocks/{to_do_list_id[task_item]}"
                response = requests.delete(url, headers=headers)
                process_result(add_event_to_to_do_list(
                    {"to_do": {"checked": True, "text": [{"text": {"content": task_item}, "plain_text": task_item}]}}, IDS))
    if temp_boolean:
        print("All items in task-list is in to-do list")


def daily_reset(IDS):
    TOKEN = IDS["id"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    to_do_list = get_to_do_list(IDS)
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
        task_list = get_task_list(IDS)
        for item in task_list:
            url = f"https://api.notion.com/v1/pages/{item.id}"
            response = requests.patch(url, json={"archived": True}, headers=headers)
            # print(response.text)
        to_do_list_tomorrow = get_to_do_list_tomorrow(IDS)
        if to_do_list_tomorrow.name[15:-2] == today:
            for event in to_do_list_tomorrow.to_do:
                process_result(add_event_to_to_do_list(
                    {"to_do": {"text": [{"text": {"content": event[0]}, "plain_text": event[0]}]}}, IDS))
        else:
            process_result(add_event_to_to_do_list({"to_do": {"text": []}}, IDS))
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
        process_result(add_event_to_to_do_list_tomorrow({"to_do": {"text": []}}, IDS))
        update_timeline_from_calendar(IDS)
        update_timeline_from_planner(IDS)
        sync_to_do_list_and_task_list(IDS)
