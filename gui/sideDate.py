#sideDate.py
import sys
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from PyQt5.QtCore import QEvent  # 이벤트 필터에서 사용
from PyQt5.QtWidgets import QAbstractScrollArea  # 테이블 크기 조정 정책에 사용
from models.goal import add_leaf  # add_leaf 함수 import
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()


connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]
class DateSidebar(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # 2열 테이블
        self.setHorizontalHeaderLabels(["Content", "Date"])  # 헤더 설정
        self.setColumnWidth(0, 300)  # 첫 번째 열 너비
        self.setColumnWidth(1, 150)  # 두 번째 열 너비
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)  # 내용 크기에 맞게 조정
        self.setVerticalScrollMode(self.ScrollPerPixel)  # 부드러운 스크롤
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.installEventFilter(self)
        self.verticalHeader().setVisible(False)
        self.current_date = QDate.currentDate()  # 현재 날짜
        self.date_range = 30  # 초기 날짜 범위
        self.setAcceptDrops(True) 
        self.setAttribute(Qt.WA_AcceptDrops, True)
        self.populate_dates()
        
        print("DateSidebar initialized") 

    def populate_dates(self):
        """날짜와 내용을 초기화"""
        self.setRowCount(0)  # 기존 데이터 초기화

        for i in range(-self.date_range, self.date_range + 1):
            # 날짜 계산
            date = self.current_date.addDays(i)
            date_text = date.toString("yyyy-MM-dd")

            # 내용 설정
            if date_text == "2025-01-01":
                content_text = "This is the first line.\nThis is the second line."
            else:
                content_text = ""

            # 테이블에 행 추가
            row = self.rowCount()
            self.insertRow(row)

            # 내용 열
            content_item = QTableWidgetItem(content_text)
            content_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setItem(row, 0, content_item)

            # 날짜 열
            date_item = QTableWidgetItem(date_text)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, date_item)

        self.resizeRowsToContents()  # 행 높이 자동 조정

    def load_more_dates(self, amount):
        """스크롤 시 더 많은 날짜를 로드"""
        new_range = self.date_range + amount
        self.date_range = new_range
        self.populate_dates()
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel and source is self.verticalScrollBar():
            if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
                self.load_more_dates(30)  # 스크롤 시 30일 추가 로드
        return super().eventFilter(source, event)

    def dragMoveEvent(self, event):
        #print("DateSidebar: dragMoveEvent Triggered")
        if event.mimeData().hasFormat("application/x-node-id"):
            #print("Dragging over DateSidebar")
            event.acceptProposedAction()
        else:
            print("Invalid drag data in DateSidebar")
            event.ignore()
    
    def dragEnterEvent(self, event):
        #print("DateSidebar: dragEnterEvent Triggered")
        if event.mimeData().hasFormat("application/x-node-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-node-id"):
            node_id = ObjectId(event.mimeData().data("application/x-node-id").data().decode("utf-8"))
            node_title = event.mimeData().text()
            event.acceptProposedAction()
            
            # 드롭 위치 파악
            data = collection.find_one({"_id": node_id})
            if not data:
                print(f"No data found for node ID: {node_id}")
                return

            start_time = data.get("start_time", "09:00")
            end_time = data.get("end_time", "10:00")
            
            # 드롭 위치 파악
            drop_pos = event.pos()
            target_item = self.itemAt(drop_pos)
            if target_item is not None:
                row = target_item.row()
                
                # 새로운 노드 생성
                new_leaf_id = add_leaf(node_id)  # MongoDB에 새 leaf 노드 추가
                print(f"New leaf created with ID: {new_leaf_id}")

                # 사용자 정의 텍스트 추가
                additional_text = f"\n{start_time}~{end_time}: {node_title}"

                # 기존 텍스트 가져오기
                current_item = self.item(row, 0)  # 첫 번째 열의 항목
                if current_item is not None:
                    current_text = current_item.text()
                else:
                    current_text = ""
                text_list = current_text.split("\n") if current_text else []
                text_list.append(additional_text)
                def extract_start_time(text):
                    try:
                        return text.split("~")[0]  # 시작 시간 추출
                    except IndexError:
                        return ""
                sorted_text_list = sorted(text_list, key=extract_start_time, reverse = True)

                # 텍스트 업데이트
                updated_content = "\n".join(sorted_text_list)
                new_item = QTableWidgetItem(updated_content.strip())
                new_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.setItem(row, 0, new_item)

                self.resizeRowsToContents()
                print(f"Updated cell at row {row} with text: {updated_content}")
            else:
                print("드롭 위치에 해당하는 셀이 없습니다.")
        else:
            print("Invalid MIME data in dropEvent")
            event.ignore()