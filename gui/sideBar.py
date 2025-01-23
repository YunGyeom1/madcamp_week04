# sidebar.py
import sys
import re
import os
from dotenv import load_dotenv
from PyQt5.QtCore import Qt, QDate, QEvent, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractScrollArea, QMainWindow, QLabel,
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
)
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QGraphicsScene
from PyQt5.QtWidgets import QVBoxLayout
from pymongo import MongoClient
from bson.objectid import ObjectId
from gui.endNode import EndNode
from models.goal import add_leaf
from api.google_calendar_service import get_events_for_date
from datetime import datetime, timedelta
from api.google_calendar_service import create_event

# MongoDB 설정
load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Calendar_Goals"]
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
        self.selected_dates = None
        self.selected_nodes = None
        self.last_clicked_date = None

    def _setup_ui(self):
        """UI 초기 설정"""
        self.setHorizontalHeaderLabels(["Node", "Date"])  # 헤더 설정
        self.setColumnWidth(0, 270)
        self.setColumnWidth(1, 150)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
            for i in range(-35, 305)
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
            self.selected_dates = self.selectedItems()  # 드래그 후 선택된 아이템들
            print(f"Selected items after drag: {[item.text() for item in self.selected_dates]}")  # node를 텍스트로 출력
            
            mouse_pos = event.pos()  # 마우스 클릭 위치
            row = self.rowAt(mouse_pos.y())  # 클릭된 행의 인덱스
            column = self.columnAt(mouse_pos.x())  # 클릭된 열의 인덱스

            print(f"Row: {row}, Column: {column}")  # 디버깅: 클릭된 행, 열 출력

            if row >= 0 and column >= 0:
                clicked_item = self.item(row, column)  # 클릭된 셀 가져오기
                clicked_date = None  # 기본 날짜 값 설정

                # 첫 번째 셀에서 날짜 확인
                if clicked_item and clicked_item.text():  # 텍스트가 존재하는지 확인
                    clicked_date = clicked_item.text()

                # 옆 셀에서 날짜 확인 (열이 오른쪽으로 하나 더)
                if not clicked_date and column + 1 < self.columnCount():  # 옆 셀도 확인
                    adjacent_item = self.item(row, column + 1)  # 옆 셀 (우측 셀)
                    if adjacent_item and adjacent_item.text():
                        clicked_date = adjacent_item.text()

                if clicked_date:
                    self.last_clicked_date = clicked_date
                    print(f"Clicked date: {clicked_date}")
                else:
                    print("No date found in clicked or adjacent cells.")
            else:
                print("Clicked outside of valid area.")


    def dragEnterEvent(self, event):
        """드래그 항목이 들어왔을 때 호출."""
        if event.mimeData().hasFormat("application/x-node-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def get_filtered_node_ids(self):
        """선택된 날짜들에 대해 필터 조건에 맞는 node_id들을 날짜별로 반환"""
        filtered_node_ids = {}
        selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]
        
        # 주어진  날짜들에 대해
        for date_item in self.selected_dates:
            date = date_item.text()
            # 날짜별로 노드들을 담을 리스트
            node_ids_for_date = []
            
            # 'date' 필드와 일치하는 노드들을 collection에서 찾기
            nodes = collection.find({"date": date})
            
            for node in nodes:
                # 1. 'deleted' 태그가 없거나, 'deleted'가 selected_tags에 포함되어야 한다
                if "deleted" not in node.get("tag", []) or "deleted" in selected_tags:
                    node_tags = node.get("tag", [])
                    # 2. 최소 하나의 태그가 selected_tags에 포함되어야 한다
                    if any(tag in selected_tags for tag in node_tags):
                        # 필터 조건을 만족하면 node_id 추가
                        node_ids_for_date.append(node["_id"])
            
            if node_ids_for_date:
                filtered_node_ids[date] = node_ids_for_date
        
        self.selected_nodes = filtered_node_ids
        print(filtered_node_ids)
        return filtered_node_ids

    def is_valid_time_format(self, time_str):
        """시간 형식이 HH:MM인지 확인하는 함수"""
        return bool(re.match(r'^\d{2}:\d{2}$', time_str))  # HH:MM 형식 (예: 12:34)
    
    def set_time(self, data, start_time, end_time):
        dialog = QDialog(self)
        dialog.setWindowTitle("시간 수정")
        
        # 레이아웃 설정
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # 시작 시간 입력
        self.start_time_edit = QLineEdit(dialog)
        self.start_time_edit.setText(start_time)
        form_layout.addRow("시작 시간 (HH:MM):", self.start_time_edit)

        # 종료 시간 입력
        self.end_time_edit = QLineEdit(dialog)
        self.end_time_edit.setText(end_time)
        form_layout.addRow("종료 시간 (HH:MM):", self.end_time_edit)

        layout.addLayout(form_layout)

        # 버튼 설정
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        # 다이얼로그 실행
        if dialog.exec_() == QDialog.Accepted:
            # 사용자가 OK 버튼을 클릭하면 입력된 시간 가져오기
            new_start_time = self.start_time_edit.text()
            new_end_time = self.end_time_edit.text()

            # 입력된 시간 검증 (00:00 형식)
            if not self.is_valid_time_format(new_start_time) or not self.is_valid_time_format(new_end_time):
                QMessageBox.warning(dialog, "잘못된 형식", "시간은 HH:MM 형식으로 입력해야 합니다.")
                self.set_time(data, start_time, end_time)  # 잘못된 형식일 경우 다이얼로그를 닫지 않음
                return

            # 시작 시간과 종료 시간을 업데이트
            if new_start_time:
                data["start_time"] = new_start_time
                collection.update_one({"_id": data["_id"]}, {"$set": {"start_time": new_start_time}})

            if new_end_time:
                data["end_time"] = new_end_time
                collection.update_one({"_id": data["_id"]}, {"$set": {"end_time": new_end_time}})

    
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

            if new_start_time==None or new_end_time==None:
                self.set_time(data, new_start_time, new_end_time)

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
                create_event(new_leaf_id)
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
                if self.selected_dates:  # 드래그 후 선택된 날짜가 있을 때만 실행
                    self.get_filtered_node_ids()

            elif event.key() == Qt.Key_V:  # Ctrl+V
                print("ctrl-v")
                if self.selected_nodes:
                    selected_items = self.selected_nodes  # 이미 선택된 노드들

                    all_dates = list(self.selected_nodes.keys())  # 모든 날짜를 리스트로 추출
                    first_date_str = min(all_dates)
                    first_date = datetime.strptime(first_date_str, "%Y-%m-%d") 
                    
                    drop_date_str = self.get_drop_date()  # 클릭된 날짜 (문자열)
                    drop_date = datetime.strptime(drop_date_str, "%Y-%m-%d")  # datetime 형식으로 변환

                    margin = drop_date - first_date


                    # 복사된 여러 노드 처리
                    for date_str, node_ids in selected_items.items():  # 날짜별로 복사된 노드들 처리
                        for node_id in node_ids:  # 각 날짜에 해당하는 노드들 처리
                            node = collection.find_one({"_id": node_id})  # 원본 노드 찾기
                            if node:
                                new_node_data = node.copy()  # 기존 노드 데이터를 복사
                                new_node_data.pop('_id', None)
                                # 해당 날짜에 margin을 더해서 노드 날짜 계산
                                node_date = datetime.strptime(date_str, "%Y-%m-%d")
                                new_node_date = node_date + margin  # margin을 더해 새로운 날짜 계산
                                new_node_data["date"] = new_node_date.strftime("%Y-%m-%d")  # 새로운 날짜 문자열로 변환

                                # MongoDB에 새 노드 추가
                                collection.insert_one(new_node_data)
                                print(f"Node copied with new ID: {new_node_data['_id']} on {new_node_data['date']}")

                    self.populate_table()  # 테이블 갱신     

            else:
                    super().keyPressEvent(event)

    def get_next_day(self, date_str):
        """다음 날의 날짜를 반환"""
        date = QDate.fromString(date_str, "yyyy-MM-dd")
        next_day = date.addDays(1)
        return next_day.toString("yyyy-MM-dd")

    def get_drop_date(self):
        # 예를 들어, selected_dates가 날짜 순서대로 정렬되어 있다고 가정
        
        return self.last_clicked_date

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