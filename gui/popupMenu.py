#popupMenu.py
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel, QWidgetAction
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
from PyQt5.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCalendarWidget, QFormLayout, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt


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
                background-color: #007777;
                color: white;
            }
        """)
        # 팝업 메뉴 항목 추가

        # 팝업 메뉴 레이아웃
        self.setTitle("활동 세부 사항")

        # Description
        self.action_description = QAction("Description", self)
        self.action_description.triggered.connect(self.edit_description)

        # 달성 기간 설정
        self.action_duration = QAction("달성 기간 설정", self)
        self.action_duration.triggered.connect(self.set_duration)

        # 태그 설정
        self.action_tag = QAction("태그 설정", self)
        self.action_tag.triggered.connect(self.add_tag)

        # 반복 설정
        self.action_repeat = QAction("반복 설정", self)
        self.action_repeat.triggered.connect(self.repeat_settings)

        # 숨기기 토글 (스위치로 변경)
        self.action_toggle_visibility = QCheckBox("숨기기 토글", self)
        self.action_toggle_visibility.setChecked(False)
        self.action_toggle_visibility.stateChanged.connect(self.toggle_visibility)

        # 메뉴 항목 추가
        self.addAction(self.action_description)
        self.addAction(self.action_duration)
        self.addAction(self.action_tag)
        self.addAction(self.action_repeat)
        self.addSeparator()
        self.addWidget(self.action_toggle_visibility)

    def edit_description(self):
        """Description 클릭: 텍스트 수정"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Description 수정")
        layout = QVBoxLayout()

        label = QLabel("현재 Description:")
        text_edit = QLineEdit("Default Description")  # 기존 값을 가져오도록 수정 가능
        save_button = QPushButton("저장")

        layout.addWidget(label)
        layout.addWidget(text_edit)
        layout.addWidget(save_button)

        save_button.clicked.connect(lambda: print(f"Description 수정됨: {text_edit.text()}"))
        save_button.clicked.connect(dialog.accept)
        dialog.setLayout(layout)
        dialog.exec_()

    def set_duration(self):
        """달성 기간 설정"""
        dialog = QDialog(self)
        dialog.setWindowTitle("달성 기간 설정")

        layout = QVBoxLayout()

        start_calendar = QCalendarWidget()
        end_calendar = QCalendarWidget()

        layout.addWidget(QLabel("시작 날짜"))
        layout.addWidget(start_calendar)
        layout.addWidget(QLabel("종료 날짜"))
        layout.addWidget(end_calendar)

        save_button = QPushButton("저장")
        layout.addWidget(save_button)

        save_button.clicked.connect(lambda: print(
            f"기간 설정됨: {start_calendar.selectedDate().toString(Qt.ISODate)} - {end_calendar.selectedDate().toString(Qt.ISODate)}"))
        save_button.clicked.connect(dialog.accept)
        dialog.setLayout(layout)
        dialog.exec_()

    def add_tag(self):
        """태그 추가"""
        dialog = QDialog(self)
        dialog.setWindowTitle("태그 추가")

        layout = QVBoxLayout()
        tag_input = QLineEdit()
        tag_list = QComboBox()
        tag_list.addItems(["기존 태그 1", "기존 태그 2"])  # 기존 태그를 표시 가능

        add_button = QPushButton("추가")
        layout.addWidget(QLabel("새 태그 입력"))
        layout.addWidget(tag_input)
        layout.addWidget(QLabel("기존 태그 선택"))
        layout.addWidget(tag_list)
        layout.addWidget(add_button)

        add_button.clicked.connect(lambda: print(f"태그 추가됨: {tag_input.text()}"))
        add_button.clicked.connect(dialog.accept)
        dialog.setLayout(layout)
        dialog.exec_()

    def repeat_settings(self):
        """반복 설정"""
        dialog = QDialog(self)
        dialog.setWindowTitle("반복 설정")

        layout = QVBoxLayout()
        repeat_type = QComboBox()
        repeat_type.addItems(["매일", "매주", "매월", "매년"])
        confirm_button = QPushButton("확인")

        layout.addWidget(QLabel("반복 유형 선택"))
        layout.addWidget(repeat_type)
        layout.addWidget(confirm_button)

        confirm_button.clicked.connect(lambda: print(f"반복 설정됨: {repeat_type.currentText()}"))
        confirm_button.clicked.connect(dialog.accept)
        dialog.setLayout(layout)
        dialog.exec_()

    def toggle_visibility(self, state):
        """숨기기 토글"""
        if state == Qt.Checked:
            print("숨기기 활성화됨")
        else:
            print("숨기기 비활성화됨")

    def addWidget(self, widget):
        """QMenu에 QWidget 추가 (QCheckBox 등)"""
        action = QWidgetAction(self)
        action.setDefaultWidget(widget)
        self.addAction(action)

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
            menu.node = mock_node  # 가상 노드 연동
            menu.action_description.triggered.connect(menu.on_description_clicked)
            menu.action_duration.triggered.connect(menu.on_duration_clicked)
            menu.action_tag.triggered.connect(menu.on_tag_clicked)
            menu.action_repeat.triggered.connect(menu.on_repeat_clicked)
            menu.action_toggle_visibility.triggered.connect(menu.on_toggle_visibility_clicked)
            menu.exec_(self.test_button.mapToGlobal(pos))

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())