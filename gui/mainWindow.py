# mainWindow.py
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from bson.objectid import ObjectId  # MongoDB ObjectId를 사용하기 위한 임포트
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
# 커스텀 모듈 임포트
from models.goal import MakeNode, collection  # MakeNode 함수와 MongoDB 컬렉션
from gui.interactions import InteractiveNode  # InteractiveNode 클래스
from gui.showTree import TreeWidget  # TreeWidget 클래스
from gui.sideDate import DateSidebar  # DateSidebar 클래스

class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()

        # 그래픽 장면 및 뷰 설정
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        # TreeWidget 추가
        self.tree_widget = TreeWidget(root)
        self.tree_widget.setGeometry(0, 0, 750, 600)  # TreeWidget 초기 크기 설정
        self.scene.addWidget(self.tree_widget)

        # DateSidebar 추가 (TreeWidget의 오른쪽에 붙임)
        self.date_sidebar = DateSidebar()
        self.date_sidebar.setGeometry(750, 0, 300, 600)  # DateSidebar 초기 위치 설정
        self.scene.addWidget(self.date_sidebar)

        # QGraphicsView 크기 자동 조정
        self.view.setSceneRect(0, 0, 1200, 600)

        # 메인 레이아웃 설정
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.view)
        self.setCentralWidget(central_widget)

        # 윈도우 크기 변경 시 내부 요소 크기 조정
        self.resizeEvent = self.adjust_layout

        # 윈도우 설정
        self.setWindowTitle("Resizable Tree and Sidebar")
        self.resize(1200, 600)  # 초기 윈도우 크기 설정
        self.setMinimumSize(800, 600)

    def adjust_layout(self, event=None):
        # 현재 창 크기 가져오기
        width = self.size().width()
        height = self.size().height()

        # sidebar 폭 고정
        sidebar_width = 450  # 사이드바의 고정된 폭

        # TreeWidget과 Sidebar 위치 및 크기 조정
        self.tree_widget.setGeometry(0, 0, width - sidebar_width, height)  # TreeWidget은 나머지 공간 사용
        self.date_sidebar.setGeometry(width - sidebar_width, 0, sidebar_width, height)  # Sidebar는 고정된 크기와 위치


def create_sample_tree():
    
    def print_node_details(node_id):
        """디버깅용: 노드의 height와 width를 출력."""
        node = collection.find_one({"_id": ObjectId(node_id)})
        if node:
            print(f"Node: {node['title']}, ID: {node_id}")
            print(f"  Height: {node.get('height', 'N/A')}, Width: {node.get('width', 'N/A')}")
        else:
            print(f"[ERROR] Node with ID {node_id} not found.")
    dummy_root_id = os.getenv("DUMMY_ROOT_ID")
    print(dummy_root_id)
    if not dummy_root_id: return
    # 루트 노드 생성
    root_id = MakeNode("Root", ObjectId(dummy_root_id))
    print("[INFO] Created Root Node:")
    print_node_details(root_id)

    # 자식 노드 생성
    child1_id = MakeNode("C1", root_id)
    print("\n[INFO] Created Child Node C1:")
    print_node_details(child1_id)

    child2_id = MakeNode("C2", root_id)
    print("\n[INFO] Created Child Node C2:")
    print_node_details(child2_id)

    child3_id = MakeNode("C3", child1_id)
    print("\n[INFO] Created Child Node C3:")
    print_node_details(child3_id)

    child4_id = MakeNode("C4", child1_id)

    return root_id  # 루트 노드 ID 반환

# 실행 코드
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # 샘플 트리 생성
    root_node_id = create_sample_tree()  # root_node_id는 ObjectId

    # TreeWidget에 루트 노드 ID를 전달
    main_window = MainWindow(root_node_id)
    main_window.show()

    sys.exit(app.exec_())