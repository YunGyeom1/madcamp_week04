import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

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

def create_event():
    try:
        creds = authenticate_google_account()
        service = build('calendar', 'v3', credentials=creds)

        # 이벤트 세부 정보 설정
        event = {
            'summary': '목표 달성 미팅',
            'location': '온라인',
            'description': '이 목표를 위한 회의',
            'start': {
                'dateTime': '2025-01-30T10:00:00',
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': '2025-01-30T11:00:00',
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
