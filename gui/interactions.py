#interactions.py
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem,
    QGraphicsItemGroup, QGraphicsSimpleTextItem, QInputDialog, QMenu,
    QGraphicsItem, QListWidget
)
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QDrag
from PyQt5.QtCore import Qt, QRectF, QPointF, QMimeData
from models.goal import MakeNode
from gui.popupMenu import NodePopupMenu, DateRangeDialog

class InteractiveNode(QGraphicsItemGroup):
    def __init__(self, node, update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node  # MongoDB 데이터
        self.update_callback = update_callback
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        # 노드 배경
        self.background = QGraphicsRectItem(0, 0, 200, 80)
        self.background.setBrush(QBrush(Qt.white))
        self.background.setPen(QPen(Qt.black, 2))
        self.background.setZValue(-1)
        self.addToGroup(self.background)

        # 상태 표시
        self.status_indicator = QGraphicsEllipseItem(10, 30, 20, 20)
        self.status_indicator.setBrush(QBrush(Qt.red))
        self.status_indicator.setPen(QPen(Qt.black))
        self.addToGroup(self.status_indicator)

        # 제목 텍스트
        self.title_text = QGraphicsSimpleTextItem(self.node["title"])
        self.title_text.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_text.setPos(40, 10)
        self.addToGroup(self.title_text)

        # "+" 버튼
        self.plus_button = QGraphicsEllipseItem(170, 25, 30, 30)
        self.plus_button.setBrush(QBrush(Qt.lightGray))
        self.plus_button.setPen(QPen(Qt.black))
        self.addToGroup(self.plus_button)

        # "+" 텍스트
        self.plus_text = QGraphicsSimpleTextItem("+")
        self.plus_text.setFont(QFont("Arial", 14, QFont.Bold))
        self.plus_text.setPos(180, 30)
        self.plus_text.setParentItem(self.plus_button)

    def mousePressEvent(self, event):
        try:
            if self.plus_button.contains(self.mapFromScene(event.scenePos())):
                # + 버튼 클릭: 새 자식 노드 추가
                new_child_id = MakeNode(f"Child of {self.node['title']}", self.node["_id"])
                print(f"New child node created with ID: {new_child_id}")
                # 데이터 갱신
                self.node["children"].append(new_child_id)

                if self.update_callback:
                    self.update_callback()
            else:
                # 기본 드래그 시작
                view = self.scene().views()[0]  # 첫 번째 뷰 가져오기
                print("Views: ", self.scene().views())
                for idx, view in enumerate(self.scene().views()):
                    print(f"View {idx}: {view}, Type: {type(view)}")
                drag = QDrag(view)
                mime_data = QMimeData()
                mime_data.setData("application/x-node-id", str(self.node["_id"]).encode("utf-8"))
                mime_data.setText(self.node["title"])
                drag.setMimeData(mime_data)
                print(mime_data)
                drag.exec_(Qt.MoveAction)
                
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event):
        if hasattr(self, "isDragging") and self.isDragging:
            new_pos = self.mapToScene(event.pos()) - self.mapToScene(event.buttonDownPos(Qt.LeftButton))
            self.setPos(self.original_pos + new_pos)
