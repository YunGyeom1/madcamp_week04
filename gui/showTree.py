#showTree.py
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItemGroup, QGraphicsLineItem, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QPainter
import sys
from models.goal import GoalNode
from gui.interactions import InteractiveNode


class TreeWidget(QWidget):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root

        # 레이아웃 설정
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # 그래픽 장면 및 뷰 설정
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.view)

        # 트리 렌더링
        self.update_tree()

    def add_edge(self, parent_pos, child_pos):
        parent = QPointF(parent_pos.x() + 75, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        child = QPointF(child_pos.x(), child_pos.y() + 15)  # y 간격 감소

        if parent.y() == child.y():
            line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            return

        if parent.x() == child.x():
            line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(line)
            return

        # 수평, 수직, 수평 선분의 중간 좌표 계산
        mid = QPointF(parent_pos.x() + 100, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        # 첫 번째 수평 직선
        line1 = QGraphicsLineItem(mid.x(), mid.y(), mid.x(), child.y())
        line1.setPen(QPen(Qt.black, 2))
        self.scene.addItem(line1)

        # 수직 직선
        line2 = QGraphicsLineItem(mid.x(), child.y(), child.x(), child.y())
        line2.setPen(QPen(Qt.black, 2))
        self.scene.addItem(line2)
    
    def place_node(self, node, x, y):
        vnode = InteractiveNode(node, self.update_tree)
        vnode.setPos(400 - 200 * node.height, y)  # x 간격 증가
        self.scene.addItem(vnode)

        dy = 0  # 세로 간격 감소
        for ch in node.children:
            child_x = 400 - 200 * ch.height  # x 간격 증가
            child_y = y + dy  # y 간격 감소
            self.place_node(ch, child_x, child_y)
            self.add_edge(vnode.pos(), QPointF(child_x, child_y))
            dy += ch.width * 100  # 하위 노드 간 간격 조정

        vnode.node = node
        node.vnode = vnode
    
    def update_tree(self):
        self.scene.clear()
        self.place_node(self.root, 100, 100)

    def mouseReleaseEvent(self, event):
        # 드래그 종료 상태 확인
        if hasattr(self, "isDragging") and self.isDragging:
            self.isDragging = False
            if event.button() == Qt.RightButton:  # 오른쪽 버튼으로 드래그 종료 시 복제
                if self.scene():  # 현재 장면이 유효한 경우
                    new_node = InteractiveNode(self.node, self.update_callback)
                    new_node.setPos(self.pos() + QPointF(30, 30))  # 약간 다른 위치로 복제
                    self.scene().addItem(new_node)
                    print(f"Copied node: {self.node.title}")

        # 부모 클래스 메서드 호출 전에 유효성 확인
        if self.scene():
            super().mouseReleaseEvent(event)

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

    # 샘플 트리 생성
    root_node = create_sample_tree()

    # TreeWidget 인스턴스 생성 및 테스트
    tree_widget = TreeWidget(root_node)
    tree_widget.setWindowTitle("TreeWidget Test")
    tree_widget.setGeometry(100, 100, 800, 600)
    tree_widget.show()

    sys.exit(app.exec_())