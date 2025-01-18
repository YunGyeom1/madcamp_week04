#sideDate.py
import sys
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from PyQt5.QtCore import QEvent  # 이벤트 필터에서 사용
from PyQt5.QtWidgets import QAbstractScrollArea  # 테이블 크기 조정 정책에 사용


class DateSidebar(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 2, parent)  # 2열 테이블
        self.setHorizontalHeaderLabels(["Content", "Date"])  # 헤더 설정
        self.setColumnWidth(0, 300)  # 첫 번째 열 너비
        self.setColumnWidth(1, 150)  # 두 번째 열 너비
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)  # 내용 크기에 맞게 조정
        self.setVerticalScrollMode(self.ScrollPerPixel)  # 부드러운 스크롤
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.installEventFilter(self)
        self.verticalHeader().setVisible(False)
        self.current_date = QDate.currentDate()  # 현재 날짜
        self.date_range = 30  # 초기 날짜 범위

        self.populate_dates()

    def populate_dates(self):
        """날짜와 내용을 초기화"""
        self.setRowCount(0)  # 기존 데이터 초기화

        for i in range(-self.date_range, self.date_range + 1):
            # 날짜 계산
            date = self.current_date.addDays(i)
            date_text = date.toString("yyyy-MM-dd")

            # 내용 설정
            if date_text == "2025-01-01":
                content_text = "This is the first line.\nThis is the second line."
            else:
                content_text = ""

            # 테이블에 행 추가
            row = self.rowCount()
            self.insertRow(row)

            # 내용 열
            content_item = QTableWidgetItem(content_text)
            content_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setItem(row, 0, content_item)

            # 날짜 열
            date_item = QTableWidgetItem(date_text)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, date_item)

        self.resizeRowsToContents()  # 행 높이 자동 조정

    def load_more_dates(self, amount):
        """스크롤 시 더 많은 날짜를 로드"""
        new_range = self.date_range + amount
        self.date_range = new_range
        self.populate_dates()
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Wheel and source is self.verticalScrollBar():
            if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
                self.load_more_dates(30)  # 스크롤 시 30일 추가 로드
        return super().eventFilter(source, event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Date Sidebar as Table")
        self.setGeometry(100, 100, 500, 600)

        # DateSidebar 추가
        self.sidebar = DateSidebar()

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.sidebar)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())