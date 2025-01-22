from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QScrollArea, QVBoxLayout, QSizePolicy, QLabel
from PyQt5.QtCore import Qt, QEvent
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from db.db import get_collection

tag_collection = get_collection("Tags")
goal_collection = get_collection("Test")

class TagFilterWidget(QWidget):
    def __init__(self, update_callback = None):
        super().__init__()

        self.update_callback = update_callback
        self.tags = list(tag_collection.find())
        self.tags.sort(key=lambda tag: (tag["name"] != "all", tag["name"] == "deleted"))
        self.ensure_essential_tags()
        self.init_ui()

    def init_ui(self):
        # 메인 레이아웃 설정
        self.setStyleSheet("background-color: #F5F5F5;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    
        # 스크롤 영역 추가
        self.scroll_area = QScrollArea()  # 클래스 속성으로 선언
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 수직 스크롤 바 제거
        main_layout.addWidget(self.scroll_area)

        # 마우스 휠 이벤트 필터 추가
        self.scroll_area.viewport().installEventFilter(self)

        # 스크롤 콘텐츠 위젯
        scroll_content = QWidget()
        scroll_content.setMinimumHeight(40) 
        scroll_content.setMinimumWidth(len(self.tags) * 110)  # 태그 수에 따라 최소 너비 설정
        scroll_content.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(scroll_content)

        # 수평 레이아웃 (태그 버튼을 배치)
        self.scroll_layout = QHBoxLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)  # 태그 버튼 간 마진 제거
        self.scroll_layout.setSpacing(0)  # 버튼 간 간격 제거
        scroll_content.setLayout(self.scroll_layout)

        # 각 태그에 대해 버튼 생성
        for tag in self.tags:
            tag_name = tag["name"]
            is_selected = tag["selected"]

            # 버튼 생성
            button = QPushButton(tag_name)
            button.setFixedSize(80, 30)  # 버튼 크기 고정

            # 초기 색상 설정
            self.update_button_style(button, tag_name, is_selected)

            # 버튼 클릭 이벤트 연결
            button.clicked.connect(lambda checked, btn=button, name=tag_name: self.toggle_tag(btn, name))

            # 버튼을 수평 레이아웃에 추가
            self.scroll_layout.addWidget(button)


    def update_button_style(self, button, tag_name, is_selected):
        if tag_name == "deleted":
            # deleted 버튼: 초록(활성), 빨강(비활성)
            if is_selected:
                button.setStyleSheet("background-color: lightgreen; color: black; font-weight: bold;")
            else:
                button.setStyleSheet("background-color: lightcoral; color: black; font-weight: bold;")
        else:
            # 일반 태그: 초록(활성), 회색(비활성)
            if is_selected:
                button.setStyleSheet("background-color: lightgreen; color: black; font-weight: bold;")
            else:
                button.setStyleSheet("background-color: lightgray; color: black; font-weight: bold;")

    def toggle_tag(self, button, tag_name):
        tag = tag_collection.find_one({"name": tag_name})
        if not tag:
            return

        is_selected = not tag["selected"]

        # 색상 업데이트
        self.update_button_style(button, tag_name, is_selected)

        # MongoDB 업데이트
        tag_collection.update_one(
            {"name": tag_name},
            {"$set": {"selected": is_selected}}
        )

        if tag_name != "all" and is_selected:
            tag_collection.update_one(
                {"name": "all"},
                {"$set": {"selected": False}}
            )
            # 'all' 버튼의 색상도 업데이트
            for i in range(self.scroll_layout.count()):
                item = self.scroll_layout.itemAt(i)
                widget = item.widget()
                if isinstance(widget, QPushButton) and widget.text() == "all":
                    self.update_button_style(widget, "all", False)
                    break

        if self.update_callback:
            self.update_callback()

    def ensure_essential_tags(self):
        # 'all' 태그가 없으면 추가
        if not any(tag["name"] == "all" for tag in self.tags):
            all_tag = {"name": "all", "selected": True}
            tag_collection.insert_one(all_tag)
            self.tags.append(all_tag)

        # 'deleted' 태그가 없으면 추가
        if not any(tag["name"] == "deleted" for tag in self.tags):
            deleted_tag = {"name": "deleted", "selected": False}
            tag_collection.insert_one(deleted_tag)
            self.tags.append(deleted_tag)

    def eventFilter(self, obj, event):
        if obj == self.scroll_area.viewport() and event.type() == QEvent.Wheel:
            delta = event.angleDelta().y()
            horizontal_scroll = self.scroll_area.horizontalScrollBar()
            horizontal_scroll.setValue(horizontal_scroll.value() - delta)
            return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    import sys

    # MongoDB에서 태그 데이터 가져오기
    tags = list(tag_collection.find())

    #test_tags = [{"name": f"tag_{i}", "selected": False} for i in range(1, 4)]
    test_tags = []
    added_tags = []

    for test_tag in test_tags:
        if not any(tag["name"] == test_tag["name"] for tag in tags):
            # MongoDB에 태그 추가
            tag_collection.insert_one(test_tag)
            added_tags.append(test_tag["name"])  # 추가된 태그 이름 저장

    try:
        # PyQt 애플리케이션 시작
        app = QApplication(sys.argv)
        window = TagFilterWidget()
        window.setWindowTitle("Tag Filter")
        window.resize(500, 40)
        window.show()
        sys.exit(app.exec_())
    finally:
        # 테스트 데이터 삭제
        #print("Deleting test tags:", added_tags)
        for tag_name in added_tags:
            tag_collection.delete_one({"name": tag_name})
        print("Test tags deleted.")