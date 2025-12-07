from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QAbstractItemView,
                               QScrollArea, QInputDialog,
                               QTableWidget, QFrame, QHeaderView,
                               QTableWidgetItem, QListWidget,
                               QSplitter, QTreeView, QTextEdit)
from PySide6.QtGui import (QAction, QStandardItemModel, QStandardItem, QFont)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QModelIndex, QObject, QThread,
                            Slot, QThread)

from shiboken6 import isValid
from helper_hwp import hwp_to_txt
from Config.config import ProgrameAction, ProgrameEventChecker
from EMSW_UI.core.resource import ProjectConfig, Display, GlobalSignalHub, GlobalWorld

import os, copy, hashlib

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
            directory = "/".join(file_path.split('/')[:-1])
            name = file_path.split('/')[-1]
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


class DocumentView(QWidget):
    # 열린 문서를 관리하는 뷰
    def __init__(self, parent, project:ProjectConfig):
        super().__init__(parent=parent)
        self.parents = parent
        self.project = project
        self._names = None
        self._selected_name = None
        self.treeView = QTreeView()
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Documents"])
        self.treeView.setModel(self.model)
        self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeView.clicked.connect(self._on_tree_clicked)

        self.read_files()
        self.__init_ui__()
    # 파일을 읽는 메소드
    def read_files(self):
        try:
            self._names = self.project.get_documents_name()
        except:
            pass
    def set_names(self, names:list):
        self._names = names
        self.make_trees()
    def names(self):
        return self._names
    def name(self):
        return self._selected_name[0]
    def title_pos(self):
        return self._selected_name[1]
    # tree를 만드는 메서드
    def make_trees(self):
        # 중복 방지
        self.model.removeRows(0, self.model.rowCount())
        for n in self.names():
            if 'sample' != n:
                pass
            item = self.make_group_tree(n)
            self.model.appendRow(item)
        if self.model.columnCount() == 0:
            self.model.setRow(0, '없음')
    # tree clicked action
    def _on_tree_clicked(self, index):
        try:
            data = index.parent().data()
            pos = index.column() + 1
            if data is None:
                print('None')
            else:
                text = self.project.get_document_text(data, index.column() + 1)
                self.textWidget.setText(text)
                title = self.project.get_document_title(data, pos)
                GlobalWorld().add_documents(title, text)
                self.project.open_document_file_name = title
        except Exception as e:
            print(f"error : {type(e)}")
            pass
    # 그룹 하위의 문서를 등록하는 매서드
    def make_group_tree(self, name:str):
        item = QStandardItem(name)
        for i, k in enumerate(self.project.get_documents_title(name)):
            if i == 0:
                pass
            else:
                print(name, i)
                t = QStandardItem(self.project.get_document_title(name, i))
                item.appendRow(t)
        return item
    # 편집된 텍스트를 저장
    def saveText(self):
        if self._selected_name is not None:
            self.project.update_document_text(self._selected_name[0], self._selected_name[1], self.textWidget.toPlainText())
    # 삭제 작업 시 treeView에 접근하여 값을 갱신
    def delete_item(self):
        self.make_trees()
    def __init_ui__(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Horizontal)

        # === 왼쪽 : group List ===
        self.make_trees()
        splitter.addWidget(self.treeView)

        # === 오른쪽 : text View ===
        self.textWidget = QTextEdit(self)
        self.textWidget.setReadOnly(True)

        splitter.addWidget(self.textWidget)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

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

