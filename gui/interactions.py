#interactions.py
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsSimpleTextItem, QInputDialog
)
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRectF
from models.goal import GoalNode
from gui.popupMenu import NodePopupMenu, DateRangeDialog
from PyQt5.QtGui import QFont  # 글꼴 설정을 위해 필요
from PyQt5.QtCore import QPointF  # 위치 계산에 필요
from PyQt5.QtWidgets import QMenu  # PopupMenu 실행을 위해 필요

class InteractiveNode(QGraphicsItemGroup):

    def __init__(self, node, update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node
        self.update_callback = update_callback

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
    
    def mousePressEvent(self, event):
        try:
            if self.plus_button.contains(event.pos()):  # + 버튼 클릭 시 새 자식 노드 추가
                new_child = GoalNode(f"C{len(self.node.children) + 10}")
                self.node.add_child(new_child)
                print(f"Added child node: {new_child.title}")

                # 업데이트 콜백 호출
                if self.update_callback:
                    self.update_callback()
            elif self.menu_button_rect.contains(event.pos()):  # ... 버튼 클릭 시 팝업 메뉴 실행
                self.popupMenu.exec_(event.screenPos())
            else:
                self.isDragging = True  # 드래그 시작
                self.original_pos = self.pos()  # 드래그 시작 위치 저장

            super().mousePressEvent(event)

        except RuntimeError as e:
            print(f"Error: {e}")

    def mouseMoveEvent(self, event):
        if self.isDragging:  # 드래그 중인 경우
            new_pos = self.mapToScene(event.pos()) - self.mapToScene(event.buttonDownPos(Qt.LeftButton))
            self.setPos(self.original_pos + new_pos)  # 새 위치로 이동
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if self.isDragging:  # 드래그 종료
            self.isDragging = False
            if event.button() == Qt.RightButton:  # 오른쪽 버튼으로 드래그 종료 시 노드 복제
                new_node = InteractiveNode(self.node, self.update_callback)
                new_node.setPos(self.pos() + QPointF(30, 30))  # 약간 다른 위치에 복사
                if self.scene():
                    self.scene().addItem(new_node)
                print(f"Copied node: {self.node.title}")
        if self.scene():
            super().mouseReleaseEvent(event)
        if self.update_callback:
            self.update_callback()
        super().mouseReleaseEvent(event)
    
    def on_description_clicked(self):
        """Description 클릭: 노드 제목 변경."""
        new_title, ok = QInputDialog.getText(None, "노드 제목 변경", "새 제목을 입력하세요:", text=self.node.title)
        if ok and new_title:
            self.node.title = new_title
            self.title_text.setText(new_title)
            print(f"노드 제목이 '{new_title}'로 변경되었습니다.")

    def on_duration_clicked(self):
        """달성 기간 설정 클릭: 캘린더로 시작/종료 날짜 설정."""
        dialog = DateRangeDialog()
        if dialog.exec_():  # 사용자가 "확인" 버튼을 클릭하면
            start_date, end_date = dialog.get_dates()
            print(f"달성 기간 설정: 시작={start_date}, 종료={end_date}")
            self.node.start_date = start_date
            self.node.end_date = end_date

    def on_tag_clicked(self):
        """태그 설정 클릭: 노드 태그 추가."""
        new_tag, ok = QInputDialog.getText(None, "태그 추가", "새 태그를 입력하세요:")
        if ok and new_tag:
            if not hasattr(self.node, "tags"):
                self.node.tags = []
            self.node.tags.append(new_tag)
            print(f"태그 '{new_tag}'가 추가되었습니다. 현재 태그: {self.node.tags}")

    def on_repeat_clicked(self):
        """반복 설정 클릭: 추가 구현 필요."""
        print("반복 설정 기능은 아직 구현되지 않았습니다.")

    def on_toggle_visibility_clicked(self):
        """숨기기 토글 클릭: isOpen 상태 변경."""
        self.isOpen = not self.isOpen
        print(f"노드 숨기기 상태가 '{self.isOpen}'로 변경되었습니다.")