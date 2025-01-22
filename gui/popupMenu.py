#popupMenu.py
from PyQt5.QtWidgets import QDialog, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel, QWidgetAction, QTimeEdit, QColorDialog
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import sys
from PyQt5.QtWidgets import (
    QMenu, QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCalendarWidget, QFormLayout, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import os
from db.db import get_collection
from models.goal import set_child_color
collection = get_collection()
tag_collection = get_collection("Tags")

class NodePopupMenu(QDialog):
    popup_closed = pyqtSignal()  # 팝업 종료 시 신호
    def __init__(self, node_id=None, update_callback=None, update_callback2=None):
        super().__init__()
        self.update_callback = update_callback
        self.update_callback2 = update_callback2
        self.update_filter = None
        
        self.setWindowTitle("활동 세부 사항")
        self.resize(400, 600)  # 다이얼로그 크기 설정

        self.setStyleSheet("""
            QDialog {
                font-size: 20px;  /* 전체 팝업 폰트 크기 */
                padding: 20px;    /* 다이얼로그 안쪽 여백 */
            }
            QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton {
                font-size: 18px;  /* 개별 위젯 폰트 크기 */
            }
            QPushButton {
                padding: 10px;   /* 버튼 안쪽 여백 */
            }
        """)

        self.node_id=node_id
        self.node_data = collection.find_one({"_id": node_id})
        layout = QVBoxLayout()
    

        # Description field
        layout.addWidget(QLabel("Description"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("일정에 대한 설명입니다.")
        self.description_input.setText(self.node_data.get("description", ""))  # 기본값 설정
        layout.addWidget(self.description_input)

        # Tag field
        layout.addWidget(QLabel("태그:"))
        self.tag_input = QLineEdit()
        self.tag_input.setText(", ".join(map(str, self.node_data.get("tag", []))))  # 기본값 설정
        layout.addWidget(self.tag_input)

        # 달성 기간 설정 버튼
        self.date_button = QPushButton("달성 기간 설정")
        self.date_button.clicked.connect(self.set_date)
        layout.addWidget(QLabel("달성 기간"))
        layout.addWidget(self.date_button)

        # Time setting fields
        layout.addWidget(QLabel("시간 설정"))
        time_layout = QVBoxLayout()
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        start_time_str = self.node_data.get("start_time", "00:00")
        self.start_time.setTime(QTime.fromString(start_time_str, "HH:mm")) 

        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        end_time_str = self.node_data.get("end_time", "01:00")
        self.end_time.setTime(QTime(QTime.currentTime().hour() + 1, 0))  # 종료 시간은 기본적으로 1시간 후, 분은 00
        self.end_time.setTime(QTime.fromString(end_time_str, "HH:mm"))

        time_layout.addWidget(self.start_time)
        time_layout.addWidget(self.end_time)
        layout.addLayout(time_layout)

        # 반복 설정
        layout.addWidget(QLabel("반복 설정"))

        repeat_layout = QHBoxLayout()
        self.repeat_count = QComboBox()
        self.repeat_count.addItems([str(i) for i in range(1, 11)])  # 1부터 10까지 숫자
        self.repeat_count.setCurrentText(str(self.node_data.get("repeat", [1, 0])[0]))

        self.repeat_type = QComboBox()
        self.repeat_type.addItems(["반복 안함", "일", "주", "달"])  # 반복 주기
        self.repeat_type.setCurrentIndex(self.node_data.get("repeat", [1, 0])[1])

        # "마다" 라벨 추가
        self.repeat_label = QLabel("마다")
        self.repeat_label.setAlignment(Qt.AlignLeft)

        # 반복 설정 레이아웃 구성
        repeat_layout.addWidget(self.repeat_count)
        repeat_layout.addWidget(self.repeat_type)
        repeat_layout.addWidget(self.repeat_label)  # "마다" 추가
        layout.addLayout(repeat_layout)
        self.repeat_type.currentIndexChanged.connect(self.update_repeat_label_visibility) 


        # 색상 선택 버튼 추가
        layout.addWidget(QLabel("노드 색상"))
        self.color_button = QPushButton("색상 선택")
        self.color_button.clicked.connect(self.choose_color)
        self.node_color = self.node_data.get("color", "#FFFFFF")  # 기본 색상 흰색
        self.update_color_button(self.node_color)  # 버튼 배경 업데이트
        layout.addWidget(self.color_button)


        # 숨기기 토글
        self.hide_checkbox = QCheckBox("달성률 숨기기 토글")
        self.hide_checkbox.setChecked(self.node_data.get("isOpen", False))
        layout.addWidget(self.hide_checkbox)

        self.save_button = QPushButton("저장")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.accept)
        self.save_button.clicked.connect(lambda: self.save_node_changes(node_id))

        self.setLayout(layout)

    def accept(self):
        super().accept()
        self.popup_closed.emit()  # 팝업 종료 신호 보내기

    def reject(self):
        super().reject()
        self.popup_closed.emit()  # 팝업 종료 신호 보내기

    def update_repeat_label_visibility(self):
        if self.repeat_type.currentText() == "반복 안함":
            self.repeat_label.hide()
        else:
            self.repeat_label.show()

    def choose_color(self):
        """색상 선택 다이얼로그 표시."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.node_color = color.name()  # 색상 값을 hex 문자열로 저장
            self.update_color_button(self.node_color)

    def update_color_button(self, color):
        """색상 버튼의 배경색을 업데이트."""
        self.color_button.setStyleSheet(f"background-color: {color};")

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
        save_date_button.clicked.connect(lambda: self.save_due_date(start_calendar.selectedDate(), end_calendar.selectedDate()))


        date_dialog.setLayout(date_layout)
        date_dialog.exec_()

    def save_due_date(self, start_date, end_date):
        """캘린더 형태의 팝업 써야돼서 따로 저장해야될 것 같음."""
        start_date_str = start_date.toString("yyyy-MM-dd")
        end_date_str = end_date.toString("yyyy-MM-dd")

        updated_node = {
            "due_date": [start_date_str, end_date_str]
        }

        collection.update_one({"_id": self.node_id}, {"$set": updated_node})
        print(f"Due date updated: {start_date_str} to {end_date_str}")
        self.accept()


    def save_node_changes(self, node_id):
        """입력된 정보를 사용하여 노드 업데이트."""
        description = self.description_input.text()
        start_time = self.start_time.time().toString("HH:mm")
        end_time = self.end_time.time().toString("HH:mm")
        hide_toggle = self.hide_checkbox.isChecked()
        tag = self.tag_input.text()
        tags = list(map(str.strip, tag.split(", "))) if tag else []

        repeat_count = int(self.repeat_count.currentText())
        repeat_type_mapping = {"반복 안함": 0, "일": 1, "주": 2, "달": 3}
        repeat_type = repeat_type_mapping[self.repeat_type.currentText()]
    
        # DB에서 기존 노드 가져오기
        node_data = collection.find_one({"_id": node_id})
        if not node_data:
            print(f"Error: Node with ID {node_id} not found.")
            return
        existing_tags = {tag["name"] for tag in tag_collection.find({}, {"name": 1})}
        new_tags = set(tags) - existing_tags
        if new_tags:
            tag_collection.insert_many([{"name": t, "selected": False} for t in new_tags])
        # DB 스키마 업데이트
        updated_node = {
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "isOpen": not hide_toggle,
            "tag": tags,
            "repeat": [repeat_count, repeat_type],
        }

        # DB에 업데이트 적용
        collection.update_one(
            {"_id": node_id},
            {"$set": updated_node}
        )

        set_child_color(node_id, self.node_color)
        if self.update_callback:
            self.update_callback()
        if self.update_callback2:
            self.update_callback2()
        else:
            print("error")
        if self.update_filter:
            self.update_filter()
        else: print("error222")
        print("노드가 성공적으로 업데이트되었습니다.")


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