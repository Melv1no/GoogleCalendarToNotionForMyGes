import datetime
import json
import time
import dotenv
import requests

from cal_setup import get_calendar_service

database_id = dotenv.get_key(".env","DATABASE_ID")
calendar_id = dotenv.get_key(".env", "CALENDAR_ID")
notion_token = dotenv.get_key(".env", "NOTION_TOKEN")

def main():
   service = get_calendar_service()
   now = datetime.datetime.utcnow().isoformat() + 'Z'
   events_result = service.events().list(
       calendarId=calendar_id, timeMin=now,
       maxResults=100, singleEvents=True,
       orderBy='startTime').execute()
   events = events_result.get('items', [])

   if not events:
       print('No upcoming events found.')
   for event in events:
       start = event['start'].get('dateTime', event['start'].get('date'))
       print("[+] "+event['summary'])
       time.sleep(1)
       if not "description" in event:
           event['description'] = "no more info"
       if NotionEventExist(start,event['summary']) == True:
          createNotionEvent(start ,event['summary'], event['description'])


def createNotionEvent(date,title, description):
  url = f'https://api.notion.com/v1/pages'
  payload = {
    "parent": {
      "database_id": database_id
    },
    "properties": {
      "Date" : {
          "type" : "date",
          "date" : {
             "start": date
          }
      },
      "title": {
        "title": [
          {
            "text": {
              "content": title
            }
          }
        ]
      },
      "info": {
        "rich_text": [
          {
            "text": {
              "content": description
            }
          }
        ]
      },
    }
  }

  r = requests.post(url, headers={
    "Authorization": f"Bearer "+ notion_token,
    "Notion-Version": "2021-08-16",
    "Content-Type": "application/json"
  }, data=json.dumps(payload))


def NotionEventExist(date,title):
    url = "https://api.notion.com/v1/databases/"+database_id+"/query"


    payload = {
        "filter":{
            "and":[
                {
                "property" : "title",
                "text":{
                    "equals": title
                }
                },
                {
                "property" : "Date",
                "date":{
                    "equals":date
                }
                }
            ]
        }

    }

    r = requests.post(url, headers={
        "Authorization": f"Bearer " + notion_token,
        "Notion-Version": "2021-08-16",
        "Content-Type": "application/json"
    }, data=json.dumps(payload))

    error = '{"object":"list","results":[],"next_cursor":null,"has_more":false}'
    if r.text == error:
        return True
    return False


if __name__ == '__main__':
   main()