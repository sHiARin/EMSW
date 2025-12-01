from PySide6.QtWidgets import (
    QApplication, QWidget,
    QListWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QScrollArea
)
from PySide6.QtCore import Qt, QTimer
import sys


class ChatWidget(QWidget):
    """
    다른 프로그램의 레이아웃에 embed 해서 쓸 수 있는
    DM 스타일 채팅 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("ChatWidget")
        self.resize(900, 600)

        # 메인 레이아웃 (좌: 리스트, 우: 채팅창)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 왼쪽: DM 리스트 영역 =====
        self.thread_list = QListWidget()
        self.thread_list.setFixedWidth(250)
        self.thread_list.addItem("Friend #1")
        self.thread_list.addItem("Friend #2")
        self.thread_list.addItem("System Echo Bot")

        self.thread_list.setStyleSheet("""
            QListWidget {
                border-right: 1px solid #cccccc;
                background: #f5f5f5;
            }
        """)

        # ===== 오른쪽: 채팅 영역 =====
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # --- 상단 헤더 ---
        self.header_label = QLabel("System Echo Bot")
        self.header_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.header_label.setFixedHeight(50)
        self.header_label.setStyleSheet("""
            QLabel {
                padding-left: 16px;
                font-size: 16px;
                font-weight: bold;
                border-bottom: 1px solid #cccccc;
                background: #ffffff;
            }
        """)
        chat_layout.addWidget(self.header_label)

        # --- 메시지 스크롤 영역 ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()  # 맨 아래쪽 정렬용 스페이서

        self.scroll_area.setWidget(self.messages_container)
        chat_layout.addWidget(self.scroll_area)

        # --- 하단 입력 영역 ---
        input_area = QWidget()
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(8)

        self.message_edit = QLineEdit()
        self.message_edit.setPlaceholderText("메시지를 입력하세요...")
        self.message_edit.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_edit)
        input_layout.addWidget(self.send_button)

        chat_layout.addWidget(input_area)

        # 메인 레이아웃에 좌/우 배치
        main_layout.addWidget(self.thread_list)
        main_layout.addWidget(chat_panel)

        # 기본 안내 메시지
        self.add_message("안녕하세요! 여기는 에코 봇입니다.", is_me=False)
        self.add_message("메시지를 보내면 같은 내용을 다시 돌려줄게요.", is_me=False)

        # 대화방 선택 시 헤더 이름 변경
        self.thread_list.currentItemChanged.connect(self.on_thread_changed)
        self.thread_list.setCurrentRow(2)  # System Echo Bot 선택

    # ----- 대화방 이름 변경 -----
    def on_thread_changed(self, current, previous):
        if current:
            self.header_label.setText(current.text())

    # ----- 메시지 추가 (말풍선) -----
    def add_message(self, text: str, is_me: bool):
        """
        text : 메시지 텍스트
        is_me : 내가 보낸 메시지면 True, 상대방이면 False
        """
        line_widget = QWidget()
        line_layout = QHBoxLayout(line_widget)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(0)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_me:
            # 내 메시지: 오른쪽 정렬 + 파란 말풍선
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #0f8cff;
                    color: white;
                    border-radius: 16px;
                    padding: 8px 12px;
                    max-width: 400px;
                }
            """)
            line_layout.addStretch()
            line_layout.addWidget(bubble)
        else:
            # 상대 메시지: 왼쪽 정렬 + 회색 말풍선
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #e5e5ea;
                    color: black;
                    border-radius: 16px;
                    padding: 8px 12px;
                    max-width: 400px;
                }
            """)
            line_layout.addWidget(bubble)
            line_layout.addStretch()

        # stretch 앞에 삽입해서 아래로 쌓이게
        index = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(index, line_widget)

        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ----- 메시지 전송 + 에코 -----
    def send_message(self):
        text = self.message_edit.text().strip()
        if not text:
            return

        self.add_message(text, is_me=True)
        self.message_edit.clear()

        def echo():
            self.add_message(f"echo: {text}", is_me=False)

        QTimer.singleShot(400, echo)  # 0.4초 후 에코


# 이 파일을 단독 실행할 때만 테스트용으로 띄우기
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ChatWidget()
    w.setWindowTitle("DM 스타일 채팅 (ChatWidget 테스트)")
    w.show()
    sys.exit(app.exec())
