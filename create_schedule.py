from __future__ import print_function
import pickle
import os.path
import datetime
import pprint
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
CONNPASS = "https://connpass.com/api/v1/event/?event_type=participation&keyword=福岡市"

# 福岡の参加型イベントで一月以内のものを検索

def p(text):
  pprint.pprint(text)

def fetch_conpass_events():
  response = requests.get(CONNPASS)
  return response

def credential():
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
  return service
  
def fetch_google_calender(started_at, ended_at):
    service = credential()
    # 期間内の予定を取得する
    events_result = service.events().list(calendarId='primary', 
                                        timeMin=started_at,
                                        timeMax=ended_at,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    schedules_in_calender = events_result.get('items', [])
    return schedules_in_calender

def main():
  started_at = 0
  ended_at = 0
  now = datetime.datetime.utcnow()
  if not started_at:
    started_at = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
  if not ended_at:
    ended_at = now + datetime.timedelta(weeks=4)
    ended_at = ended_at.isoformat() + 'Z' # 'Z' indicates UTC time

  schedules_in_calender = fetch_google_calender(started_at, ended_at)

  response = fetch_conpass_events()
  next_events = json.loads(response.text)
 
  service = credential()

  for event in next_events['events']:
    double_booking = False
    for schedule in schedules_in_calender:
      schedule_start = schedule['start'].get('dateTime', schedule['start'].get('dateTime')) 
      if not schedule_start:
        continue
      schedule_start = datetime.datetime.strptime( schedule_start, '%Y-%m-%dT%H:%M:%S%z')
      event_start = datetime.datetime.strptime(event['started_at'], '%Y-%m-%dT%H:%M:%S%z')
      if schedule_start > event_start:
        break

      if schedule_start == event_start and schedule['summary'] == event['title']:
        double_booking = True
        break

    if double_booking:
      print('---------------------------------')
      print('同一の予定があるためイベントは登録しませんでした')
      print( event['started_at'] ,':', event['title'])
      continue
    
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