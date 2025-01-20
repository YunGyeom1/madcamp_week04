from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout


class EndNode(QWidget):
    def __init__(self, node, parent=None):
        super().__init__(parent)

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
    main_window.setWindowTitle("EndNode Test")
    main_window.resize(200, 80)

    # 레이아웃 생성
    layout = QVBoxLayout()

    # EndNode 추가
    end_node = EndNode(node=node_data)
    layout.addWidget(end_node)

    # 레이아웃을 메인 윈도우에 설정
    main_window.setLayout(layout)
    main_window.show()

    # 이벤트 루프 실행
    sys.exit(app.exec_())