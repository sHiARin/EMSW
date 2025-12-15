from EMSW_UI import *

class ChatController(QObject):
    ai_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.worker = Ollama_Connector()

        self.worker.answer_ready.connect(self.on_answer_ready)
    @Slot(str)
    def on_answer_message(self, name:str, text:str, type:int, model_name:str="gpt-oss:20b", title:str = ''):
        print(7)
        if 0 < type and type < 5 and len(text) == 0:
            self.worker.generate(name, '', type, model_name, title)
        elif 0 < len(text):
            self.worker.generate(name, text, type, model_name, title)
    @Slot(str)
    def on_answer_ready(self, ai_text):
        self.ai_message.emit(ai_text)

class Ollama_Connector(QWidget):
    answer_ready = Signal(str)
    def generate(self, name:str, text:str, type:int, model_name:str, title:str=None):
        print(8)
        try:
            print(f"Generating AI Response... Input: {text[:20]}...")
            GlobalWorld().init_prompt_data()
            if model_name is None:
                GlobalWorld().get_llm('gpt-oss:20b', 0.7)
            else:
                GlobalWorld().get_llm(model_name, 0.7)
            if 0 < len(text):
                b = GlobalWorld().get_last_talk()
                if b is not None  and len(b) >= 2:
                    GlobalWorld().add_prompt(b[0], b[1])

            response_text = GlobalWorld().call_ai(name, text, type, key=title)
            print(f"AI Response Generated: {response_text[:20]}...")
            self.answer_ready.emit(response_text)

            
        except Exception as e:
            print(f"AI Generation Error: {e}")
            self.answer_ready.emit(f"오류가 발생했습니다: {str(e)}")
class EgoSettup(QMainWindow):
    def __init__(self, project:ProjectConfig, name:str):
        super().__init__()
        print('EgoSettup')
        self.project = project
        self.name = name
        self.start()
        self.__init_ui__()
        print('EgoSetup 2')
    def chattingSetUp(self):
        GlobalWorld().create_ai_memory(self.name)
        GlobalWorld().set_persona_data(self.name, self.project.get_persona_dict()[self.name])
        GlobalWorld().init_prompt_data()
        GlobalWorld().get_llm('gpt-oss:20b', 0.7)
    def CreateChattingView(self):
        self.chat_view = ChattingView(self, 1)
        self.chat_view.set_name(self.name)
    def start(self):
        self.chattingSetUp()
        self.CreateChattingView()
    def __init_ui__(self):
        self.move(400, 400)
        self.resize(300, 800)
        self.setWindowTitle(self.name)

        central = QWidget(self)
        vlayout = QVBoxLayout(central)
        vlayout.addWidget(self.chat_view)

        self.setCentralWidget(central)
        self.show()

