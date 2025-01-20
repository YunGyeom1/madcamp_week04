#popupMenu.py
from PyQt5.QtWidgets import QDialog, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel, QWidgetAction, QTimeEdit
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
from PyQt5.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCalendarWidget, QFormLayout, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt


class NodePopupMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("활동 세부 사항")

        layout = QVBoxLayout()
    
        # 팝업 메뉴 항목 추가

        # 팝업 메뉴 레이아웃
    

        # Description field
        layout.addWidget(QLabel("Description"))
        description_input = QLineEdit()
        description_input.setPlaceholderText("일정에 대한 설명입니다.")
        layout.addWidget(description_input)

        # Tag field
        layout.addWidget(QLabel("태그:"))
        tag_input = QLineEdit()
        layout.addWidget(tag_input)

        # 달성 기간 설정 버튼
        date_button = QPushButton("달성 기간 설정")
        date_button.clicked.connect(self.set_date)
        layout.addWidget(QLabel("달성 기간"))
        layout.addWidget(date_button)

        # Time setting fields
        layout.addWidget(QLabel("시간 설정"))
        time_layout = QVBoxLayout()
        start_time = QTimeEdit()
        start_time.setDisplayFormat("HH:mm")
        start_time.setTime(QTime(QTime.currentTime().hour(), 0))  # 현재 시간에 분은 00

        end_time = QTimeEdit()
        end_time.setDisplayFormat("HH:mm")
        end_time.setTime(QTime(QTime.currentTime().hour() + 1, 0))  # 종료 시간은 기본적으로 1시간 후, 분은 00

        time_layout.addWidget(start_time)
        time_layout.addWidget(end_time)
        layout.addLayout(time_layout)

        # 반복 설정
        layout.addWidget(QLabel("반복 설정"))
        repeat_combo = QComboBox()
        repeat_combo.addItems(["매주", "매월", "매년", "반복 안 함"])
        layout.addWidget(repeat_combo)

        # 숨기기 토글
        hide_checkbox = QCheckBox("숨기기 토글")
        layout.addWidget(hide_checkbox)

        save_button = QPushButton("저장")
        layout.addWidget(save_button)
        save_button.clicked.connect(self.accept)

        self.setLayout(layout)

    def set_date(self):
        """달성 기간 설정 팝업."""
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("달성 기간 설정")

        date_layout = QVBoxLayout()

        start_calendar = QCalendarWidget()
        end_calendar = QCalendarWidget()
        start_calendar.setSelectedDate(QDate.currentDate())
        end_calendar.setSelectedDate(QDate.currentDate().addDays(7))

        date_layout.addWidget(QLabel("시작 날짜"))
        date_layout.addWidget(start_calendar)
        date_layout.addWidget(QLabel("종료 날짜"))
        date_layout.addWidget(end_calendar)

        save_date_button = QPushButton("저장")
        date_layout.addWidget(save_date_button)
        save_date_button.clicked.connect(date_dialog.accept)

        date_dialog.setLayout(date_layout)
        date_dialog.exec_()

if __name__ == "__main__":

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("NodePopupMenu Test")
            self.setGeometry(100, 100, 400, 300)

            # 중앙 위젯 설정
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)

            # 테스트 버튼 추가
            self.test_button = QPushButton("Right Click Me")
            self.test_button.setContextMenuPolicy(Qt.CustomContextMenu)
            self.test_button.customContextMenuRequested.connect(self.show_context_menu)
            layout.addWidget(self.test_button)

            self.setCentralWidget(central_widget)

        def show_context_menu(self, pos):
            """NodePopupMenu를 표시."""
            # 가상 노드 데이터 생성
            mock_node = type("MockNode", (object,), {"title": "Test Node", "tags": []})()

            menu = NodePopupMenu(self)
            #menu.node = mock_node  # 가상 노드 연동
            menu.exec_()

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())