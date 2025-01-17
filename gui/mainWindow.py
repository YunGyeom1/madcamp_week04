from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from models.goal import GoalNode  # GoalNode 클래스가 models.goal 모듈에 있다고 가정
from gui.interactions import InteractiveNode  # InteractiveNode 클래스가 gui.interactions 모듈에 있다고 가정
from gui.showTree import TreeWidget
class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)

        # 트리 위젯 추가
        self.tree_widget = TreeWidget(root)
        layout.addWidget(self.tree_widget)

        # 버튼 추가
        add_node_button = QPushButton("Add Node")
        add_node_button.clicked.connect(self.add_node)
        layout.addWidget(add_node_button)

        # 윈도우 설정
        self.setWindowTitle("GoalNode Tree Visualization")
        self.setGeometry(100, 100, 1000, 600)

    def add_node(self):
        print("Add Node button clicked")
        # 노드 추가 로직 구현 가능

# 샘플 트리 생성
def create_sample_tree():
    root = GoalNode("Root")
    child1 = GoalNode("C1")
    child2 = GoalNode("C2")
    child3 = GoalNode("C3")
    child4 = GoalNode("C4")
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