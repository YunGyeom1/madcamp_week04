#popupMenu.py
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt, QRectF


class NodePopupMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 팝업 메뉴 항목 추가
        self.action_description = QAction("Description", self)
        self.action_duration = QAction("달성 기간 설정", self)
        self.action_tag = QAction("태그 설정", self)
        self.action_repeat = QAction("반복 설정", self)
        self.action_toggle_visibility = QAction("숨기기 토글", self)

        # 메뉴에 항목 추가
        self.addAction(self.action_description)
        self.addAction(self.action_duration)
        self.addAction(self.action_tag)
        self.addAction(self.action_repeat)
        self.addAction(self.action_toggle_visibility)

    def connect_signals(self, callbacks):
        """콜백 함수들을 메뉴 항목에 연결."""
        self.action_description.triggered.connect(callbacks.get("description", lambda: None))
        self.action_duration.triggered.connect(callbacks.get("duration", lambda: None))
        self.action_tag.triggered.connect(callbacks.get("tag", lambda: None))
        self.action_repeat.triggered.connect(callbacks.get("repeat", lambda: None))
        self.action_toggle_visibility.triggered.connect(callbacks.get("toggle_visibility", lambda: None))


class DateRangeDialog(QDialog):
    """캘린더를 이용하여 날짜 범위를 설정하는 다이얼로그."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("달성 기간 설정")

        self.start_date = QCalendarWidget(self)
        self.end_date = QCalendarWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("시작 날짜"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("종료 날짜"))
        layout.addWidget(self.end_date)

        self.confirm_button = QPushButton("확인")
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def get_dates(self):
        """선택된 시작 날짜와 종료 날짜 반환."""
        start = self.start_date.selectedDate().toString(Qt.ISODate)
        end = self.end_date.selectedDate().toString(Qt.ISODate)
        return start, end