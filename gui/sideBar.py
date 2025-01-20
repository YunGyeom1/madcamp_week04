# sidebar.py
import sys
import os
from dotenv import load_dotenv
from PyQt5.QtCore import Qt, QDate, QEvent
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractScrollArea, QMainWindow, QLabel
)
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from pymongo import MongoClient
from bson.objectid import ObjectId
from gui.endNode import EndNode
from models.goal import add_leaf

# MongoDB 설정
load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]
tag_collection = db["Tags"]

class Sidebar(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # 2열 테이블 초기화
        self.date_range = 45  # 날짜 범위 초기화
        self.current_date = QDate.currentDate()  # 현재 날짜 초기화

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
            for i in range(-self.date_range, self.date_range + 1)
        ]

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
            
            if date in grouped_data:
                for node in grouped_data[date]:
                    if "deleted" not in node.get("tag", []) or "deleted" in selected_tags:
                        end_node = EndNode(node, self.populate_table)
                        container_layout.addWidget(end_node)

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

    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel and source is self.verticalScrollBar():
            # 스크롤이 하단에 가까우면 데이터를 더 로드
            if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
                self.load_more_dates(30)  # 스크롤 시 30일 추가 로드
            
            # 스크롤이 상단에 가까우면 데이터를 더 로드
            elif self.verticalScrollBar().value() == 0:
                self.load_more_dates(30)  # 스크롤 시 30일 이전 날짜 추가 로드

        return super().eventFilter(source, event)

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