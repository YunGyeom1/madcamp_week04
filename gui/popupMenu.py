#popupMenu.py
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt, QRectF


class NodePopupMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 70);
                border: 1px solid #cccccc;
                font-size: 14px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
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

    def on_description_clicked(self):
        """Description 클릭: 노드 제목 변경."""
        new_title, ok = QInputDialog.getText(None, "노드 제목 변경", "새 제목을 입력하세요:", text=self.node.title)
        if ok and new_title:
            self.node.title = new_title
            self.title_text.setText(new_title)
            print(f"노드 제목이 '{new_title}'로 변경되었습니다.")

    def on_duration_clicked(self):
        """달성 기간 설정 클릭: 캘린더로 시작/종료 날짜 설정."""
        dialog = DateRangeDialog()
        if dialog.exec_():  # 사용자가 "확인" 버튼을 클릭하면
            start_date, end_date = dialog.get_dates()
            print(f"달성 기간 설정: 시작={start_date}, 종료={end_date}")
            self.node.start_date = start_date
            self.node.end_date = end_date

    def on_tag_clicked(self):
        """태그 설정 클릭: 노드 태그 추가."""
        new_tag, ok = QInputDialog.getText(None, "태그 추가", "새 태그를 입력하세요:")
        if ok and new_tag:
            if not hasattr(self.node, "tags"):
                self.node.tags = []
            self.node.tags.append(new_tag)
            print(f"태그 '{new_tag}'가 추가되었습니다. 현재 태그: {self.node.tags}")

    def on_repeat_clicked(self):
        """반복 설정 클릭: 추가 구현 필요."""
        print("반복 설정 기능은 아직 구현되지 않았습니다.")

    def on_toggle_visibility_clicked(self):
        print("NO")

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