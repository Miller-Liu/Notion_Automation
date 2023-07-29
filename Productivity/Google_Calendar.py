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


def get_google_calendar_events(IDS, month_from_now):
    creds = None
    error_occured = False
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as ex:
                print(f"An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args}")
                error_occured = True
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    if not error_occured:
        try:
            service = build('calendar', 'v3', credentials=creds, static_discovery=False)
            api = IDS["google_api"]
            # get list of calendars
            today = datetime.datetime.today()
            begin_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for i in range(month_from_now):
                begin_date = begin_date + datetime.timedelta(days=32)
                begin_date = begin_date.replace(days=1)
            end_date = begin_date + datetime.timedelta(days=32)
            end_date = end_date.replace(day=1).astimezone().isoformat()
            begin_date = begin_date.astimezone().isoformat()

            events = []
            calendar_list = service.calendarList().list().execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] in \
                        ['millerliu.work@gmail.com', 'Berkeley']:
                    events_result = service.events().list(key=api,
                                                          calendarId=calendar_list_entry['id'],
                                                          orderBy='startTime',
                                                          timeMin=begin_date, timeMax=end_date,
                                                          singleEvents=True).execute()
                    for event in events_result["items"]:
                        events.append(
                            [event["summary"], event["start"]["dateTime"], event["end"]["dateTime"],
                             calendar_list_entry['summary']])
            events_result = service.events().list(key=api, calendarId="en.usa#holiday@group.v.calendar.google.com",
                                                  orderBy='startTime',
                                                  timeMin=begin_date, timeMax=end_date, singleEvents=True).execute()
            for event in events_result["items"]:
                events.append([event["summary"], "Holiday"])
            return events
        except HttpError as error:
            print('An error occurred: %s' % error)
    else:
        remove_token_file()
        get_google_calendar_events(IDS, month_from_now)


def remove_token_file():
    if os.path.exists(token_path):
        os.remove(token_path)
