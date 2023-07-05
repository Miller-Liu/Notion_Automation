import datetime
import requests
import json


def get_upcoming_reminders(IDS):
    TOKEN, REMINDER_DATABASE_ID = IDS["id"], IDS["reminder_page"]["reminder-database"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    begin_date = datetime.datetime.today()
    day_after_begin_date = begin_date + datetime.timedelta(days=1)
    end_date = begin_date + datetime.timedelta(days=15)
    begin_date = begin_date.strftime('%Y-%m-%d')
    day_after_begin_date = day_after_begin_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    url = f"https://api.notion.com/v1/databases/{REMINDER_DATABASE_ID}/query"
    # print(begin_date, end_date)
    payload = {"filter": {"and": [{"property": "Date", "date": {"on_or_after": f"{begin_date}"}},
                                  {"property": "Date", "date": {"before": f"{end_date}"}}]},
               "sorts": [{"property": "Date", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    response = json.loads(response.text)
    pages = [[], [], []]
    for item in response["results"]:
        if len(item["properties"]["Name"]["title"]) == 1:
            if item["properties"]["Date"]["date"]["start"] == begin_date:
                pages[0].append(item["properties"]["Name"]["title"][0]["plain_text"])
            elif item["properties"]["Date"]["date"]["start"] == day_after_begin_date:
                pages[1].append(item["properties"]["Name"]["title"][0]["plain_text"])
            else:
                pages[2].append((item["properties"]["Name"]["title"][0]["plain_text"],
                                 item["properties"]["Date"]["date"]["start"]))
    return pages
