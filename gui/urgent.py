from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QMainWindow, QWidget
from PyQt5.QtGui import QDrag
from PyQt5.QtCore import Qt, QMimeData
from db.db import get_collection

class GoalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Goal List")
        self.setGeometry(100, 100, 600, 400)
        
        # 중앙 위젯과 레이아웃 설정
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        self.layout = QVBoxLayout(central_widget)
        central_widget.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        
        # 목표 데이터 불러오기
        self.goal_collection = get_collection("Test")
        self.data = self.fetch_goals()
        
        # 테이블 위젯 설정
        self.table_widget = QTableWidget(self)
        self.layout.addWidget(self.table_widget)
        
        self.populate_table()

    def fetch_goals(self):
        # goal_collection에서 모든 데이터를 가져오고 종료일 기준으로 정렬
        goals = list(self.goal_collection.find())  # 예시로 find() 사용
        sorted_goals = sorted(goals, key=lambda x: (x['due_date'][1] if x['due_date'][1] else float('inf')))
        return sorted_goals

    def populate_table(self):
        # 테이블의 행과 열 설정 (title, due_date만 표시)
        self.table_widget.setColumnCount(2)  # title, due_date
        self.table_widget.setHorizontalHeaderLabels(['Title', 'Due Date'])
        
        # 데이터 테이블에 추가
        self.table_widget.setRowCount(len(self.data))
        
        for row, goal in enumerate(self.data):
            title_item = QTableWidgetItem(goal['title'])
            due_date_item = QTableWidgetItem(str(goal['due_date'][1]) if goal['due_date'][1] else 'N/A')
            
            self.table_widget.setItem(row, 0, title_item)
            self.table_widget.setItem(row, 1, due_date_item)
            
            # 드래그 이벤트 연결
            for col in range(2):  # 2개의 컬럼만 드래그 가능
                self.table_widget.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            
            # 드래그 이벤트 처리
            for col in range(2):
                self.table_widget.item(row, col).setData(Qt.UserRole, goal["_id"])

if __name__ == '__main__':
    app = QApplication([])
    window = GoalApp()
    window.show()
    app.exec_()