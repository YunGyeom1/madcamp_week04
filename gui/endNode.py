from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QInputDialog, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QSizePolicy
from models.goal import MakeNode, set_deleted_true
from db.db import get_collection
from gui.colors import StyleColors

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

        # 색상 읽기 (기본값: 흰색)
        node_color = node.get("color", "#FFFFFF")  # HEX 색상 코드
        print(node_color)

        # 외곽 프레임 생성
        self.frame = QFrame(self)
        self.frame.setStyleSheet(f"""
            background-color: {node_color};  /* 커스텀 색깔 */
            border-radius: 8px;         /* 약간 둥근 모서리 */
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
        #self.setFixedSize(200, 80)  # 크기를 최대한 줄임
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 가로로 확장, 세로는 고정
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.setSelected(self.is_selected)  # 선택 상태 반영
            print(f"Node clicked: {self.node['title']} - Selected: {self.is_selected}")
            event.accept()
    

    def mouseDoubleClickEvent(self, event):
        """더블 클릭하면 시작 시간과 종료 시간을 수정할 수 있게 한다."""
        try:
            start_time = self.node.get("start_time", "N/A")
            end_time = self.node.get("end_time", "N/A")
            # 시작 시간과 종료 시간을 수정할 수 있는 입력 창
            dialog = QDialog(self)
            dialog.setWindowTitle("시간 수정")
        
            # 레이아웃 설정
            layout = QVBoxLayout(dialog)
            form_layout = QFormLayout()

            # 시작 시간 입력
            self.start_time_edit = QLineEdit(dialog)
            self.start_time_edit.setText(start_time)
            form_layout.addRow("시작 시간 (HH:MM):", self.start_time_edit)

            # 종료 시간 입력
            self.end_time_edit = QLineEdit(dialog)
            self.end_time_edit.setText(end_time)
            form_layout.addRow("종료 시간 (HH:MM):", self.end_time_edit)

            layout.addLayout(form_layout)

            # 버튼 설정
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
            layout.addWidget(button_box)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            # 다이얼로그 실행
            if dialog.exec_() == QDialog.Accepted:
                # 사용자가 OK 버튼을 클릭하면 입력된 시간 가져오기
                new_start_time = self.start_time_edit.text()
                new_end_time = self.end_time_edit.text()

                # 시작 시간과 종료 시간을 업데이트
                if new_start_time:
                    self.node["start_time"] = new_start_time
                    collection.update_one({"_id": self.node["_id"]}, {"$set": {"start_time": new_start_time}})

                if new_end_time:
                    self.node["end_time"] = new_end_time
                    collection.update_one({"_id": self.node["_id"]}, {"$set": {"end_time": new_end_time}})

                # UI 업데이트
                if self.update_callback:
                    self.update_callback()
        
        except Exception as e:
            print(f"Error updating times: {e}")


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