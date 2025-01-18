from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

from models.goal import MakeNode, collection
from gui.interactions import InteractiveNode
from gui.showTree import TreeWidget
from gui.sideDate import DateSidebar

class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()

        # 중앙 위젯 및 수평 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)  # Tree와 Sidebar를 나란히 배치

        # QGraphicsScene 및 QGraphicsView 설정
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        # TreeWidget을 장면에 추가
        self.tree_widget = TreeWidget(root)
        self.tree_widget.setGeometry(0, 0, 750, 600)  # 초기 크기 설정 (필요 시 제거 가능)
        self.scene.addWidget(self.tree_widget)

        # QGraphicsView를 레이아웃에 추가
        layout.addWidget(self.view)

        # DateSidebar 생성 및 설정
        self.date_sidebar = DateSidebar()
        self.date_sidebar.setFixedWidth(450)  # 사이드바 폭 고정
        layout.addWidget(self.date_sidebar)

        # 윈도우 기본 설정
        self.setWindowTitle("Resizable Tree and Sidebar")
        self.resize(1200, 600)
        self.setMinimumSize(800, 600)

def create_sample_tree():
    def print_node_details(node_id):
        node = collection.find_one({"_id": ObjectId(node_id)})
        if node:
            print(f"Node: {node['title']}, ID: {node_id}")
            print(f"  Height: {node.get('height', 'N/A')}, Width: {node.get('width', 'N/A')}")
        else:
            print(f"[ERROR] Node with ID {node_id} not found.")
    dummy_root_id = os.getenv("DUMMY_ROOT_ID")
    print(dummy_root_id)
    if not dummy_root_id: return

    root_id = MakeNode("Root", ObjectId(dummy_root_id))
    # 루트 노드 생성
    root_id = MakeNode(title="Root", parent=ObjectId(dummy_root_id))
    print_node_details(root_id)
    child1_id = MakeNode("C1", root_id)
    child2_id = MakeNode("C2", root_id)
    child3_id = MakeNode("C3", child1_id)
    child4_id = MakeNode("C4", child1_id)

    return root_id

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    root_node_id = create_sample_tree()
    main_window = MainWindow(root_node_id)
    main_window.show()
    sys.exit(app.exec_())