class PersonaSettingWindow(QWidget):
    """ persona의 세부 사항을 설정하고 편집하는 동작을 담당하는 위젯"""
    def __init__(self, parent, project):
        super().__init__()
        self.edit_cell = False
        self.edit_list = []
        self.clickedNum = 0
        self.project = project
        self.parents = parent
        
        # 테이블 키 설정
        self.persona_keys = ['name', 'age', 'sex', 'hobby', 'personality', 'tendency', 'body', 'self_body', 'self_personality', 'self_tendency', 'self_image']

        # 윈도우 초기 설정
        window_data = self.project.getPersonaEditing_WindowData()
        self.move(window_data.get('x', 100), window_data.get('y', 100))
        self.resize(window_data.get('w', 800), window_data.get('h', 600))
        self.setWindowTitle("캐릭터 관리")
        self.setStyleSheet("background: #F0F2F5")

        # UI 및 데이터 로드
        self.init_ui()
        self.load_table_data()

    def init_ui(self):
        """UI 레이아웃 및 스타일 설정"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. 상단 헤더 영역 (제목 + 검색 + 버튼)
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel("캐릭터 목록")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; border: none;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이름으로 검색...")
        self.search_input.setStyleSheet("""
            QLineEdit { border: 1px solid #CCC; border-radius: 5px; padding: 5px 10px; background-color: #FAFAFA; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #ABC1D1; }
        """)
        self.search_input.textChanged.connect(self.filter_table) # 검색 기능 연결

        search_btn = QPushButton("검색")
        search_btn.setFixedSize(60, 30)
        self._apply_btn_style(search_btn, "#ABC1D1", "white")
        search_btn.clicked.connect(lambda: self.filter_table(self.search_input.text()))

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setFixedSize(80, 30)
        self._apply_btn_style(refresh_btn, "#FEE500", "#333")
        refresh_btn.clicked.connect(self.load_table_data)

        self.edit_btn = QPushButton("편집")
        self.edit_btn.setFixedSize(60, 30)
        self._apply_btn_style(self.edit_btn, "#00E0F0", "#333")
        self.edit_btn.clicked.connect(self.edit_button)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(search_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(refresh_btn)
        main_layout.addWidget(top_frame)

        # 2. 테이블 위젯 설정
        self.columns = ['이름', '나이', '성별', '취미', '성격', '성향', '외모', '설정']
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        
        # 테이블 옵션
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        # 테이블 스타일
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #DDD; border-radius: 10px; gridline-color: #EEE; font-size: 12px; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F0F0; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #000; }
            QHeaderView::section { background-color: #ABC1D1; color: white; padding: 8px; border: none; font-weight: bold; font-size: 13px; }
        """)
        
        main_layout.addWidget(self.table)

        # 3. 하단 상태바
        status_layout = QHBoxLayout()
        self.count_label = QLabel("총 0개의 항목")
        self.count_label.setStyleSheet("color: #666; font-size: 12px;")
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedSize(80, 30)
        close_btn.setStyleSheet("background-color: #EEE; border-radius: 5px;")
        close_btn.clicked.connect(self.close)

        status_layout.addWidget(self.count_label)
        status_layout.addStretch()
        status_layout.addWidget(close_btn)
        main_layout.addLayout(status_layout)

    def edit_button(self):
        self.edit_cell = not self.edit_cell
        if self.edit_cell:
            self.edit_btn.setText('저장')
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)
            self.table.itemClicked.connect(self._handle_dobule_clicked_)
        else:
            self.edit_btn.setText('편집')
            # 편집 모드 종료
            # 트리거 연결 해제, 오류 우회를 위한 except pass
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            try:
                self.table.itemClicked.disconnect(self._handle_clicked_)
            except:
                pass
            for item in self.edit_list:
                name = self.table.item(item.row(), 0).text()
                content = item.text()
                if item.column() == 0:
                    pass
                elif item.column() < 3:
                    self.project._update_persona_field(name, self.persona_keys[item.column()], content)
                    self.project.save_project()
                else:
                    content, type_str = self.parents._parse_input_string(content)
                    self.project._update_persona_field(name, self.persona_keys[item.column()], content, type_str)
                    self.project.save_project()

    def _handle_dobule_clicked_(self, item):
        self.clickedNum += 1
        self.edit_list.append(item)
        is_save_mode = (self.edit_btn.text() == '저장')
        if not is_save_mode:
            self.table.setItem(item.row(), item.column(), item)
            self.clickedNum = 0

    def load_table_data(self):
        """데이터를 불러와 테이블을 채웁니다."""
        self.table.setRowCount(0) # 초기화
        persona_dict = self.project.get_persona_dict()
        
        for name, data in persona_dict.items():
            if name == 'sample':
                continue
            
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 데이터 포맷팅 및 셀 생성
            # 컬럼 순서: 이름, 나이, 성별, 취미, 성격, 성향, 외모
            cell_values = [
                name,
                str(data.get('age', '')),
                str(data.get('sex', '')),
                self._format_value(data.get('hobby'), '취미가 없습니다.'),
                self._format_value(data.get('personality')),
                self._format_value(data.get('tendency')),
                self._format_value(data.get('body'))
            ]

            # 텍스트 셀 추가
            for col_idx, value in enumerate(cell_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setSelected(False)
                self.table.setItem(row_idx, col_idx, item)

            # 마지막 컬럼: 설정 버튼
            btn = self._create_setup_button(name)
            self.table.setCellWidget(row_idx, len(self.columns)-1, btn)

        # 데이터 로드 후 레이아웃 조정
        self.count_label.setText(f"총 {self.table.rowCount()}개의 항목")
        self._adjust_column_sizes()

    def _format_value(self, value, default_msg=""):
        """데이터 타입(str, list, dict)에 따라 적절한 문자열로 변환합니다."""
        if value is None:
            return default_msg
        
        if isinstance(value, list):
            return '\n'.join([str(t) for t in value])
        elif isinstance(value, dict):
            return '\n'.join([f"{k} : {v}" for k, v in value.items()])
        
        # 문자열이거나 기타 타입
        return str(value)

    def _create_setup_button(self, name):
        """설정 버튼 생성"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button = QPushButton('설정')
        button.setFixedSize(60, 24)
        button.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        button.clicked.connect(lambda: self._open_ego_setup(name))
        
        layout.addWidget(button)
        return container

    def _open_ego_setup(self, name):
        """EgoSetup 창 열기"""
        self.egosetup = EgoSettup(self.project, name)
        # self.egosetup.show() # EgoSettup 내부에서 show()를 호출하지 않는다면 여기서 호출

    def _adjust_column_sizes(self):
        """테이블의 행/열 크기를 내용에 맞게 조정합니다."""
    
        # 열 너비(Width)를 내용에 맞게 자동 조정
        self.table.resizeColumnsToContents()
    
        # 행 높이(Height)를 내용(개행 포함)에 맞게 자동 조정
        self.table.resizeRowsToContents()

        # 행 높이를 내용에 맞게 '고정' (사용자가 마우스로 조절 불가능하게)
        # 내용이 바뀌면 자동으로 늘어나고 줄어듦
        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 특정 항목은 최대 길이를 막어 무한정 불어나는 것을 막습니다.
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 300)

        # 마지막 항목은 btn의 너비(60) 보다 여유있게 설정하여 잘리는 것을 방지하고, Table의 길이를 수정할 수 없도록 변경.
        self.table.setColumnWidth(len(self.columns) - 1, 80)
        self.table.EditTrigger(QAbstractItemView.EditTrigger.NoEditTriggers)

    def filter_table(self, text):
        """검색어에 따라 테이블 행 숨기기/보이기"""
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0) # 0번 컬럼이 이름
            if name_item:
                is_match = text.lower() in name_item.text().lower()
                self.table.setRowHidden(row, not is_match)

    def _apply_btn_style(self, btn, bg_color, text_color):
        """버튼 스타일 적용 헬퍼"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                font-weight: bold; border: none; border-radius: 5px;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
    def closeEvent(self, event):
        self.project.set_Persona_editing_windows_geometry(self.x(), self.y(), self.width(), self.height())
        return super().closeEvent(event)

class ChatController(QObject):
    ai_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.worker = Ollama_Connector()

        self.worker.answer_ready.connect(self.on_answer_ready)
    @Slot(str)
    def on_answer_message(self, name:str, text:str, type:int, model_name:str="gpt-oss:20b", title:str = ''):
        if 0 < type and type < 5 and len(text) == 0:
            self.worker.generate(name, '', type, model_name, title)
        elif type == 0 and 0 < len(text):
            self.worker.generate(name, text, type, model_name, title)
    @Slot(str)
    def on_answer_ready(self, ai_text):
        self.ai_message.emit(ai_text)

class Ollama_Connector(QWidget):
    answer_ready = Signal(str)
    def generate(self, name:str, text:str, type:int, model_name:str, title:str=None):
        try:
            print(f"Generating AI Response... Input: {text[:20]}...")
            GlobalWorld().init_prompt_data()
            if model_name is None:
                GlobalWorld().get_llm('gpt-oss:20b', 0.7)
            if len(text) > 0:
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
            '자기외모': 'self_body', '자아': 'self_image', '자기모습': 'self_image'
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
        if not text:
            return
        active_mode = self._get_active_mode()

        # 1. 설정 모드일 때 처리
        if active_mode:
            self._handle_active_mode(text, active_mode)
        # 2. 일반 대화 시의 처리
        else:
            self._handle_general_command(text)

    def _handle_active_mode(self, text: list, mode_info):
        """설정 모드 중의 로직 처리"""
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
            user_input = " ".join(text)
            prompt = f"{user_input}을(를) 포함하여 다시 {prompt_topic} 직접 정의하여 설명하라."
            self.request_ai_signal.emit(self.name(), prompt, type_id)

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
        elif 0 < t <= 4:
            self.request_ai_signal.emit(self.name(), msg, t, None, None)
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