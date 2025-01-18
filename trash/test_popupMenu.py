from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
#popupMenu.py
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QCalendarWidget, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QDate
from PyQt5.QtCore import Qt, QRectF
from gui.popupMenu import NodePopupMenu, DateRangeDialog


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodePopupMenu Test")
        self.setGeometry(100, 100, 400, 300)

        # 테스트 버튼 추가
        self.test_button = QPushButton("Right Click Me", self)
        self.test_button.setGeometry(150, 120, 100, 40)
        self.test_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.test_button.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        """NodePopupMenu를 표시."""
        # 테스트용 노드 데이터 생성
        mock_node = type("MockNode", (object,), {"title": "Test Node", "tags": []})()
        
        menu = NodePopupMenu(self)
        menu.node = mock_node  # 가상 노드 연동
        menu.action_description.triggered.connect(menu.on_description_clicked)
        menu.action_duration.triggered.connect(menu.on_duration_clicked)
        menu.action_tag.triggered.connect(menu.on_tag_clicked)
        menu.action_repeat.triggered.connect(menu.on_repeat_clicked)
        menu.action_toggle_visibility.triggered.connect(menu.on_toggle_visibility_clicked)
        menu.exec_(self.test_button.mapToGlobal(pos))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 테스트 윈도우 실행
    window = TestWindow()
    window.show()

    sys.exit(app.exec_())