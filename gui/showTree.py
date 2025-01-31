from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QEvent
from PyQt5.QtGui import QPen, QPainter, QTransform

from bson.objectid import ObjectId
from models.goal import get_collection, duplicate_node, set_deleted_true
from gui.interactions import InteractiveNode
import os
from dotenv import load_dotenv
import sys

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path = env_path)

tag_collection = get_collection("Tags")
collection = get_collection()


class TreeWidget(QWidget):
    def __init__(self, root_id):
        super().__init__()
        self.root_id = root_id
        self.copied_node_id = None
        self.update_date = None
        self.update_sidebar = None
        self.update_filter = None

        self.setStyleSheet("background-color: #000000;")
        
        # 줌 및 패닝 상태 변수 초기화
        self.zoom_factor = 1.0
        self.is_panning = False
        self.last_mouse_position = QPointF()

        # QGraphicsView 설정
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # 이벤트 필터 추가
        self.view.viewport().installEventFilter(self)

        # 트리 렌더링
        self.update_tree()
        self.view.centerOn(1000, 200)

    def update_tree(self):
        self.scene.clear()
        root = collection.find_one({"_id": self.root_id})
        root_x = 1000-root["height"]*250
        root_y = 100
        print("와우", root_x, root_y)
        self.place_node(root, root_x, root_y)

        self.view.ensureVisible(root_x - 100, root_y - 100, 200, 200)
        if self.update_sidebar:
            self.update_sidebar()
    
    def place_node(self, node, x, y):
        if node["date"] : 
            return # leaf 노드면 더 로닝 ㄴㄴ
        vnode = InteractiveNode(node, self.update_tree)
        vnode.update_sidebar = self.update_sidebar
        vnode.update_filter = self.update_filter
        vnode.setPos(x, y)
        print(node["title"], node["width"], node["height"], x, y, node["tag"])
        self.scene.addItem(vnode)


        selected_tags = [tag["name"] for tag in tag_collection.find({"selected": True})]
        
        dy = 100
        child_x = x
        child_y = y
        for child_id in node["children"]:
            child_node = collection.find_one({"_id": child_id})

            if not any(tag in selected_tags for tag in child_node.get("tag", [])):
                continue
             # "deleted" 태그가 있는 경우 selected 태그에 포함되어 있어야 렌더링
            if "deleted" in child_node.get("tag", []):
                if "deleted" not in selected_tags:
                    continue
            if child_node["date"]:
                continue

            
            child_x = 1000 - child_node["height"] * 250
            if child_node and 'deleted' not in child_node["tag"]:
                self.place_node(child_node, child_x, child_y)
                self.add_edge(vnode.pos(), QPointF(child_x, child_y))
                child_y += child_node["width"] * 100
 
    def add_edge(self, parent_pos, child_pos):
        parent = QPointF(parent_pos.x() + 75, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        child = QPointF(child_pos.x(), child_pos.y() + 15)  # y 간격 감소

        if parent.y() == child.y():
            line = QGraphicsLineItem(parent.x()+125, parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.white, 2))
            self.scene.addItem(line)
            return

        if parent.x() == child.x():
            line = QGraphicsLineItem(parent.x(), parent.y(), child.x(), child.y())
            line.setPen(QPen(Qt.white, 2))
            self.scene.addItem(line)
            return

        # 수평, 수직, 수평 선분의 중간 좌표 계산
        mid = QPointF(parent_pos.x() + 100, parent_pos.y() + 15)  # x 간격 증가, y 간격 감소
        # 첫 번째 수직 직선
        line1 = QGraphicsLineItem(mid.x()+125, mid.y(), mid.x()+125, child.y())
        line1.setPen(QPen(Qt.white, 2))
        self.scene.addItem(line1)

        # 수평 직선
        line2 = QGraphicsLineItem(mid.x()+125, child.y(), child.x(), child.y())
        line2.setPen(QPen(Qt.white, 2))
        self.scene.addItem(line2)

    def zoom_event(self, event):
        """
        마우스 휠로 트리 줌 인/줌 아웃 처리.
        """
        if event.angleDelta().y() > 0:
            # 줌 인
            self.zoom_factor *= 1.03
        else:
            # 줌 아웃
            self.zoom_factor /= 1.03
        
        min_zoom = 0.5
        max_zoom = 7.0

        self.zoom_factor = max(min_zoom, min(self.zoom_factor, max_zoom))

        # 트랜스폼 적용
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

    def eventFilter(self, source, event):
        """
        이벤트 필터: 배경에서만 패닝 동작 처리.
        """
        if event.type() == QEvent.Wheel:  # 마우스 휠 이벤트 처리
            self.zoom_event(event)
            return True 

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # 클릭된 위치가 InteractiveNode 위인지 확인
            items = self.scene.items(self.view.mapToScene(event.pos()))
            if any(isinstance(item, InteractiveNode) for item in items):
                return False  # InteractiveNode가 이벤트를 처리

            # 배경에서 클릭한 경우 패닝 시작
            self.is_panning = True
            self.last_mouse_position = event.pos()
            return True  # 이벤트 소모


        elif event.type() == QEvent.MouseMove and self.is_panning:
            delta = event.pos() - self.last_mouse_position
            self.last_mouse_position = event.pos()

            if not delta.isNull():
                # 트랜스폼 적용된 delta 계산
                transform = self.view.transform()
                scaled_delta = QPointF(delta.x() / transform.m11(), delta.y() / transform.m22())
                
                # 패닝 감도 낮추기 (예: 0.5로 감도 조정)
                sensitivity = 0.5
                scaled_delta *= sensitivity

                # 스크롤바 이동
                self.view.horizontalScrollBar().setValue(
                    int(self.view.horizontalScrollBar().value() - scaled_delta.x())
                )
                self.view.verticalScrollBar().setValue(
                    int(self.view.verticalScrollBar().value() - scaled_delta.y())
                )
            return True

        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            # 패닝 종료
            self.is_panning = False
            return True  # 이벤트 소모

        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_C:  # Ctrl+C
                print("ctrl-c")
                selected_items = self.scene.selectedItems()
                if selected_items:
                    self.copied_node_id = selected_items[0].node["_id"]  # 선택된 노드의 ID를 저장
            elif event.key() == Qt.Key_V:  # Ctrl+V
                print("ctrl-v")
                if self.copied_node_id:
                    selected_items = self.scene.selectedItems()
                    if selected_items:
                        parent_node_id = selected_items[0].node["_id"]  # 부모 노드 ID
                        duplicate_node(parent_node_id, self.copied_node_id)
                    self.update_tree()
        else:
            super().keyPressEvent(event)