class ChattingView(QWidget):
    # AI 요청 시그널 (이름, 메시지, 타입)
    request_ai_signal = Signal(str, str, int, object, object)

    # type을 받아서 1이면 초기화(즉 페르소나 설정), 0이면 기본 채팅 모드로 시작한다.
    def __init__(self, parent, type:int):
        super().__init__(parent=parent)
        self.parents = parent
        self.__name = None
        self._footer = ''
        self.type = type
        
        # 설정 모드 플래그 초기화
        self.setSelfBody = False
        self.setSelfPersonality = False
        self.setSelfTendency = False
        self.setSelfImage = False

        self.__init_ollama_chat()
    def __init_ollama_chat(self):
        """AI 통신 스레드 및 컨트롤러 초기화"""
        self.chat_thread = QThread(self)
        self.chatController = ChatController()
        self.chatController.moveToThread(self.chat_thread)
        
        # 시그널 연결
        self.chatController.ai_message.connect(self.addAI_message)
        self.request_ai_signal.connect(self.chatController.on_answer_message)
        
        self.chat_thread.start()

    def name(self):
        return self.__name
    def footer(self):
        return self._footer

    def set_name(self, name: str):
        self.__name = name
        self.__init_ui__()
        self._init_command_config()
    def set_footer(self, footer: str):
        self._footer = footer

    def addAI_message(self, msg: str):
        self._last_ai_message = msg
        self.add_message(msg, False)

    # =========================================================================
    # UI Setup
    # =========================================================================
    def __init_ui__(self):
        """UI 컴포넌트 구성"""
        # 기존 레이아웃 제거 (재설정 시 중복 방지)
        if self.layout():
            QWidget().setLayout(self.layout())

        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # 1. 헤더
        self.header_label = QLabel(f"{self.__name}{self._footer}")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.header_label.setFixedHeight(50)
        self.header_label.setStyleSheet("""
            QLabel {
                padding-left: 16px; font-size: 16px; font-weight: bold;
                border-bottom: 1px solid #cccccc; background: #ffffff;
            }
        """)
        chat_layout.addWidget(self.header_label)

        # 2. 메시지 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        chat_layout.addWidget(self.scroll_area)

        # 3. 입력 영역
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

        self.setLayout(chat_layout)
        
        # 기본 안내 메시지 출력 (type이 1 일때만 호출, type이 0이라면 호출하지 않음)
        if self.type == 1:
            self._print_welcome_message()
        
    def _print_welcome_message(self):
        msgs = [
            f'AI가 {self.name()}에 대한 셀프 이미지를 생성합니다.',
            'show 명령어를 통해 설정된 데이터를 볼 수 있습니다.',
            'set 명령어를 통해 데이터를 설정할 수 있습니다.',
            'help show 또는 help set 명령어로 필요한 명령어를 확인하세요.'
        ]
        for m in msgs:
            self.add_message(m, False)

    # =========================================================================
    # Command & Logic Handling
    # =========================================================================
    def _init_command_config(self):
        """명령어 처리를 위한 설정 데이터 초기화"""
        # 1. 한글 명령어를 영문 키로 매핑
        self.key_map = {
            '이름': 'name', '성별': 'sex', '나이': 'age', '외형': 'body',
            '성격': 'personality', '성향': 'tendency', '취미': 'hobby',
            '자기성격': 'self_personality', '자기성향': 'self_tendency',
            '자기외모': 'self_body', '자기모습': 'self_body', '자아': 'self_image'
        }

        # 2. 'show' 명령어용 데이터 Getter
        p = self.parents.project
        self.data_getters = {
            'name': lambda n: self.name(),
            'age': p.getAge, 'sex': p.getSex, 'body': p.getBody,
            'personality': p.getPersonality, 'hobby': p.getHobby, 'tendency': p.getTendency,
            'self_body': p.getSelfBody, 'self_personality': p.getSelfPersonality,
            'self_tendency': p.getSelfTendency, 'self_image': p.getSelfImage,
        }

        # 3. 'set' 명령어 타겟 및 모드 ID
        self.set_targets = {
            'self_body': 1, 'self_personality': 2, 'self_tendency': 3, 'self_image': 4
        }
        
        # 4. 도움말 텍스트
        self.help_descs = {
            'name': '이름', 'age': '나이', 'sex': '성별',
            'body': '외형', 'personality': '성격', 'hobby': '취미',
            'tendency': '성향', 'self_body': '자기외형',
            'self_personality': '자기성격', 'self_tendency': '자기성향',
            'self_image': '자아'
        }

    def _get_active_mode(self):
        """현재 활성화된 설정 모드 정보 반환"""
        print(2)
        if self.setSelfBody:
            return 'setSelfBody', GlobalWorld().set_ai_persona_self_body, self.parents.project._update_persona_self_body, 1, "정의된 네 외모의 특징과 전체 모습을"
        elif self.setSelfPersonality:
            return 'setSelfPersonality', GlobalWorld().set_ai_persona_self_personality, self.parents.project._update_persona_self_personality, 2, "정의된 내용을 보고 네 성향을"
        elif self.setSelfTendency:
            return 'setSelfTendency', GlobalWorld().set_ai_persona_self_tendency, self.parents.project._update_persona_self_tendency, 3, "정의된 내용을 보고 네 성향을"
        elif self.setSelfImage:
            return 'setSelfImage', GlobalWorld().set_ai_persona_self_image, self.parents.project._update_persona_self_image, 4, "정의된 내용을 보고 네가 본 네 모습을"
        return False

    def command(self, text: list):
        """사용자 입력 처리 메인"""
        print(1)
        if not text:
            return
        active_mode = self._get_active_mode()

        # 1. 설정 모드일 때 처리
        if active_mode:
            print(3)
            self._handle_active_mode(text, active_mode)
        # 2. 일반 대화 시의 처리
        else:
            self._handle_general_command(text)

    def _handle_active_mode(self, text: list, mode_info):
        """설정 모드 중의 로직 처리"""
        print(4)
        flag_name, save_func, local_save, type_id, prompt_topic = mode_info
        
        if 'exit' in text:
            # 모드 종료 및 저장
            setattr(self, flag_name, False)
            last_talk = GlobalWorld().get_last_talk()
            save_func(self.name(), self._last_ai_message)
            local_save(self.name(), self._last_ai_message)
            self.add_message(f"{prompt_topic} 설정을 완료하고 저장했습니다.", False)
        else:
            # AI에게 추가 요청 전송
            print(5)
            user_input = " ".join(text)
            prompt = f"{user_input}을(를) 포함하여 다시 {prompt_topic} 직접 정의하여 설명하라."
            print(6)
            self.request_ai_signal.emit(self.name(), prompt, type_id, "gpt-oss:20b", None)

    def _handle_general_command(self, text: list):
        """show, set, help 등 일반 명령어 처리"""
        cmd = text[0]
        args = text[1:]
        
        if cmd == 'show' and self.type != 0:
            self._cmd_show(args)
        elif cmd == 'set' and self.type != 0:
            self._cmd_set(args)
        elif cmd == 'help' and self.type != 0:
            self._cmd_help(args)
        elif cmd == 'exit' and self.type != 0:
            self.add_message('AI 설정을 종료합니다.', False)
        elif self.type != 0:
            self.add_message("알 수 없는 명령어입니다. 'help'를 입력해보세요.", False)
    # ----- 명령어 상세 구현 -----
    def _cmd_show(self, args):
        print(args)
        if not args:
            self.add_message("확인할 항목을 입력하세요.", False)
            return
        
        key = self.key_map.get(args[0], args[0])
        if key in self.data_getters:
            data = self.data_getters[key](self.name())
            print(data)
            # 데이터 포맷팅
            if isinstance(data, list):
                msg = "\n".join(str(t) for t in data)
            elif isinstance(data, dict):
                msg = "\n".join(f"{k} : {v}" for k, v in data.items())
            else:
                msg = str(data)
            self.add_message(msg, False)
        else:
            self.add_message(f"'{args[0]}'에 대한 정보가 없습니다.", False)

    def _cmd_set(self, args):
        if not args:
            self.add_message("설정할 항목을 입력하세요.", False)
            return
        
        key = self.key_map.get(args[0], args[0])
        if key in self.set_targets:
            type_id = self.set_targets[key]
            # 해당 타입 ID로 초기화 메시지 전송
            self.send_ai_message('', type_id)
        else:
            self.add_message("설정할 수 없는 항목입니다.", False)

    def _cmd_help(self, args):
        if not args:
            self.add_message("사용법: help [show|set]", False)
            return
            
        target = args[0]
        if target == 'show':
            self.add_message("show [항목] : 정보를 확인합니다.", False)
        elif target == 'set':
            self.add_message("set [항목] : 정보를 설정하는 대화를 시작합니다.", False)
        else:
            key = self.key_map.get(target, target)
            desc = self.help_descs.get(key, "도움말이 없습니다.")
            self.add_message(f"{target}: {desc}", False)

    # =========================================================================
    # Messaging Logic
    # =========================================================================
    def send_message(self):
        if self.type == 0:
            text = self.message_edit.text().strip()
            self.add_message(text, is_me=True)
            print(GlobalWorld().get_document_num())
            if not text:
                return
            self.send_ai_message(text, 0, title=self.parents.project.open_document_file_name)
            self.message_edit.clear()
        elif self.type == 1:
            text = self.message_edit.text().strip()
            if not text:
                return
            self.add_message(text, is_me=True)
            self.message_edit.clear()
        else:
            QMessageBox.critical(self, '오류', '알 수 없는 오류가 발생했습니다.', QMessageBox.StandardButton.Ok)
            exit(0)

    def send_ai_message(self, msg: str, t:int = 0, model:str="gpt-oss:20b", title:str = ''):
        """AI에게 메시지 전송 및 모드 진입 설정"""
        # 모드 플래그 설정
        if t == 1: self.setSelfBody = True
        elif t == 2: self.setSelfPersonality = True
        elif t == 3: self.setSelfTendency = True
        elif t == 4: self.setSelfImage = True
        print("send AI Message")
        if 0 == t:
            print(title)
            self.request_ai_signal.emit(self.name(), msg, t, model, title)
        # 유효한 타입인 경우 시그널 전송
        elif 0 < t <= 4 and len(msg) == 0:
            self.request_ai_signal.emit(self.name(), msg, t, model, title)
        elif 0 < len(msg):
            self.request_ai_signal.emit(self.name(), msg, t, model, title)
        else:
            self.add_message('잘못된 입력입니다.', False)

    def add_message(self, text: str, is_me: bool):
        """채팅 말풍선 추가"""
        line_widget = QWidget()
        line_layout = QHBoxLayout(line_widget)
        line_layout.setContentsMargins(0, 0, 0, 0)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # 스타일 설정
        if is_me:
            bubble.setStyleSheet("""
                QLabel { background-color: #0f8cff; color: white; 
                         border-radius: 16px; padding: 8px 12px; max-width: 400px; }
            """)
            line_layout.addStretch()
            line_layout.addWidget(bubble)
        else:
            bubble.setStyleSheet("""
                QLabel { background-color: #e5e5ea; color: black; 
                         border-radius: 16px; padding: 8px 12px; max-width: 400px; }
            """)
            line_layout.addWidget(bubble)
            line_layout.addStretch()

        # 스크롤 영역에 추가
        index = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(index, line_widget)
        
        # 사용자 메시지일 경우 명령어 처리 (중요: 재귀 호출 주의)
        # self.command 호출은 외부에서 add_message를 호출할 때만 발생해야 함.
        if is_me:
            self.command(text.split(' '))
        
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """스크롤 최하단 이동 (안전성 확보)"""
        try:
            if hasattr(self, "scroll_area") and self.scroll_area:
                bar = self.scroll_area.verticalScrollBar()
                if bar:
                    bar.setValue(bar.maximum())
        except RuntimeError:
            pass
    def closeEvent(self, event):
        """창이 닫힐 때 데이터 저장 및 스레드 정리"""
        
        # 진행 중인 AI 작업이 있다면 데이터 저장/마무리
        if hasattr(self, 'chatController'):
            # 만약 컨트롤러에 별도 저장 로직이 있다면 호출
            # self.chatController.save_context() 
            pass

        # ProjectConfig를 통해 파일로 최종 저장 (확실하게 디스크에 쓰기)
        if self.parent and hasattr(self.parent, 'project'):
            print(f"[{self.__name}] 페르소나 데이터 저장 중...")
            self.project.save_project()

        # 스레드 안전하게 종료 (매우 중요: 안 하면 16ms 에러나 Segfault 발생 가능)
        if hasattr(self, 'chat_thread') and self.chat_thread.isRunning():
            self.chat_thread.quit()
            self.chat_thread.wait() # 스레드가 완전히 꺼질 때까지 대기
        super().closeEvent(event)

