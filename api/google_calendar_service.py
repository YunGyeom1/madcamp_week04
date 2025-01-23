import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Calendar_Goals"]

# 사용자의 인증 정보를 저장할 파일
TOKEN_FILE = 'token.pickle'

# 구글 캘린더 API 스코프
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_account():
    creds = None
    # 이전에 저장된 토큰 파일이 있으면 사용
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 유효한 자격 증명이 없다면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 자격 증명을 저장하여 다음에 사용할 수 있도록 함
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_events_for_date(start_date, end_date):
    """특정 날짜 범위의 사용자가 생성한 일정을 가져온다."""
    try:
        creds = authenticate_google_account()
        service = build('calendar', 'v3', credentials=creds)

        # QDate 객체를 ISO 8601 형식의 문자열로 변환
        time_min = start_date.toString("yyyy-MM-ddT00:00:00Z")
        time_max = end_date.toString("yyyy-MM-ddT23:59:59Z")

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []



def create_event(node_id):
    """node_id를 받아서 DB에서 가져와서 구글 캘린더에 등록"""
    try:
        print("create event!!")
        creds = authenticate_google_account()
        service = build('calendar', 'v3', credentials=creds)

        node = collection.find_one({"_id": node_id})

        # 날짜와 시간을 조합하여 dateTime 생성
        event_date = node["date"]  # YYYY-MM-DD 형식
        start_time = node["start_time"]  # HH:MM 형식
        end_time = node["end_time"]  # HH:MM 형식

        # datetime 조합
        start_datetime = f"{event_date}T{start_time}:00"  # YYYY-MM-DDTHH:MM:SS
        end_datetime = f"{event_date}T{end_time}:00"  # YYYY-MM-DDTHH:MM:SS

        # 이벤트 세부 정보 설정
        event = {
            'summary': node["title"],
            'location': node["location"],
            'description': node["description"],
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        # 이벤트 생성
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"이벤트 생성됨: {event_result.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    create_event()
