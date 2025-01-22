from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from models.goal import MakeNode, set_deleted_true
from db.db import get_collection

tag_collection = get_collection("Tags")
collection = get_collection()

class EndNode(QWidget):
    def __init__(self, node, update_callback = None):
        super().__init__()
        self.node = node
        self.update_callback = update_callback
        self.setFocusPolicy(Qt.StrongFocus)  # 위젯이 포커스를 받을 수 있게 설정
        self.setFocus()  
        self.is_selected = False 
        
        # 노드 데이터에서 필요한 정보 추출
        title = node.get("title", "Untitled")
        start_time = node.get("start_time", "N/A")
        end_time = node.get("end_time", "N/A")

        # 외곽 프레임 생성
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            background-color: #f0f0f0;  /* 연한 회색 배경 */
            border: 2px solid black;    /* 검은 테두리 */
            border-radius: 5px;         /* 약간 둥근 모서리 */
        """)
        frame_layout = QVBoxLayout(self.frame)

        # 제목과 날짜를 같은 라벨에 표시
        combined_label = QLabel(f"<b>{title}</b><br>{start_time} ~ {end_time}", self.frame)
        combined_label.setFont(QFont("Arial", 12))  # 글씨 크기를 줄임
        combined_label.setAlignment(Qt.AlignCenter)
        combined_label.setStyleSheet("color: black;")  # 텍스트 색상 검은색으로 설정
        frame_layout.addWidget(combined_label)

        # 프레임 레이아웃 설정
        frame_layout.setContentsMargins(10, 5, 10, 5)  # 최소한의 내부 여백

        # 최상위 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.addWidget(self.frame)
        layout.setContentsMargins(0, 0, 0, 0)
        # 크기 조정
        self.setFixedSize(200, 80)  # 크기를 최대한 줄임
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.setSelected(self.is_selected)  # 선택 상태 반영
            print(f"Node clicked: {self.node['title']} - Selected: {self.is_selected}")
            event.accept()
    
    def update_selection_style(self):
        # task 상태에 따라 스타일을 설정합니다.
        if self.node["task"] == [1, 0, 0]:  # 흰색
            style = "background-color: white; border: 2px solid black; border-radius: 5px;"
        elif self.node["task"] == [0, 1, 0]:  # 초록색
            style = "background-color: green; border: 2px solid green; border-radius: 5px;"
        elif self.node["task"] == [0, 0, 1]:  # 빨간색
            style = "background-color: red; border: 2px solid red; border-radius: 5px;"
        else:
            style = "background-color: #f0f0f0; border: 2px solid black; border-radius: 5px;"  # 기본 상태

        print(f"Applying style: {style}")
        self.frame.setStyleSheet(style)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            if self.is_selected:
                print(f"Deleting node: {self.node['title']} with ID: {self.node['_id']}")
                set_deleted_true(self.node["_id"])
                if self.update_callback:
                    self.update_callback()
            else:
                print("nope")
        elif event.key() == Qt.Key_Return:
            print(f"Updating task for node: {self.node['title']}")
            
            # task 값 순환 [1, 0, 0] -> [0, 1, 0] -> [0, 0, 1]
            if self.node["task"] == [1, 0, 0]:
                self.node["task"] = [0, 1, 0]
            elif self.node["task"] == [0, 1, 0]:
                self.node["task"] = [0, 0, 1]
            else:
                self.node["task"] = [1, 0, 0]
            
            # 데이터베이스 업데이트
            collection.update_one(
                {"_id": self.node["_id"]},
                {"$set": {"task": self.node["task"]}}
            )
            print("ok good")
            
            # 스타일 업데이트
            self.update_selection_style()
        else:
            super().keyPressEvent(event)

    def setSelected(self, selected):
        self.is_selected = selected
        self.frame.setStyleSheet("border: 2px solid blue;") if selected else self.frame.setStyleSheet("border: 2px solid black;")


    def mouseReleaseEvent(self, event):
        selected_items = self.table.selectedItems()
        selected_nodes = [item.data(Qt.UserRole) for item in selected_items]  # QTableWidgetItem에서 'node' 데이터 추출
        
        print(f"Selected items after drag: {[node for node in selected_nodes]}")   
if __name__ == "__main__":
    import sys

    # PyQt5 애플리케이션 생성
    app = QApplication(sys.argv)

    # 테스트 노드 데이터
    node_data = {
        "title": "Compact Box",
        "start_time": "2025-01-30 10:00",
        "end_time": "2025-01-30 11:00"
    }

    # 메인 윈도우 생성
    main_window = QWidget()
    main_window.setWindowTitle("Test")
    main_window.resize(200, 80)

    # 레이아웃 생성
    layout = QVBoxLayout()

    # EndNode 추가
    end_node = EndNode(node_data)
    layout.addWidget(end_node)

    # 레이아웃을 메인 윈도우에 설정
    main_window.setLayout(layout)
    main_window.show()

    # 이벤트 루프 실행
    sys.exit(app.exec_())