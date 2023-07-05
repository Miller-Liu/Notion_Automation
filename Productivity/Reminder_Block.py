import requests
import json


def change_reminder_block_content(IDS, event_data):
    TOKEN, REMINDER_BLOCK_ID = IDS["id"], IDS["calendar_page"]["reminder-block"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    if len(event_data[0]) != 0 and len(event_data[1]) != 0 and len(event_data[2]) != 0:
        text = "Reminders: "
        if len(event_data[0]) != 0:
            text += "\n\tToday:\t\t"
            for item in event_data[0]:
                text += f"{item}\t"
        if len(event_data[1]) != 0:
            text += "\n\tTomorrow:\t"
            for item in event_data[1]:
                text += f"{item}\t"
        if len(event_data[2]) != 0:
            text += "\n\tComing up:\t"
            for item in event_data[2]:
                text += f"{item[0]} on {item[1]}\t"
    else:
        text = "No Reminders :D"
    url = f"https://api.notion.com/v1/blocks/{REMINDER_BLOCK_ID}"
    payload = {"callout": {"text": [{"text": {"content": text}, "plain_text": text}]}}
    response = requests.patch(url, json=payload, headers=headers)
    response = json.loads(response.text)
    return response
