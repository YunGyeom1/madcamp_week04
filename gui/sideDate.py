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
        self.setAcceptDrops(True) 

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

    def dragMoveEvent(self, event):
        print("Drag Move Event Triggered")  # 디버깅
        if event.mimeData().hasFormat("application/x-node-id"):
            print("Dragging over valid drop area.")  # 디버깅
            event.acceptProposedAction()
        else:
            print("Dragging over invalid drop area.")  # 디버깅
            event.ignore()
    def dropEvent(self, event):
        print("Drop Event Triggered")  # 디버깅: 드롭 이벤트 발생
        if event.mimeData().hasFormat("application/x-node-id"):
            print("Valid MIME data format detected.")  # 디버깅: 올바른 데이터 형식
            try:
                # 드래그된 데이터 추출
                node_id = event.mimeData().data("application/x-node-id").data().decode("utf-8")
                node_title = event.mimeData().text()

                print(f"Extracted Node ID: {node_id}, Title: {node_title}")  # 디버깅: 데이터 추출 확인

                # 테이블에 새로운 행 추가
                row = self.rowCount()
                self.insertRow(row)
                print(f"Adding row {row} to the table.")  # 디버깅: 행 추가 확인

                # 내용 추가 (노드 제목)
                content_item = QTableWidgetItem(node_title)
                content_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.setItem(row, 0, content_item)
                print(f"Set content for row {row}, column 0: {node_title}")  # 디버깅: 콘텐츠 추가 확인

                # 날짜 추가 (현재 날짜 사용)
                date_item = QTableWidgetItem(self.current_date.toString("yyyy-MM-dd"))
                date_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 1, date_item)
                print(f"Set date for row {row}, column 1: {self.current_date.toString('yyyy-MM-dd')}")  # 디버깅: 날짜 추가 확인

                # 드롭 완료 메시지
                print(f"Dropped Node ID: {node_id}, Title: {node_title}")
                event.acceptProposedAction()
            except Exception as e:
                print(f"Error during dropEvent: {e}")  # 디버깅: 오류 출력
                event.ignore()
        else:
            print("Invalid MIME data format.")  # 디버깅: 잘못된 데이터 형식
            event.ignore()