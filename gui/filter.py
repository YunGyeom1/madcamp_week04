from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from db.db import get_collection

tag_collection = get_collection("Tags")
collection = get_collection()

class TagFilterWidget(QWidget):
    def __init__(self, tags, update_callback = None):
        super().__init__()
        self.update_callback = update_callback
        for tag in tags:
            if tag["name"] == "all":
                tag["selected"] = True
                tag["restricted"] = False
            elif tag["name"] == "deleted":
                tag["selected"] = False
                tag["restricted"] = True
            else:
                tag["selected"] = False
                tag["restricted"] = False
            tag_collection.update_one(
                {"name": tag["name"]},
                {"$set": {"selected": tag["selected"], "restricted": tag["restricted"]}},
                upsert=True  # 태그가 없으면 추가
            )
        self.tags = tags  # 태그 데이터 (리스트)
        self.init_ui()

    def init_ui(self):
        # 레이아웃 설정
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # 각 태그에 대해 버튼 생성
        for tag in self.tags:
            tag_name = tag["name"]
            is_selected = tag["selected"]
            is_restricted = tag["restricted"]

            # 버튼 생성
            button = QPushButton(tag_name)
            button.setFixedSize(100, 50)

            # 초기 색상 설정
            self.update_button_style(button, is_selected, is_restricted)

            # 버튼 클릭 이벤트 연결
            button.clicked.connect(lambda checked, btn=button, name=tag_name: self.toggle_tag(btn, name))

            self.layout.addWidget(button)

    def update_button_style(self, button, is_selected, is_restricted):
        if is_selected and is_restricted:
            button.setStyleSheet("background-color: orange; color: black; font-weight: bold;")
        elif is_selected:
            button.setStyleSheet("background-color: lightgreen; color: black; font-weight: bold;")
        elif is_restricted:
            button.setStyleSheet("background-color: lightcoral; color: black; font-weight: bold;")
        else:
            button.setStyleSheet("background-color: lightgray; color: black; font-weight: bold;")

    def toggle_tag(self, button, tag_name):
        tag = tag_collection.find_one({"name": tag_name})

        if not tag:
            return

        is_selected = tag["selected"]
        is_restricted = tag["restricted"]

        # all 태그의 동작
        if tag_name == "all":
            if is_selected or is_restricted:  # 회색으로만 설정
                is_selected = False
                is_restricted = False
            else:
                is_selected = True
                is_restricted = False
        else:
            # 다른 태그 클릭 시 all을 회색으로
            all_tag = tag_collection.find_one({"name": "all"})
            if all_tag:
                all_tag["selected"] = False
                all_tag["restricted"] = False
                tag_collection.update_one(
                    {"name": "all"},
                    {"$set": {"selected": False, "restricted": False}}
                )
                # 버튼 업데이트
                for i in range(self.layout.count()):
                    btn = self.layout.itemAt(i).widget()
                    if btn.text() == "all":
                        self.update_button_style(btn, False, False)
                        break

            # 상태 순환: 회색 -> 초록색 -> 붉은색 -> 회색
            if not is_selected and not is_restricted:  # 회색 -> 초록색
                is_selected = True
                is_restricted = False
            elif is_selected and not is_restricted:  # 초록색 -> 붉은색
                is_selected = False
                is_restricted = True
            elif not is_selected and is_restricted:  # 붉은색 -> 회색
                is_selected = False
                is_restricted = False

        # 색상 업데이트
        self.update_button_style(button, is_selected, is_restricted)

        # MongoDB 업데이트
        tag_collection.update_one(
            {"name": tag_name},
            {"$set": {"selected": is_selected, "restricted": is_restricted}}
        )

        
        if self.update_callback:
            self.update_callback()

# 테스트 코드
if __name__ == "__main__":
    import sys

    # MongoDB에서 태그 데이터 가져오기
    tags = list(tag_collection.find())

    # 테스트 데이터를 추가
    test_tags = [
        {"name": "study", "selected": True, "restricted": False},
        {"name": "work", "selected": False, "restricted": False},
    ]

    # 태그 데이터와 테스트 데이터 병합 (중복 방지)
    for test_tag in test_tags:
        if not any(tag["name"] == test_tag["name"] for tag in tags):
            # MongoDB에 태그 추가
            tag_collection.insert_one(test_tag)
            tags.append(test_tag)

    # PyQt 애플리케이션 시작
    app = QApplication(sys.argv)
    window = TagFilterWidget(tags)
    window.setWindowTitle("Tag Filter")
    window.resize(500, 100)
    window.show()
    sys.exit(app.exec_())