class MainChattingView(QWidget):
    # ollama와 연결된 AI Chatting Widget
    name_trigger = Signal(str)
    name = Signal(str)
    def __init__(self, parent, project:ProgrameAction):
        super().__init__()
        self.parents = parent
        self.project = project
        self._names = self.project.get_persona_names()
        self.__init_ollama_chat()
        self.__init_ui__()
    def setNames(self, names:list):
        self._names = names
    def names(self):
        return self._names
    def __init_ollama_chat(self):
        """AI 통신 스레드 및 컨트롤러 초기화"""
        self.chat_thread = QThread(self)
        self.chatController = ChatController()
        self.chatController.moveToThread(self.chat_thread)
    def __init_ui__(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === 왼쪽 : make character List ===
        self.thread_list = QListWidget()
        self.thread_list.setFixedWidth(250)

        self.thread_list.setStyleSheet("""
            QListWidget {
                border-right: 1px solid #cccccc;
                background: #f5f5f5;
            }
        """)
        
        for n in self._names:
            self.thread_list.addItem(n)
        
        self.thread_list.setStyleSheet("""
            QListWidget {
                border-right: 1px solid #cccccc;
                background: #f5f5f5;
            }
        """)
        
        # --- 오른쪽 : 채팅 영역

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # --- 채팅 패널
        self.chatpanel = ChattingView(self, 0)
        self.chatpanel.set_name('')
        self.chatpanel.setWindowTitle('')
        right_layout.addWidget(self.chatpanel)

        # --- click event 추가
        self.thread_list.currentItemChanged.connect(self.on_character_clicked_trigger)

        main_layout.addWidget(self.thread_list)
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)
    def on_character_clicked_trigger(self, current, previous):
        if current:
            self.chatpanel.set_name(current.text())
