# All things related to the google calendar api
from __future__ import print_function

import datetime
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
token_path = os.path.abspath(os.path.join(bundle_dir, 'token.json'))
credentials_path = os.path.abspath(os.path.join(bundle_dir, 'credentials.json'))


def get_google_calendar_events(IDS):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds, static_discovery=False)
        api = IDS["google_api"]
        # get list of calendars
        '''
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list['items']:
            print("calendar", calendar_list_entry['summary'], calendar_list_entry['id'])
        '''
        today = datetime.datetime.today()
        begin_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = begin_date + datetime.timedelta(days=32)
        end_date = end_date.replace(day=1).astimezone().isoformat()
        begin_date = begin_date.astimezone().isoformat()
        events = []
        events_result = service.events().list(key=api, calendarId="millerliu.work@gmail.com", orderBy='startTime',
                                              timeMin=begin_date, timeMax=end_date, singleEvents=True).execute()
        for event in events_result["items"]:
            # print(event["summary"], event["start"]["dateTime"], event["end"]["dateTime"])
            events.append([event["summary"], event["start"]["dateTime"], event["end"]["dateTime"], "Default"])
        events_result = service.events().list(key=api,
                                              calendarId="19e9be64fcf30188881eee3c1fd85a06ee0659abd6e635f22ca59af229c6206e@group.calendar.google.com",
                                              orderBy='startTime',
                                              timeMin=begin_date, timeMax=end_date, singleEvents=True).execute()
        for event in events_result["items"]:
            events.append([event["summary"], event["start"]["dateTime"], event["end"]["dateTime"], "School"])
        events_result = service.events().list(key=api,
                                              calendarId="1db81f0fd638de399817ca155442e68066cd6119b16ddb4397e243bb3056e975@group.calendar.google.com",
                                              orderBy='startTime', timeMin=begin_date, timeMax=end_date,
                                              singleEvents=True).execute()
        for event in events_result["items"]:
            events.append([event["summary"], event["start"]["dateTime"], event["end"]["dateTime"], "Clubs"])
        events_result = service.events().list(key=api, calendarId="en.usa#holiday@group.v.calendar.google.com",
                                              orderBy='startTime',
                                              timeMin=begin_date, timeMax=end_date, singleEvents=True).execute()
        for event in events_result["items"]:
            events.append([event["summary"], "Holiday"])
        return events
    except HttpError as error:
        print('An error occurred: %s' % error)


def remove_token_file():
    if os.path.exists(token_path):
        os.remove(token_path)