# sidebar.py
import sys
from PyQt5.QtCore import Qt, QDate, QEvent
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractScrollArea
)
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from models.goal import add_leaf
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from gui.endNode import EndNode
load_dotenv()

# MongoDB 설정
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]



class Sidebar(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # 2열 테이블
        self.date_range = 30  # 날짜 범위 초기화
        self.current_date = QDate.currentDate()  # 현재 날짜 초기화
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
        self.populate_table()

        print("Sidebar initialized")

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
        nodes.append({"title": "Example Node", "start_time": "10:00", "end_time": "11:00", "date": "2025-01-01"})
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

            if date in grouped_data:
                for node in grouped_data[date]:
                    end_node = EndNode(node)
                    container_layout.addWidget(end_node)

            self.setCellWidget(row, 0, node_container)  # 첫 번째 열에 컨테이너 추가

            # 두 번째 열: 날짜
            date_item = QTableWidgetItem(date)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, date_item)

        self.resizeRowsToContents()  # 행 높이 자동 조

    def load_more_dates(self, amount):
        """스크롤 시 더 많은 날짜를 로드"""
        self.date_range += amount
        self.populate_table()


    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel and source is self.verticalScrollBar():
            if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
                self.load_more_dates(30)  # 스크롤 시 30일 추가 로드
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

            # MongoDB에서 노드 데이터 확인
            data = collection.find_one({"_id": node_id})
            if not data:
                print(f"No data found for node ID: {node_id}")
                return

            # 새로운 노드 생성
            new_leaf_id = add_leaf(node_id)  # MongoDB에 새 leaf 노드 추가
            new_node_data = collection.find_one({"_id": new_leaf_id})

            # Sidebar에 새 노드 추가
            date = new_node_data.get("date", "N/A")
            row = self.find_row_by_date(date)
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

            end_node = EndNode(new_node_data)
            container_layout.addWidget(end_node)

            self.resizeRowsToContents()
            print(f"Added new node with ID: {new_leaf_id} under date: {date}")
        else:
            print("Invalid MIME data in dropEvent")
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