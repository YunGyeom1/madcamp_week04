#interactions.py
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsSimpleTextItem, QInputDialog, QMenu, QGraphicsTextItem, QGraphicsItem
)
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF
from models.goal import MakeNode
from gui.popupMenu import NodePopupMenu, DateRangeDialog

class InteractiveNode(QGraphicsItemGroup):

    def __init__(self, node, update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node
        self.update_callback = update_callback
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        # 노드 배경 (라운드 사각형)
        self.background = QGraphicsRectItem(0, 0, 200, 80)
        self.background.setBrush(QBrush(Qt.white))
        self.background.setPen(QPen(Qt.black, 2))
        self.background.setZValue(-1)
        self.addToGroup(self.background)

        # 상태 표시 (원형 상태 표시기)
        self.status_indicator = QGraphicsEllipseItem(10, 30, 20, 20)
        self.status_indicator.setBrush(QBrush(Qt.red))
        self.status_indicator.setPen(QPen(Qt.black))
        self.addToGroup(self.status_indicator)

        # 제목 텍스트 (가독성 높은 글꼴)
        self.title_text = QGraphicsSimpleTextItem(node.title)
        self.title_text.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_text.setPos(40, 10)
        self.addToGroup(self.title_text)

        # 하위 텍스트 (작은 설명)
        self.sub_text = QGraphicsSimpleTextItem("달성 기간: 2주")
        self.sub_text.setFont(QFont("Arial", 10))
        self.sub_text.setPos(40, 40)
        self.addToGroup(self.sub_text)

        # "+" 버튼 (노드 오른쪽에 위치)
        self.plus_button = QGraphicsEllipseItem(170, 25, 30, 30)
        self.plus_button.setBrush(QBrush(Qt.lightGray))
        self.plus_button.setPen(QPen(Qt.black))
        self.addToGroup(self.plus_button)

        # "+" 텍스트
        self.plus_text = QGraphicsSimpleTextItem("+")
        self.plus_text.setFont(QFont("Arial", 14, QFont.Bold))
        self.plus_text.setPos(180, 30)
        self.plus_text.setParentItem(self.plus_button)

        self.menu_button = QGraphicsEllipseItem(130, 25, 30, 30)
        self.menu_button.setBrush(QBrush(Qt.lightGray))
        self.menu_button.setPen(QPen(Qt.black))
        self.addToGroup(self.menu_button)

        # "..." 텍스트
        self.menu_text = QGraphicsSimpleTextItem("...")
        self.menu_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.menu_text.setPos(140, 30)
        self.menu_text.setParentItem(self.menu_button)


        self.popupMenu = NodePopupMenu(None)
        self.popupMenu.addAction("설명 변경", lambda: self.popupMenu.on_description_clicked(self.node, self.title_text))
        self.popupMenu.addAction("달성 기간 설정", lambda: self.popupMenu.on_duration_clicked(self.node))
        self.popupMenu.addAction("태그 추가", lambda: self.popupMenu.on_tag_clicked(self.node))
        self.popupMenu.addAction("반복 설정", self.popupMenu.on_repeat_clicked)
        self.popupMenu.addAction("숨기기/보이기 토글", lambda: self.popupMenu.on_toggle_visibility_clicked(self.node))
        
    def mousePressEvent(self, event):
        try:
            print("mousePressEvent called")
            if self.plus_button.contains(self.mapFromScene(event.scenePos())):  # + 버튼 클릭 시 새 자식 노드 추가
                new_child = MakeNode(f"C{len(self.node.children) + 10}")
                self.node.add_child(new_child)
                print(f"Added child node: {new_child.title}")

                # 업데이트 콜백 호출
                if self.update_callback:
                    self.update_callback()
            elif self.menu_button.contains(self.mapFromScene(event.scenePos())):  # ... 버튼 클릭 시 팝업 메뉴 실행
                self.popupMenu.exec_(event.screenPos())
            else:
                # 새 노드 복사본 생성
                self.copied_node = InteractiveNode(self.node, self.update_callback)
                self.copied_node.setPos(self.pos())  # 원본과 같은 위치에 생성
                if self.scene():
                    self.scene().addItem(self.copied_node)
                print(f"Copied node created: {self.node.title}")
                
                # 드래그를 복사된 노드로 시작
                self.copied_node.isDragging = True
                self.copied_node.original_pos = self.copied_node.pos()

        except RuntimeError as e:
            print(f"Error: {e}")

    def mouseMoveEvent(self, event):
        if hasattr(self, 'isDragging') and self.isDragging:  # 드래그 중인 경우
            # 새로운 위치 계산
            new_pos = self.mapToScene(event.pos()) - self.mapToScene(event.buttonDownPos(Qt.LeftButton))
            self.setPos(self.original_pos + new_pos)  # 노드 위치 업데이트
            print(f"Dragging to new position: {self.pos()}")

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'isDragging') and self.isDragging:  # 드래그 종료
            self.isDragging = False
            print(f"Dragging ended at position: {self.pos()}")

        if self.update_callback:  # 업데이트 콜백 호출
            self.update_callback()