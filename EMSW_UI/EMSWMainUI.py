from EMSW_UI import *


###
#    프로그램의 메인 뷰
###

class EMSW(QMainWindow):
    def __init__(self, project: ProjectConfig):
        super().__init__()
        self.project = project
        self.project_open = False
        self.dir = None
        self.documentOpened = False
        self.documentEdit = False
        
        # 시그널 허브 설정
        self.hub = GlobalSignalHub.instance()
        self.hub.programe_signal.connect(self._process_action)
        self.hub.message.connect(self._handle_message)

        # 액션 매핑 (Dispatch Table)
        self.action_map = {
            ProgrameAction.ProgrameStart: self._get_activate_window_position,
            ProgrameAction.SetWindowPosition: self._fix_monitor_position,
            ProgrameAction.FixedWindowPosition: self._finish_initialization,
            ProgrameAction.MakeUI: self._run_program,
            ProgrameAction.CreateAIPersona: self._create_persona,
            ProgrameAction.OpenProjectSuccess: self._on_project_opened,
            ProgrameAction.SuccessBaigicSetupAIPersona: self._setup_self_image,
            ProgrameAction.DocumentsOpen: self._document_open_file,
            ProgrameAction.DocumentsEdit: self._document_set_mode,
            ProgrameAction.DocumentsDelete: self._document_delete,
        }

        self.error_map = {
            ProgrameAction.ErrorFileJson: self._show_json_file_error,
        }
        
        # 초기화 시작
        self.hub.programe_signal.emit(ProgrameAction.ProgrameStart)

    # =========================================================================
    # 이벤트 오버라이딩
    # =========================================================================
    def resizeEvent(self, event):
        """창 크기가 변경될 때마다 자동으로 프로젝트 설정 업데이트"""
        self.project.update_scale(self.width(), self.height())
        super().resizeEvent(event)

    def moveEvent(self, event):
        """창 위치가 변경될 때마다 자동으로 프로젝트 설정 업데이트"""
        self.project.update_position(self.x(), self.y())
        super().moveEvent(event)

    # =========================================================================
    # 초기화 로직
    # =========================================================================
    def _process_action(self, signal: ProgrameAction):
        """프로그램 액션 시그널 처리"""
        if signal in self.action_map:
            self.action_map[signal]()
        elif signal in self.error_map:
            self.error_map[signal]()

    def _get_activate_window_position(self):
        self._display_ = Display() 
        self.hub.programe_signal.emit(ProgrameAction.SetWindowPosition)

    def _fix_monitor_position(self):
        """창이 모니터 화면 밖으로 나갔는지 확인하고 보정"""
        over_monitor = False
        x, y = zip([self.x(), self.y()])
        for dis in self._display_:
            x1, x2 = zip([dis['geometry']['x'], dis['geometry']['x'] + dis['geometry']['width']])
            y1, y2 = zip([dis['geometry']['y'], dis['geometry']['y'] + dis['geometry']['height']])
            if x1 < x and x < x2 and y1 < y and y < y2:
                over_monitor = False
            else:
                over_monitor = True
        if over_monitor:
            self.move(100, 100)
        self.hub.programe_signal.emit(ProgrameAction.FixedWindowPosition)

    def _finish_initialization(self):
        self.hub.programe_signal.emit(ProgrameAction.MakeUI)

    def _run_program(self):
        """UI 구성 및 메인 루프 시작"""
        # 초기 윈도우 위치/크기 설정
        data = self.project.program_data()
        self.setGeometry(
            data['windows_pos']['x'], data['windows_pos']['y'],
            data['windows_scale']['width'], data['windows_scale']['height']
        )
        # _init_ui()에 삽입될 view data 설정
        self._horizontal_spliter = QSplitter()
        self._horizontal_spliter.setOrientation(Qt.Orientation.Horizontal)
        self._create_menus()
        self._init_ui()

    def _init_ui(self):
        """메인 위젯 설정"""
        if self.centralWidget():
            self.centralWidget().setParent(None)

        mainboard = QWidget()
        hBoxLayout = QVBoxLayout()
        hBoxLayout.addWidget(self._horizontal_spliter)
        mainboard.setLayout(hBoxLayout) # 메인 레이아웃
        self.setCentralWidget(mainboard)

        self.documentView = DocumentView(self, self.project)
        self._horizontal_spliter.addWidget(self.documentView)
        self.show()

    # =========================================================================
    # 메뉴 설정
    # =========================================================================
    def _create_menus(self):
        mb = self.menuBar()
        self._setup_file_menu(mb.addMenu("파일"))
        self._edit_menu(mb.addMenu("편집"))
        self._setup_character_menu(mb.addMenu("캐릭터"))

    def _add_action(self, menu, text, slot):
        """메뉴 액션 추가 헬퍼 함수"""
        action = QAction(text, self)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _setup_file_menu(self, menu):
        self._add_action(menu, "프로젝트 만들기", self._new_project)
        self._add_action(menu, "프로젝트 열기", self._open_project)
        menu.addSeparator()
        document_group_menu = menu.addMenu("문서")
        self._add_action(document_group_menu, "HWP", self._open_files)
    
    def _edit_menu(self, menu):
        self._add_action(menu, "도큐멘트 편집", self.set_document_edit)
        self._add_action(menu, "도큐멘트 삭제", self._document_delete)
        menu.addSeparator()
        self._add_action(menu, "AI 챗 뷰 추가", self._add_chatting_view)
        self._add_action(menu, "wiki 뷰 추가", self._add_wiki_view)

    def _setup_character_menu(self, menu):
        self._add_action(menu, "새 캐릭터", self._create_persona)
        self._add_action(menu, "캐릭터 편집하기", self._edit_persona)


    # =========================================================================
    # 프로젝트 및 파일 관리
    # =========================================================================
    def _new_project(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "새 프로젝트", "새 프로젝트", "EMSW File(*.emsw)")
        if file_path:
            self.project.new_project_files(file_path)

    def _open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "프로젝트 열기", "", "EMSW File(*.emsw)")
        if file_path:
            directory = "/".join([t for t in file_path.split('/')[0:-1]])
            if '/' not in directory:
                directory = directory + '/'
            name = file_path.split('/')[-1]
            print(directory, name)
            self.project.open_project(directory=directory, name=name)
            
            x, y = self.project.get_position()
            self.move(x, y)
            self.hub.programe_signal.emit(ProgrameAction.OpenProjectSuccess)

    def _on_project_opened(self):
        """프로젝트 열기 성공 시 호출"""
        self.project_open = True
        
        # 윈도우 제목을 현재 열린 프로젝트 이름으로 변경
        if hasattr(self.project, 'project_name'):
            self.setWindowTitle(f"{self.project.project_name} - EMSW")
        # 저장된 창 위치와 크기로 복원
        x, y = self.project.get_position()
        w, h = self.project.get_scale()
        self.setGeometry(x, y, w, h)

        self.documentView.set_names(self.project.get_documents_name())

        # global에서 호출하는 Chatview에 쓰일 패르소나를 업데이트
        self.project.load_global()
    def _document_open_file(self):
        """도큐멘트 열기 성공 시 호출"""
        self.documentView.set_names(self.project.get_documents_name())
    def _handle_message(self, message):
        self.dir = message

    def _show_json_file_error(self):
        QMessageBox.warning(self, '오류', '설정 파일(JSON)에 오류가 발생했습니다.')
    
    def _open_files(self):
        file_path, ok = QFileDialog.getOpenFileName(self, "hwp 파일 열기", "", "HWP File(*.hwp)")
        title = file_path.split('/')[-1]
        if '.hwp' not in file_path:
            self.documentOpened = False
            QMessageBox.critical(self, "경고", "파일 형식이 다릅니다.", QMessageBox.StandardButton.Ok)
            return False
        elif not ok:
            QMessageBox.information(self, "알림", "파일 열기를 취소하셨습니다.")
        else:
            text = hwp_to_txt(file_path)
            replay = QMessageBox.information(self, "로드", "새 그룹을 생성하시겠습니까?", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
            if replay is QMessageBox.StandardButton.Ok:
                name, ok = QInputDialog.getText(self, "새 그룹", "새 그룹")
                if not ok: return False
                if name not in self.project.get_documents_name():
                    self.project.open_document_files(name, title, text)
            else:
                name_list = len(self.project.get_documents_name())
                if name_list == 0:
                    QMessageBox.information(self, "알림", "그룹이 없습니다.", QMessageBox.StandardButton.Ok)
                    return False
                else:
                    name, ok = QInputDialog.getItem(self, '그룹 선택', '그룹 명', self.project.get_documents_name())
                    if ok:
                        if name in self.project.get_documents_name() and title not in self.project.get_documents_title(name):
                            self.project.update_document(name, title, self.project.get_documents_range(name), text=text)
            self.hub.programe_signal.emit(ProgrameAction.DocumentsOpen)
    
    # 페이지의 키워드를 페이지 제목을 sha256 암호화를 통해 겹치지 않게 만듬
    def _encryption_page(self, text:str):
        hash_object = hashlib.sha256()
        hash_object.update(text.encode('utf-8'))
        return hash_object.hexdigest()

    # =========================================================================
    # 레이아웃 편집 로직
    # =========================================================================
    def set_document_edit(self):
        self.documentEdit = not self.documentEdit
        self.hub.programe_signal.emit(ProgrameAction.DocumentsEdit)
    def _document_set_mode(self):
        """Layout 편집 로직, 편집이 가능한 경우에는 자동 저장을 하지 않으며, 편집 가능이 꺼졌을 경우에는 자동 저장이 된다."""
        if self.documentEdit:
            QMessageBox.information(self, "알림", "도큐멘트가 편집 가능하도록 바뀌었습니다.")
            self.documentView.textWidget.setReadOnly(False)
        else:
            QMessageBox.information(self, "알림", "도큐멘트가 편집할 수 없게 바뀌었습니다.")
            self.documentView.saveText()
            self.documentView.textWidget.setReadOnly(True)
    def _document_delete(self):
        n = self.documentView.name()
        p = self.documentView.title_pos()
        self.project.delete_document_name_pos(n, p)
        self.documentView.delete_item()
    # =========================================================================
    # 캐릭터 생성 로직
    # =========================================================================
    def _create_persona(self):
        """캐릭터 생성 프로세스"""
        self.new_ai_config = True
        
        if self._process_profile_creation():
            print('프로파일 설정 완료')
            self.hub.programe_signal.emit(ProgrameAction.SuccessBaigicSetupAIPersona)
        else:
            QMessageBox.information(self, "생성 취소", "캐릭터 생성을 취소하였습니다.")
            self.hub.programe_signal.emit(ProgrameAction.CancleCreateAIPersona)

    def _process_profile_creation(self):
        """
        순차적인 입력 다이얼로그 처리. 
        Early Return을 사용하여 들여쓰기 깊이를 줄임.
        """
        # 1. 이름
        name, ok = QInputDialog.getText(self, '이름 입력', "이름을 입력해 주세요.")
        if not ok or not name: return False
        if len(name) <= 2 or self.project.search_persona_name(name):
            QMessageBox.warning(self, "오류", "이름이 너무 짧거나 이미 존재합니다.")
            return False
        self.project.update_persona_Name(name)

        # 2. 나이
        age, ok = QInputDialog.getInt(self, '나이 입력', '나이를 입력해 주세요:', 0)
        if not ok: return False
        self.project._update_persona_field(name, 'age', age)

        # 3. 성별
        sex, ok = QInputDialog.getItem(self, '성별 선택', '성별을 선택해 주세요:', ['남자', '여자'], 0, False)
        if not ok: return False
        self.project._update_persona_field(name, 'sex', sex)

        # 4. 취미 (파싱 로직 사용)
        hobby_str, ok = QInputDialog.getText(self, '취미 입력', '취미를 입력해 주세요 (, 구분):')
        if not ok: return False
        hobby_data, type_str = self._parse_input_string(hobby_str)
        if not hobby_data: 
            self.project._update_persona_field(name, '취미가 없습니다.', 'str')
        else:
            self.project._update_persona_field(name, 'hobby', hobby_data, type_str)

        # 5. 성격
        pers_str, ok = QInputDialog.getText(self, '성격 입력', '성격을 입력해 주세요 (필수):')
        if not ok or not pers_str: return False
        pers_data, type_str = self._parse_input_string(pers_str)
        self.project._update_persona_field(name, 'personality', pers_data, type_str)

        # 6. 성향
        tend_str, ok = QInputDialog.getText(self, '성향 입력', '성향을 입력해 주세요 (필수):')
        if not ok or not tend_str: return False
        tend_data, type_str = self._parse_input_string(tend_str)
        self.project._update_persona_field(name, 'tendency', tend_data, type_str)

        # 7. 신체 묘사
        body_str, ok = QInputDialog.getText(self, '신체 묘사', '신체를 묘사해 주세요:')
        if not ok: return False
        body_data, type_str = self._parse_input_string(body_str)
        self.project._update_persona_field(name, 'body', body_data, type_str)

        # 저장
        self.project.save_project()
        return True

    def _parse_input_string(self, text: str):
        """
        입력된 문자열을 분석하여 (데이터, 타입문자열) 튜플을 반환
        - 빈 문자열 -> (None, 'str')
        - ',' 포함 -> list 분환 ('list')
        - ':' 포함 -> dict 변환 ('dict')
        - 그 외 -> 그대로 반환 ('str')
        """
        if not text:
            return None, 'str'
        
        if ',' in text:
            items = [t.strip() for t in text.split(',')]
            # 딕셔너리 체크 (key:value 형태인지)
            if ':' in items[0]:
                data_dict = {}
                for item in items:
                    if ':' in item:
                        k, v = item.split(':', 1)
                        data_dict[k.strip()] = v.strip()
                return data_dict, 'dict'
            else:
                return items, 'list'
        
        return text, 'str'

    def _setup_self_image(self):
        print('Setup Self Image...')
    def _edit_persona(self):
        self.edit_view = PersonaSettingWindow(self, self.project)
        self.edit_view.show()
    
    # =========================================================================
    # 뷰 생성 로직
    # =========================================================================
    def _add_chatting_view(self):
        if not self._persona_key_check():
            return False
        self.append_chatting_view()
    def _persona_key_check(self):
        personalist = []
        names = GlobalWorld().get_ai_names()
        if len(names) == 0:
            replay = QMessageBox.information(self, '알림', '생성된 캐릭터가 없습니다. \n 캐릭터를 생성하시겠습니까?', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if replay == QMessageBox.StandardButton.Ok:
                if hasattr(self, '_create_persona'):
                    self._create_persona()
                return False
            else:
                return False
        required_keys = GlobalWorld.PERSONA_KEYS if hasattr(GlobalWorld, 'PERSONA_KEYS') else [
            'age', 'sex', 'personality', 'hobby', 'tendency', 'body', 
            'self_body', 'self_personality', 'self_tendency', 'self_image'
        ]
        for n in names:
            if GlobalWorld().check_persona_integrity(n, required_keys) < 0:
                pass
            else:
                personalist.append(n)
        if (personalist) == 0:
            QMessageBox.information(self, '알림', '유효한 캐릭터가 없습니다.\n 캐릭터는 생성한 뒤, self attention을 위해 self attention 과정을 거쳐야 합니다.')
            return False
        self._persona_list = personalist
        return True
    
    def append_chatting_view(self):
        main_chat_layout = MainChattingView(self, self.project)
        main_chat_layout.setNames(self.project.get_persona_names())
        current_size = self._horizontal_spliter.sizes()
        new_size = sum(current_size) // (len(current_size) + 1) if current_size else 300
        self._horizontal_spliter.addWidget(main_chat_layout)
        self._horizontal_spliter.setSizes([new_size] * self._horizontal_spliter.count())
        self.update()
    
    def _add_wiki_view(self):
        pass
    
    
    """
        close event 오버라이드
        최종 체크 (자동 저장)
    """
    def closeEvent(self, event):
        try:
            self.project.save_project()
        except:
            pass
        super().closeEvent(event)

