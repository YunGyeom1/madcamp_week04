#mainWindow.py
from PyQt5.QtWidgets import QSizePolicy, QApplication,QGraphicsScene,QGraphicsProxyWidget, \
                            QGraphicsWidget,QGraphicsView, QMainWindow, QVBoxLayout, QPushButton, \
                            QWidget, QHBoxLayout
from models.goal import MakeNode  # MakeNode 클래스가 models.goal 모듈에 있다고 가정
from gui.interactions import InteractiveNode  # InteractiveNode 클래스가 gui.interactions 모듈에 있다고 가정
from gui.showTree import TreeWidget
from PyQt5.QtCore import Qt, QRectF
from gui.sideDate import DateSidebar
from PyQt5.QtGui import QBrush, QPen, QPainter

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
    root = MakeNode("Root")
    child1 = MakeNode("C1")
    child2 = MakeNode("C2")
    child3 = MakeNode("C3")
    child4 = MakeNode("C4")
    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(child3)
    child1.add_child(child4)
    return root

# 실행 코드
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    root_node = create_sample_tree()
    main_window = MainWindow(root_node)
    main_window.show()
    sys.exit(app.exec_())