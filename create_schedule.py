from __future__ import print_function
import pickle
import os.path
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
CONNPASS = ['https://connpass.com/api/v1/event/?place=fukuoka']

def p(text):
  import pprint
  pprint.pprint(text)

def fetch_schedule():
  import requests
  response = requests.get("https://connpass.com/api/v1/event/?place=fukuoka")
  return response

def main():
  # """Shows basic usage of the Google Calendar API.
  # Prints the start and name of the next 10 events on the user's calendar.
  # """
  creds = None
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)

  service = build('calendar', 'v3', credentials=creds)
  now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

  response = fetch_schedule()
  text = json.loads(response.text)

  p(text)
  # p(text['event'])
  for event in text['events']:
    request_body = {
      'summary': event['title'],
      'location': event['address'],
      'description': event['description'],
      'start': {
        'dateTime': event['started_at'],
        'timeZone': 'Asia/Tokyo',
      },
      'end': {
        'dateTime': event['ended_at'],
        'timeZone': 'Asia/Tokyo',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10}
        ],
      },
    }
    event = service.events().insert(calendarId='primary', body=request_body).execute()


if __name__ == '__main__':
  main()