#interactions.py
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem,
    QGraphicsItemGroup, QGraphicsSimpleTextItem, QInputDialog, QMenu,
    QGraphicsItem, QListWidget, QGraphicsPathItem
)
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QDrag, QPainterPath, QFontDatabase
from PyQt5.QtCore import Qt, QRectF, QPointF, QMimeData, QEventLoop

from models.goal import MakeNode, set_deleted_true
from gui.popupMenu import NodePopupMenu
from db.db import get_collection
from gui.colors import ThemeColors

collection = get_collection()
tag_collection = get_collection("Tags")

class InteractiveNode(QGraphicsItemGroup):
    def __init__(self, node, update_callback):
        super().__init__()
        self.node = node  # MongoDB 데이터
        self.node_id = node["_id"]
        self.update_callback = update_callback
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setFocus()  # 필요시 포커스 설정
        self.update_sidebar = None
        self.update_filter = None

        # 색상 읽기 (기본값: 흰색)
        node_color = self.node.get("color", "#FFFFFF")  # HEX 색상 코드

        # 노드 배경
        self.background = QGraphicsRectItem(0, 0, 200, 80)
        rounded_path = QPainterPath()
        rounded_path.addRoundedRect(0, 0, 200, 80, 8, 8)  # 반지름을 8로 설정한 둥근 직사각형
        self.background = QGraphicsPathItem(rounded_path)
        self.background.setBrush(QBrush(QColor(node_color)))  # 배경색 빨간색
        self.background.setPen(QPen(Qt.NoPen))  # 테두리 없음
        self.background.setZValue(-1)
        self.addToGroup(self.background)

        # 상태 표시
        self.status_indicator = QGraphicsEllipseItem(10, 30, 20, 20)
        self.status_indicator.setBrush(QBrush(Qt.red))
        self.status_indicator.setPen(QPen(Qt.NoPen))
        self.addToGroup(self.status_indicator)

        # 제목 텍스트
        self.title_text = QGraphicsSimpleTextItem(self.node["title"][:min(15, len(self.node["title"]))])
        self.title_text.setPos(40, 10)
        self.addToGroup(self.title_text)

        # "+" 버튼
        self.plus_button = QGraphicsEllipseItem(160, 13, 30, 30)
        self.plus_button.setBrush(QBrush(Qt.white))
        self.plus_button.setPen(QPen(Qt.NoPen))
        self.addToGroup(self.plus_button)

        # "+" 텍스트
        self.plus_text = QGraphicsSimpleTextItem("+")
        self.plus_text.setFont(QFont("Arial", 14, QFont.Bold))
        self.plus_text.setPos(167, 13)
        self.plus_text.setParentItem(self.plus_button)
        
        # "..." 버튼
        self.menu_button = QGraphicsEllipseItem(125, 13, 30, 30)
        self.menu_button.setBrush(QBrush(Qt.white))
        self.menu_button.setPen(QPen(Qt.NoPen))
        self.addToGroup(self.menu_button)

        # "..." 텍스트
        self.menu_text = QGraphicsSimpleTextItem("...")
        self.menu_text.setFont(QFont("Arial", 14, QFont.Bold))
        self.menu_text.setPos(128, 5)
        self.menu_text.setParentItem(self.menu_button)
        # 시작 시간 표시
        self.start_time_text = QGraphicsSimpleTextItem(self.node.get("start_time", "Not Set"))
        font_id = QFontDatabase.addApplicationFont("assets/제주고딕(윈도우).ttf")

        print("FontID", font_id)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.start_time_text.setFont(QFont(font_family, 10))
        self.start_time_text.setPos(40, 50)
        self.addToGroup(self.start_time_text)

        # 종료 시간 표시
        self.end_time_text = QGraphicsSimpleTextItem(self.node.get("end_time", "Not Set"))
        self.end_time_text.setFont(QFont(font_family, 10))
        self.end_time_text.setPos(100, 50)
        self.addToGroup(self.end_time_text)
        self.popup_menu = None
        tags = self.node["tag"]
        existing_tags = {tag["name"] for tag in tag_collection.find({}, {"name": 1})}
        new_tags = set(tags) - existing_tags
        if new_tags:
            tag_collection.insert_many([{"name": t, "selected": False} for t in new_tags])
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            set_deleted_true(self.node["_id"])
            if self.update_callback:
                self.update_callback()
        elif event.key() == Qt.Key_Return:  # 엔터 키를 눌렀을 때
            # + 버튼 클릭과 동일하게 자식 노드 추가
            new_child_id = MakeNode(f"Child of {self.node['title']}", self.node["_id"])
            self.node["children"].append(new_child_id)

            new_title, ok = QInputDialog.getText(self.scene().views()[0], "자식 노드 제목 변경", "새 제목을 입력하세요:", text=f"Child of {self.node['title']}")
        
            if ok and new_title:
                # 새 제목을 자식 노드에 적용
                collection.update_one({"_id": new_child_id}, {"$set": {"title": new_title}})
                if self.update_callback:
                    self.update_callback()

            if self.update_callback:
                self.update_callback()
        else:
            super().keyPressEvent(event)
    def reset_popup_menu(self):
        self.popup_menu = None
        self.set_active(False)
        self.scene().clearSelection()  # 선택 상태 초기화

    def set_active(self, active):
        self.selected = active

    def mousePressEvent(self, event):
        self.scene().clearSelection()  # 선택 상태 초기화
        self.setSelected(True)
        print(f"Mouse pressed on node: {self.node['_id']}, Popup active: {self.popup_menu is not None}")
        event.accept()
        super().mousePressEvent(event)
        if self.popup_menu:
            print("Closing popup menu...")
            self.popup_menu.close()
            self.popup_menu = None
    
        try:
            super().mousePressEvent(event)
            if event.button() == Qt.LeftButton:
                self.setSelected(True) 
            if self.plus_button.contains(self.mapFromScene(event.scenePos())):
                # + 버튼 클릭: 새 자식 노드 추가
                
                new_child_id = MakeNode(f"Child of {self.node['title']}", self.node["_id"])
                # 데이터 갱신
                self.node["children"].append(new_child_id)

                # QInputDialog 생성
                input_dialog = QInputDialog(self.scene().views()[0])
                input_dialog.setWindowTitle("자식 노드 제목 변경")
                input_dialog.setLabelText("새 제목을 입력하세요:")
                input_dialog.setTextValue(f"Child of {self.node['title']}")

                # 스타일 설정
                input_dialog.setStyleSheet("""
                    QDialog {
                        background-color: white;
                    }
                    QLabel {
                        color: black;
                    }
                    QLineEdit {
                        background-color: #f5f5f5;
                        border: 1px solid #ccc;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """)

                # QInputDialog 실행
                if input_dialog.exec_() == QInputDialog.Accepted:
                    new_title = input_dialog.textValue()

                    if new_title:
                        # 새 제목을 자식 노드에 적용
                        collection.update_one({"_id": new_child_id}, {"$set": {"title": new_title}})
                        if self.update_callback:
                            self.update_callback()

                elif self.menu_button.contains(self.mapFromScene(event.scenePos())):
                    self.show_popup()
                else:
                    
                    # 기본 드래그 시작
                    view = self.scene().views()[0]  # 첫 번째 뷰 가져오기
                    drag = QDrag(view)
                    mime_data = QMimeData()
                    mime_data.setData("application/x-node-id", str(self.node["_id"]).encode("utf-8"))
                    mime_data.setText(self.node["title"])
                    drag.setMimeData(mime_data)
                    drag.exec_(Qt.MoveAction)
            elif self.menu_button.contains(self.mapFromScene(event.scenePos())):
                # ... 버튼 클릭: 기존 팝업 닫기
                # if self.popup_menu:
                #     self.popup_menu.close()  # 기존 팝업 닫기
                #     self.popup_menu = None   # 참조 제거


            
                # 새로운 팝업 메뉴 표시
                self.popup_menu = NodePopupMenu(node_id=self.node["_id"], update_callback=self.update_callback, update_callback2=self.update_sidebar)
                self.popup_menu.update_filter = self.update_filter
                self.popup_menu.popup_closed.connect(self.reset_popup_menu)
                self.popup_menu.show()
                self.popup_menu.exec_()
                self.set_active(True)
            else:
                # if not self.node.get("start_time"):
                #     return

                # 기본 드래그 시작
                view = self.scene().views()[0]  # 첫 번째 뷰 가져오기
                drag = QDrag(view)
                mime_data = QMimeData()
                mime_data.setData("application/x-node-id", str(self.node["_id"]).encode("utf-8"))
                mime_data.setText(self.node["title"])
                drag.setMimeData(mime_data)
                drag.exec_(Qt.MoveAction)
                
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")

    def mouseDoubleClickEvent(self, event):
        """노드를 더블 클릭하면 제목을 변경할 수 있게 한다."""
        try:
            # QInputDialog 생성
            input_dialog = QInputDialog(self.scene().views()[0])
            input_dialog.setWindowTitle("노드 제목 변경")
            input_dialog.setLabelText("새 제목을 입력하세요:")
            input_dialog.setTextValue(self.node["title"])

            # 배경을 흰색으로 설정
            input_dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: black;
                }
                QLineEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)

            # QInputDialog 실행
            if input_dialog.exec_() == QInputDialog.Accepted:
                new_title = input_dialog.textValue()

                if new_title:
                    self.node["title"] = new_title  # MongoDB 데이터 업데이트
                    self.title_text.setText(new_title)  # 화면에 표시된 제목 업데이트

                    # MongoDB 업데이트
                    collection.update_one({"_id": self.node["_id"]}, {"$set": {"title": new_title}})

                    if self.update_callback:
                        self.update_callback()


        except Exception as e:
            print(f"Error in mouseDoubleClickEvent: {e}")

    def mouseMoveEvent(self, event):
        if hasattr(self, "isDragging") and self.isDragging:
            new_pos = self.mapToScene(event.pos()) - self.mapToScene(event.buttonDownPos(Qt.LeftButton))
            self.setPos(self.original_pos + new_pos)

    def show_popup(self):
        """Pop-up 메뉴를 표시"""
        # 기존 팝업이 있으면 닫기
        if self.popup_menu:
            self.popup_menu.close()
        
        # 새로운 팝업 메뉴 인스턴스 생성
        self.popup_menu = NodePopupMenu(node_id=self.node_id)
        

        self.popup_menu.show()  # show()로 팝업 메뉴를 열기