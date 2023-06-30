# Control center for everything in Calendar Page
from Productivity.Calendar_Database import *
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