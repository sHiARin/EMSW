from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import (Signal, Qt, QSize)
from PySide6.QtGui import (QColor, QFont)

from Config.config import ProgrameAction, AI_Perusona
from EMSW_UI.core.LLM_Connector import Create_AI
from EMSW_UI.core.resource import GlobalSignalHub

import os

class ChatBubble(QLabel):
    """말풍선 하나를 그리는 위젯"""
    def __init__(self, text, is_sender=False):
        super().__init__(text)
        self.setWordWrap(True)  # 긴 텍스트 줄바꿈
        self.setMaximumWidth(300)  # 말풍선 최대 너비 제한
        self.setFont(QFont("Arial", 11))
        self.setTextInteractionFlags(Qt.TextSelectableByMouse) # 텍스트 복사 가능하게
        
        # 패딩 설정
        self.setContentsMargins(15, 10, 15, 10)

        # 스타일시트 설정 (CSS와 유사)
        if is_sender:
            # 내가 보낸 메시지 (오른쪽, 노란색)
            self.setStyleSheet("""
                QLabel {
                    background-color: #FEE500;
                    color: #000000;
                    border-radius: 15px;
                    padding: 10px;
                }
            """)
        else:
            # 상대방 메시지 (왼쪽, 흰색/회색)
            self.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #E0E0E0;
                    border-radius: 15px;
                    padding: 10px;
                }
            """)

class AI_Assistance_Chat(QWidget):
    def __init__(self, ai_perusona:AI_Perusona):
        super().init()
        self.hub = GlobalSignalHub.instance()
        self.perusona = ai_perusona
        self.self_image = {}
        self.update_self_image = []

        self.initUI()
    def check(self):
        c = [self.nameCheck, self.ageCheck, self.sexCheck, self.personalityCheck, self.hobbyCheck, self.TendencyCheck, self.BodyCheck, self.SelfPersonalityCheck, self.SelfTendencyCheck, self.SelfBodyCheck, self.SelfImageCheck]
        for t in c:
            if not t():
                return
    def nameCheck(self):
        if len(self.perusona.get_name()) == 0:
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def ageCheck(self):
        if int(self.perusona.get_age()) < 16:
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def sexCheck(self):
        if 'man' not in self.perusona.get_sex() or 'woman' not in self.perusona.get_sex():
            self.hub.Programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def personalityCheck(self):
        if 0 == len(self.perusona.get_personality()):
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def hobbyCheck(self):
        if 0 == len(self.perusona.get_personality()):
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def TendencyCheck(self):
        if 0 == len(self.perusona.get_Tendency()):
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    def BodyCheck(self):
        if 0 == len(self.perusona.get_body()):
            self.hub.programe_signal.emit(ProgrameAction.RemakeAIPerusona)
            return False
        else:
            return True
    
    def SelfPersonalityCheck(self):
        if 0 == len(self.perusona.get_self_personality()):
            self.update_self_image.append(ProgrameAction.ThinkPersonalityAISelf)
        return True
    def SelfTendencyCheck(self):
        if 0 == len(self.perusona.get_self_tendency()):
            self.update_self_image.append(ProgrameAction.ThinkTendencyAISelf)
        return True
    def SelfBodyCheck(self):
        if 0 == len(self.perusona.get_self_body()):
            self.update_self_image.append(ProgrameAction.ThinkBodyAISelf)
        return True
    def SelfImageCheck(self):
        if 0 == len(self.perusona.get_self_Image()):
            self.update_self_image.append(ProgrameAction.ThinkSelfImageAISelf)
        return True
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. 채팅 영역 (스크롤)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # 스크롤 내부에 들어갈 컨텐츠 컨테이너
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("background-color: #ABC1D1;") # 스크롤 내부 배경색
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop) # 위에서부터 채워지도록 설정
        self.chat_layout.setSpacing(10) # 말풍선 사이 간격

        self.scroll_area.setWidget(self.chat_widget)
        main_layout.addWidget(self.scroll_area)

        # 2. 입력 영역
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #FFFFFF;")
        input_container.setFixedHeight(60)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("메시지를 입력하세요...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
            }
        """)
        self.text_input.returnPressed.connect(self.send_message) # 엔터키 바인딩

        send_btn = QPushButton("전송")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setFixedSize(60, 35)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEE500;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #F2D800;
            }
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.text_input)
        input_layout.addWidget(send_btn)
        
        main_layout.addWidget(input_container)

        # 테스트용 초기 메시지 추가
        self.add_message("안녕하세요! PySide6로 만든 채팅창입니다.", is_sender=False)
        self.add_message("말풍선 레이아웃이 자동으로 조절됩니다.", is_sender=False)

    def send_message(self):
        text = self.text_input.text().strip()
        if text:
            self.add_message(text, is_sender=True)
            self.text_input.clear()
            
            # 1초 뒤 자동 응답 시뮬레이션 (선택 사항)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self.add_message(f"앵무새: {text}", is_sender=False))

    def add_message(self, text, is_sender):
        # 말풍선 위젯 생성
        bubble = ChatBubble(text, is_sender)
        
        # 말풍선 정렬을 위한 가로 레이아웃 (HBox)
        # HBox 안에 [Spacer + Bubble] 또는 [Bubble + Spacer]를 넣어서 좌우 정렬
        row_widget = QWidget()
        row_widget.setStyleSheet("background-color: transparent;") # 투명 배경
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 0, 10, 0) # 좌우 여백

        if is_sender:
            row_layout.addStretch() # 왼쪽에 스프링(여백) 추가 -> 오른쪽 정렬
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch() # 오른쪽에 스프링(여백) 추가 -> 왼쪽 정렬

        # 채팅창 레이아웃에 추가
        self.chat_layout.addWidget(row_widget)
        
        # 스크롤을 최하단으로 이동 (비동기 처리로 UI 렌더링 후 실행)
        QApplication.processEvents() 
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        # 스크롤바의 최대값으로 이동
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())