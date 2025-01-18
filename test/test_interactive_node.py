from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from gui.interactions import InteractiveNode
from models.goal import GoalNode


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InteractiveNode Drag and Drop Test")
        self.setGeometry(100, 100, 800, 600)

        # QGraphicsScene 및 QGraphicsView 설정
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # GoalNode 객체 생성
        self.goal_node = GoalNode("Test Node")
        self.goal_node.description = "This is a test node."

        # InteractiveNode 객체 추가
        self.interactive_node = InteractiveNode(self.goal_node, self.update_scene)
        self.interactive_node.setPos(200, 200)
        self.scene.addItem(self.interactive_node)

    def update_scene(self):
        """테스트용 업데이트 콜백."""
        print("Scene updated!")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    test_window = TestWindow()
    test_window.show()
    sys.exit(app.exec_())