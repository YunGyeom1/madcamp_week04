# sidebar.py
import sys
import os
from dotenv import load_dotenv
from PyQt5.QtCore import Qt, QDate, QEvent, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractScrollArea, QMainWindow, QLabel
)
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QGraphicsScene
from PyQt5.QtWidgets import QVBoxLayout
from pymongo import MongoClient
from bson.objectid import ObjectId
from gui.endNode import EndNode
from models.goal import add_leaf
from api.google_calendar_service import get_events_for_date

# MongoDB 설정
load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]
tag_collection = db["Tags"]

def is_time_slot_available(date, start_time, end_time):
        """주어진 날짜에 시간대가 겹치는 노드가 있는지 확인."""
        # 같은 날짜의 노드 검색
        nodes_on_date = collection.find({"date": date})

        for node in nodes_on_date:
            existing_start = node.get("start_time")
            existing_end = node.get("end_time")
        
            # 시간 겹침 확인
            if existing_start and existing_end:
                if not (end_time <= existing_start or start_time >= existing_end):
                    # 시간이 겹치면 False 반환
                    return False
        return True

class Sidebar(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # 2열 테이블 초기화
        self.date_range = 45  # 날짜 범위 초기화
        self.current_date = QDate.currentDate()  # 현재 날짜 초기화
        self.copied_nodes = None
        self.scene = QGraphicsScene(self)

        self._setup_ui()
        self.populate_table()

    def update(self):
        """Sidebar 갱신 메서드"""
        self.populate_table() 

    def _setup_ui(self):
        """UI 초기 설정"""
        self.setHorizontalHeaderLabels(["Node", "Date"])  # 헤더 설정
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 150)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.installEventFilter(self)
        self.verticalHeader().setVisible(False)
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WA_AcceptDrops, True)

    def populate_table(self):
        """날짜는 항상 표시되며, 데이터가 있는 경우 함께 표시."""
        self.setRowCount(0)  # 기존 데이터 초기화

        # 날짜 범위 계산 (-30일 ~ +30일)
        all_dates = [
            self.current_date.addDays(i).toString("yyyy-MM-dd")
            for i in range(-35, 365)
        ]
        qdate_list = [self.current_date.addDays(i) for i in range(-self.date_range, self.date_range + 1)]
        
        
        # MongoDB에서 데이터 가져오기
        nodes = list(collection.find())  # 실제 데이터를 가져옴
        # 날짜별로 그룹화
        grouped_data = {}
        for node in nodes:
            date = node.get("date")
            if not date:  # date 필드가 없는 경우 무시
                continue
            if date not in grouped_data:
                grouped_data[date] = []
            grouped_data[date].append(node)

        # google_calendar_service.py에서 특정 날짜 범위의 일정들을 가져옴
        google_events = get_events_for_date(min(qdate_list), max(qdate_list))
        google_grouped_data = {}
        for event in google_events:
            start_date = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
            if start_date:
                start_date = QDate.fromString(start_date[:10], "yyyy-MM-dd").toString("yyyy-MM-dd")
                if start_date not in google_grouped_data:
                    google_grouped_data[start_date] = []
                google_grouped_data[start_date].append(event)
        

        # 테이블에 날짜 및 데이터 추가
        for date in all_dates:
            row = self.rowCount()
            self.insertRow(row)

            # 첫 번째 열: EndNode들을 쌓을 컨테이너 위젯 생성
            node_container = QWidget()
            container_layout = QVBoxLayout(node_container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(5)
            selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]
            
            # MongoDB 일정 추가
            if date in grouped_data:
                for node in grouped_data[date]:
                    if "deleted" not in node.get("tag", []) or "deleted" in selected_tags:
                        end_node = EndNode(node, self.populate_table)
                        container_layout.addWidget(end_node)

            # Google Calendar 이벤트 추가
            if date in google_grouped_data:
                for event in google_grouped_data[date]:
                    event_title = event.get("summary", "Untitled Event")
                    google_node = NodeWidget(event_title)  # Custom widget to display Google event
                    container_layout.addWidget(google_node)

                    # 시간 정보 가져오기
                    start_time = event.get('start', {}).get('dateTime')  # 'dateTime' 형식이 있을 때만
                    end_time = event.get('end', {}).get('dateTime')
                    if start_time:
                        start_time = QDateTime.fromString(start_time, Qt.ISODate).toString("HH:mm")
                        end_time = QDateTime.fromString(end_time, Qt.ISODate).toString("HH:mm")
                        event_title += f" ({start_time} - {end_time})"
        
                    google_node = NodeWidget(event_title)  # Custom widget to display Google event
                    container_layout.addWidget(google_node)

            self.setCellWidget(row, 0, node_container)  # 첫 번째 열에 컨테이너 추가

            # 두 번째 열: 날짜
            date_item = QTableWidgetItem(date)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, date_item)

        self.resizeRowsToContents()  # 행 높이 자동 조

        today_date_str = self.current_date.toString("yyyy-MM-dd")
        today_row = self.find_row_by_date(today_date_str)
        if today_row is not None:
            today_item = self.item(today_row, 1)
            if today_item:
                self.scrollToItem(today_item)

    def load_more_dates(self, amount):
        """스크롤 시 더 많은 날짜를 로드"""
        self.date_range += amount
        self.populate_table()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clearSelection()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            selected_items = self.selectedItems()  # 드래그 후 선택된 아이템들
            print(f"Selected items after drag: {[item.text() for item in selected_items]}")  # node를 텍스트로 출력

    def dragEnterEvent(self, event):
        """드래그 항목이 들어왔을 때 호출."""
        if event.mimeData().hasFormat("application/x-node-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-node-id"):
            node_id = ObjectId(event.mimeData().data("application/x-node-id").data().decode("utf-8"))
            node_title = event.mimeData().text()
            event.acceptProposedAction()

            drop_position = event.pos()
            row = self.rowAt(drop_position.y())
            if row is None: 
                return
            
            # 드래그한 위치의 날짜 가져오기
            date_item = self.item(row, 1)
            if not date_item:
                print("No date associated with the drop position.")
                return
            drop_date = date_item.text()
            
            # MongoDB에서 노드 데이터 확인
            data = collection.find_one({"_id": node_id})
            if not data:
                print(f"No data found for node ID: {node_id}")
                return
            
            # 드래그한 노드의 시작 시간과 종료 시간 가져오기
            new_start_time = data.get("start_time")  # 노드의 시작 시간
            new_end_time = data.get("end_time")      # 노드의 종료 시간

            # 시간대 겹침을 검사
            if not is_time_slot_available(drop_date, new_start_time, new_end_time):
                print(f"Cannot add node on {drop_date}: time slot is already occupied.")
                return
            
            # 새로운 노드 생성
            new_leaf_id = add_leaf(node_id, date = drop_date)  # MongoDB에 새 leaf 노드 추가
            print(f"New leaf ID created: {new_leaf_id}")
            new_node_data = collection.find_one({"_id": new_leaf_id})

            # Sidebar에 새 노드 추가
            date = new_node_data.get("date", "N/A")
            row = self.find_row_by_date(date)
            print(f"New node's date: {date}")
            if row is None:
                print(f"No row found for date: {date}. Creating a new row.")
            else:
                print(f"Found existing row for date: {date}, Row index: {row}")
                if row is None:
                    row = self.rowCount()
                    self.insertRow(row)
                    date_item = QTableWidgetItem(date)
                    date_item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, 1, date_item)

            # 첫 번째 열 업데이트
            node_container = self.cellWidget(row, 0)
            if not node_container:
                node_container = QWidget()
                container_layout = QVBoxLayout(node_container)
                container_layout.setContentsMargins(5, 5, 5, 5)
                container_layout.setSpacing(5)
                self.setCellWidget(row, 0, node_container)
            else:
                container_layout = node_container.layout()

            end_node = EndNode(new_node_data, self.populate_table)
            container_layout.addWidget(end_node)
            node_container.setLayout(container_layout)
            node_container.updateGeometry()
            QApplication.processEvents()  
            
            self.resizeRowToContents(row)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-node-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def find_row_by_date(self, date):
        """지정된 날짜에 해당하는 행 번호를 반환."""
        for row in range(self.rowCount()):
            date_item = self.item(row, 1)
            if date_item and date_item.text() == date:
                return row
        return None

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_C:  # Ctrl+C
                print("ctrl-c")
                selected_items = self.scene.selectedItems()
                print(f"Selected items: {[item.node for item in selected_items]}") 
                if selected_items:
                    # 여러 개의 노드를 복사
                    self.copied_nodes = [item.node for item in selected_items]  # 복사할 노드들
            elif event.key() == Qt.Key_V:  # Ctrl+V
                print("ctrl-v")
                if self.copied_nodes:
                    selected_items = self.scene.selectedItems()
                    if selected_items:
                        parent_node_id = selected_items[0].node["_id"]  # 부모 노드 ID
                        # 새로운 날짜 계산: 드래그한 위치의 날짜
                        drop_date = self.get_drop_date()

                        # 복사된 여러 노드 처리
                        for i, copied_node in enumerate(self.copied_nodes):
                            new_node_data = copied_node.copy()  # 기존 데이터를 복사
                            new_node_data["date"] = drop_date  # 새로운 날짜로 변경
                            new_node_data["_id"] = ObjectId()  # 새로운 _id 생성

                            # 부모 ID 유지
                            new_node_data["parent_id"] = parent_node_id  # 부모 노드를 동일하게 유지

                            # 시간대 중복 검사
                            if not is_time_slot_available(drop_date, new_node_data["start_time"], new_node_data["end_time"]):
                                print(f"Cannot add node on {drop_date}: time slot is already occupied.")
                                continue

                            # MongoDB에 새 노드 추가
                            collection.insert_one(new_node_data)
                            print(f"Node copied with new ID: {new_node_data['_id']}")

                            # 날짜를 바꾼 후, 여러 개의 노드를 붙여넣을 때는 순차적으로 날짜를 증가시킬 수 있음
                            drop_date = self.get_next_day(drop_date)  # 날짜를 하루씩 증가

                        self.populate_table()  # 트리 갱신
            else:
                super().keyPressEvent(event)

    def get_next_day(self, date_str):
        """다음 날의 날짜를 반환"""
        date = QDate.fromString(date_str, "yyyy-MM-dd")
        next_day = date.addDays(1)
        return next_day.toString("yyyy-MM-dd")

    def get_drop_date(self):
        """드래그한 위치의 날짜를 반환"""
        drop_position = self.mapToScene(self.mousePos())
        row = self.rowAt(drop_position.y())
        date_item = self.item(row, 1)
        return date_item.text()

    def get_selected_node_ids(self):
        """선택된 셀들로부터 node_id를 추출하여 반환"""
        selected_ids = []
        selected_items = self.scene.selectedItems()  # 선택된 아이템들

        for item in selected_items:
            # 각 아이템에서 node_id를 추출
            if hasattr(item, 'node') and item.node and "_id" in item.node:
                node_id = item.node["_id"]
                selected_ids.append(node_id)

        return selected_ids

class NodeWidget(QWidget):
    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 제목 표시
        title_label = QLabel(f"<b>{title}</b>")
        layout.addWidget(title_label)

        # 설명 표시
        if description:
            description_label = QLabel(description)
            layout.addWidget(description_label)

        # 레이아웃 설정
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

if __name__ == "__main__":


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Sidebar Test")
            self.resize(600, 400)

            # 중앙 위젯 설정
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 레이아웃 생성
            layout = QVBoxLayout(central_widget)

            # Sidebar 인스턴스 생성 및 추가
            self.sidebar = Sidebar()
            layout.addWidget(self.sidebar)

    # PyQt 애플리케이션 실행
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())