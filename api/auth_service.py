import sys
import os
import pickle
import webbrowser
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials

# Google API 인증을 위한 SCOPES
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleLoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Google 로그인')
        self.setGeometry(100, 100, 800, 600)

        # 구글 로그인 버튼
        self.login_button = QPushButton('구글 로그인', self)
        self.login_button.setGeometry(300, 250, 200, 50)
        self.login_button.clicked.connect(self.login_with_google)

        self.show()

    def login_with_google(self):
        """ 구글 로그인 처리 """
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # 구글 자격 증명이 없거나 만료된 경우 새로운 로그인 절차 진행
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # 로그인 후, 캘린더 API를 사용할 수 있는 자격증명을 받음
        self.calendar_service = self.build_calendar_service(creds)
        print("로그인 성공!")

    def build_calendar_service(self, creds):
        """ 캘린더 서비스 구축 """
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        return service

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GoogleLoginWindow()
    sys.exit(app.exec_())
