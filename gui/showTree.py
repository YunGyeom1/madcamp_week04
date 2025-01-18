# showTree.py
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainter
from bson.objectid import ObjectId  # MongoDB ObjectId를 사용하기 위한 임포트
from gui.interactions import InteractiveNode
from models.goal import collection
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import sys

class TreeWidget(QWidget):
    def __init__(self, root_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_id = root_id

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

    def fetch_node_data(self, node_id):
        """MongoDB에서 노드 데이터를 가져옴."""
        return collection.find_one({"_id": ObjectId(node_id)})

    def place_node(self, node_id, x, y):
        node = self.fetch_node_data(node_id)
        # 현재 노드 시각화
        vnode = InteractiveNode(node, self.update_tree)
        x = 800 - node["height"] * 200
        vnode.setPos(x, y)  # x, y 위치 설정
        self.scene.addItem(vnode)

        children = node.get("children", [])

        dy = 0  # 기본 세로 간격
        if node["start_time"] or node["end_time"]: return
        for i, child_id in enumerate(children):
            child_node = self.fetch_node_data(child_id)
            y += dy  # y 위치는 부모 아래로 간격 유지
            x = 800 - child_node["height"] * 200
            self.place_node(child_id, x, y)
            self.add_edge(vnode.pos(), QPointF(x, y))

            dy += child_node["width"] * 100  # 자식 노드 간 고정된 세로 간격
            print(child_node["title"], child_node["width"])

        
    def add_edge(self, parent_pos, child_pos):
        parent = QPointF(parent_pos.x() + 75, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        child = QPointF(child_pos.x(), child_pos.y() + 15)  # y 간격 감소

        if parent.y() == child.y():
            line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.red, 2))
            self.scene.addItem(line)
            return

        if parent.x() == child.x():
            line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.red, 2))
            self.scene.addItem(line)
            return

        # 수평, 수직, 수평 선분의 중간 좌표 계산
        mid = QPointF(parent_pos.x() + 100, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        # 첫 번째 수평 직선
        line1 = QGraphicsLineItem(mid.x(), mid.y(), mid.x(), child.y())
        line1.setPen(QPen(Qt.red, 2))
        self.scene.addItem(line1)

        # 수직 직선
        line2 = QGraphicsLineItem(mid.x(), child.y(), child.x(), child.y())
        line2.setPen(QPen(Qt.red, 2))
        self.scene.addItem(line2)

    def update_tree(self):
        """트리를 다시 렌더링."""
        self.scene.clear()
        self.place_node(self.root_id, 100, 100)