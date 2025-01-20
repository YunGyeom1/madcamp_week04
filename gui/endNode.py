from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from models.goal import MakeNode, set_deleted_true

class EndNode(QWidget):
    def __init__(self, node, update_callback):
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
        frame = QFrame(self)
        frame.setStyleSheet("""
            background-color: #f0f0f0;  /* 연한 회색 배경 */
            border: 2px solid black;    /* 검은 테두리 */
            border-radius: 5px;         /* 약간 둥근 모서리 */
        """)
        frame_layout = QVBoxLayout(frame)

        # 제목과 날짜를 같은 라벨에 표시
        combined_label = QLabel(f"<b>{title}</b><br>{start_time} ~ {end_time}", frame)
        combined_label.setFont(QFont("Arial", 12))  # 글씨 크기를 줄임
        combined_label.setAlignment(Qt.AlignCenter)
        combined_label.setStyleSheet("color: black;")  # 텍스트 색상 검은색으로 설정
        frame_layout.addWidget(combined_label)

        # 프레임 레이아웃 설정
        frame_layout.setContentsMargins(10, 5, 10, 5)  # 최소한의 내부 여백

        # 최상위 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        # 크기 조정
        self.setFixedSize(200, 80)  # 크기를 최대한 줄임
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.update_selection_style()
            print(f"Node clicked: {self.node['title']} - Selected: {self.is_selected}")
            event.accept()
    
    def update_selection_style(self):
        # 클릭 상태에 따라 스타일을 변경
        if self.is_selected:
            self.setStyleSheet("background-color: yellow; border: 2px solid black;")
        else:
            self.setStyleSheet("background-color: #f0f0f0; border: 2px solid black;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            if self.is_selected:
                print(f"Deleting node: {self.node['title']} with ID: {self.node['_id']}")
                set_deleted_true(self.node["_id"])
                if self.update_callback:
                    print("efe")
                    self.update_callback()
            else:
                print("nope")
        else:
            super().keyPressEvent(event)


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