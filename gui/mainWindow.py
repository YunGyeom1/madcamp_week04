from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QFontDatabase, QFont
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path = env_path)

from models.goal import MakeNode, collection, set_time
from gui.showTree import TreeWidget
from gui.sideBar import Sidebar  # Sidebar를 가져옴
from gui.filter import TagFilterWidget

class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()

        # 중앙 위젯 및 수직 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)  # 세로 레이아웃 사용 (필터와 트리를 세로로 배치)
        layout.setSpacing(0) 
        layout.setContentsMargins(0, 0, 0, 0) 

        # 태그 필터 생성 및 추가
        self.filter_widget = TagFilterWidget(self.update_tree)
        
        layout.addWidget(self.filter_widget)  # 필터를 위에 추가

        # 수평 레이아웃: Tree와 Sidebar 배치
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(main_layout)  # 수평 레이아웃을 세로 레이아웃에 추가

        # QGraphicsScene 및 QGraphicsView 설정
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 트리 위젯 생성
        self.tree_widget = TreeWidget(root)
        self.scene.addWidget(self.tree_widget)  # 트리 위젯 추가
        self.scene.setSceneRect(QRectF(self.view.rect()))
        
        # QGraphicsView를 레이아웃에 추가
        main_layout.addWidget(self.view, stretch=4)

        # Sidebar 생성 및 설정 (사이드바는 오른쪽에 배치)
        self.sidebar = Sidebar()
        self.update_sidebar = self.sidebar.update
        self.filter_widget.update_sidebar = self.update_sidebar
        self.tree_widget.update_sidebar = self.update_sidebar

        self.sidebar.setFixedWidth(420)  # 사이드바 폭 고정
        main_layout.addWidget(self.sidebar, stretch=1)  # Sidebar 배치
        
        # 윈도우 기본 설정
        self.setWindowTitle("NODELIGHT")  # 창의 타이틀 설정

        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

    def update_tree(self):
        self.tree_widget.update_tree()
    

    def resizeEvent(self, event):
        """윈도우 크기 조정 이벤트 처리."""
        super().resizeEvent(event)

        # QGraphicsView의 크기를 MainWindow의 크기에 맞게 조정
        self.view.setGeometry(self.rect())

        # TreeWidget의 크기를 QGraphicsView에 맞게 조정
        if self.tree_widget:
            self.tree_widget.setGeometry(0, 0, self.view.width(), self.view.height())
        self.scene.setSceneRect(QRectF(self.view.rect()))  # 뷰의 크기에 맞춰 씬 크기 설정
        self.filter_widget.setFixedHeight(60)
        self.filter_widget.setFixedHeight(60)

            
def create_sample_tree():
    # def print_node_details(node_id):
    #     node = collection.find_one({"_id": ObjectId(node_id)})
    #     if node:
    #         print(f"Node: {node['title']}, ID: {node_id}")
    #         print(f"  Height: {node.get('height', 'N/A')}, Width: {node.get('width', 'N/A')}")
    #         print(f"  Start Time: {node.get('start_time', 'N/A')}, End Time: {node.get('end_time', 'N/A')}")
    #     else:
    #         print(f"[ERROR] Node with ID {node_id} not found.")

    # 루트 노드 생성
    root_id = ObjectId(os.getenv("DUMMY_ROOT_ID"))

    # 자식 노드 생성
    # child1_id = MakeNode("C1", root_id)
    # child2_id = MakeNode("C2", root_id)
    # child3_id = MakeNode("C3", child1_id)  # 시간 없이 생성
    # child4_id = MakeNode("C4", child1_id)  # 시간 없이 생성

    # # 각 노드의 상세 정보를 출력
    # print_node_details(root_id)  # 루트 노드 정보 출력
    # print_node_details(child1_id)  # 자식 노드 1 정보 출력
    # print_node_details(child2_id)  # 자식 노드 2 정보 출력
    # print_node_details(child3_id)  # 자식 노드 3 정보 출력
    # print_node_details(child4_id)  # 자식 노드 4 정보 출력

    # # set_time 함수로 시간 설정
    # set_time(child3_id, start_time="09:00", end_time="10:00")
    # set_time(child4_id, start_time="10:30", end_time="11:30")

    # # 각 노드의 시간 정보를 출력
    # print_node_details(child3_id)
    # print_node_details(child4_id)

    return root_id

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    font_id = QFontDatabase.addApplicationFont("/Users/yungyeom/Downloads/madcamp_week4/madcamp_week04/assets/제주고딕(윈도우).otf")
    print("FontID: ", font_id)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    app.setFont(QFont(font_family, 10))
    root_node_id = create_sample_tree()
    main_window = MainWindow(root_node_id)
    main_window.show()
    sys.exit(app.exec_())