from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItemGroup
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt
from models.goal import GoalNode

class InteractiveNode(QGraphicsItemGroup):
    def __init__(self, node, update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node
        self.update_callback = update_callback

        # 노드 모양
        ellipse = QGraphicsEllipseItem(0, 0, 50, 50)
        ellipse.setBrush(QBrush(Qt.yellow))
        ellipse.setPen(QPen(Qt.black))
        self.addToGroup(ellipse)

        # 노드 텍스트
        text = QGraphicsTextItem(f"{node.title}")
        text.setDefaultTextColor(Qt.black)
        text.setPos(10, 10)
        self.addToGroup(text)

    def mousePressEvent(self, event):
        # 클릭 시 새 자식 노드 추가
        new_child = GoalNode(f"C{len(self.node.children) + 10}")
        self.node.add_child(new_child)
        print(f"Added child node: {new_child.title}")

        # 업데이트 콜백 호출
        self.update_callback()