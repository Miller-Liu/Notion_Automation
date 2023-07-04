from Home_Page.Home_Page import fun_home_page
from Productivity.Calendar_Page import *
import json

file = open("IDS.json")
data = json.load(file)

# fun_home_page(0, data)
# sync_google_calendar(data)
# process_result(add_event_to_to_do_list_tomorrow({"to_do": {"text": []}}, data))
# update_timeline_from_calendar(data)
# sync_to_do_list_and_task_list(data)
# print(get_planner_database_items_today(data))
update_timeline_from_planner(data)

# def controller():
#     controller_dict = {}