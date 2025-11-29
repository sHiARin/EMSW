from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QAbstractItemView, QMenu,
                               QSpinBox, QCheckBox, QInputDialog,
                               QTableWidget, QFrame, QHeaderView,
                               QTableWidgetItem)
from PySide6.QtGui import (QKeyEvent, QAction, QStandardItemModel,
                           QStandardItem, QPalette, QColor,
                           QGuiApplication, QFont, QTextItem)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QModelIndex, QObject)
from Config.config import ProgrameAction, ProgrameEventChecker
from EMSW_UI.core.resource import ProjectConfig, Display, GlobalSignalHub

import os

class EMSW(QMainWindow):
    def __init__(self, project:ProjectConfig):
        super().__init__()
        self.projectOpen = False
        self.project = project
        self.new_ai_config = None

        self.ActionRoop = {
                                ProgrameAction.ProgrameStart: self.__get_activate_window_position__,
                                ProgrameAction.SetWindowPosition: self.__fixed_monitor_position__,
                                ProgrameAction.FixedWindowPosition: self.__finish_initialization__,
                                ProgrameAction.CreateAIPerusona: self.__create_persona__,
                                ProgrameAction.OpenProjectSuccess: self.__ProjectOpening__,
                                ProgrameAction.SuccessBaigicSetupAIPerusona: self.__setup_selfImage__,

                            }
        self.ErrorRoop = {
                            ProgrameAction.ErrorFileJson : self.__jsonFileError_notice__,
                        }
        self.ForceUpdate = {
            "position" : self.update_position,
            "scale" : self.update_scale,
            "title" : self.update_title,
            "height" : self.setHeight,
        }

        self.hub = GlobalSignalHub.instance()
        self.hub.programe_signal.connect(self.__process_initialization_action__)
        self.hub.programe_signal.connect(self.__make_UI__)
        self.hub.windows_data['x'], self.hub.windows_data['y']
        self.hub.programe_signal.emit(ProgrameAction.ProgrameStart)

    def update_position(self, x:int, y:int):
        self.project.updatePosition(x, y)
    def update_title(self, title:str):
        self.setWindowTitle(title)
    def update_scale(self, width:int, height:int):
        self.project.updateScale(width, height)    
    def update_title(self, title:str):
        self.setWindowTitle(title)
        self.project.change_project_title(title)
    def setHeight(self, h:int):
        self.project.setHeight(h)
    def setWidth(self, w:int):
        self.project.setWidth(w)
    # 활성화된 모니터의 포지션을 식별합니다.

    def __get_activate_window_position__(self):
        self.__display__ = Display()
        self.hub.programe_signal.emit(ProgrameAction.SetWindowPosition)
        return 1

    # 모니터 밖을 벗어났는지 확인하고, 고칩니다.
    def __fixed_monitor_position__(self):
        def isIn(data:dict, x, y):
            return data['x'] < x and x < data['width'] or data[y] < y and y < data['height']
        t = False
        for d in self.__display__:
            t = isIn(d['geometry'], *self.project.ProgrameData()['windows_pos'].values())
            if t:
                break
        if not t:
            pass
        self.hub.programe_signal.emit(ProgrameAction.FixedWindowPosition)
        return 1

    #process signal을 처리합니다.
    def __process_initialization_action__(self, signal:ProgrameAction):
        if signal in self.ActionRoop.keys():
            self.ActionRoop[signal]()

    # ui를 만듭니다.
    def __make_UI__(self, signal:ProgrameAction):
        if signal == ProgrameAction.MakeUI:
            self.__run_programe__()

    # 프로그램 로딩 roop를 끝내는 메소드
    def __finish_initialization__(self):
        self.hub.programe_signal.emit(ProgrameAction.MakeUI)

    # run loop를 실행하는 메소드
    def __run_programe__(self):
        self.setGeometry(self.project.ProgrameData()['windows_pos']['x'], self.project.ProgrameData()['windows_pos']['y'], self.project.ProgrameData()['windows_scale']['width'], self.project.ProgrameData()['windows_scale']['height'])
        self.__make_menu__()
        self.Timer = QTimer()
        self.Timer.timeout.connect(self.__update__)
        self.Timer.setInterval(16)
        self.Timer.start()
        self.initUI()

    # 파일 에러를 처리하기 위해서 dir을 통해 메시지를 관리하는 메소드
    def __dir_changer__(self, message):
        self.dir = message

    # jsonfile에서 발생한 애러를 처리하는 메소드
    def __jsonFileError_notice__(self):
        QMessageBox.information(self, '알림', '파일에 오류가 발생했습니다.')

    # config의 데이터를 읽어서,
    # 가장 먼저 호출되며 UI 객체에서 사용되는 기본 설정을 담당함.
    # 일반적으로 start 함수의 동작이 전부 처리되기 전까지, 다음 호출은 중지된다.
    def __start__(self):
        self.hub.message.connect(self.dir)
        while self.__start_loop__:
            self.hub.programe_signal.connect(self.__start_action__)

    #초기에 프로그램을 구성하는 설정 메소드
    def __start_action__(self, signal:ProgrameAction):
        ProgrameEventChecker(signal)
        self.ActionRoop[signal]()
    # config에 windows_pos_scale을 업데이트
    def __update_windows_pos_scale__(self):
        self.project.updatePosition(self.x(), self.y())
        self.project.updateScale(self.width(), self.height())
    # 메뉴를 만드는 메소드
    def __make_menu__(self):
        documents = self.menuBar().addMenu("파일")
        self.__set_document_menu__(documents)
        edit = self.menuBar().addMenu("편집")
        tools = self.menuBar().addMenu("도구")
        characterMenu = self.menuBar().addMenu("캐릭터")
        views = self.menuBar().addMenu("뷰")
        self.__set_character_menu__(characterMenu)
        self.__set_view_menu__(views)
    # windows의 사이즈가 변경될 때 호출되는 메소드
    def resizeEvent(self, event):
        new_size = event.size()
        self.project.updateScale(new_size.width(), new_size.height())
        return super().resizeEvent(event)
    # 현재의 GlobalHub의 dir을 받아오는 메소드
    def __dir__(self):
        return self.dir
    # Action 정보를 식별하는 메소드
    def __Action_method__(self, action_signal : ProgrameAction):
        self.ActionRoop[action_signal]()
    # Error Action을 식별하는 메소드
    def __Error_method__(self, action_signal : ProgrameAction):
        self.ErrorRoop[action_signal]()
    # 매뉴의 액션 매뉴를 만드는 메소드
    def __add_menu_action__(self, text:str):
        return QAction(text, self)
    # documents 메뉴를 만드는 메소드
    def __set_document_menu__(self, documentMenu: QMenu):
        new_project = self.__add_menu_action__("프로젝트 만들기")
        new_project.triggered.connect(self.__new_project__)
        open_project = self.__add_menu_action__("프로젝트 열기")
        open_project.triggered.connect(self.__open_project__)
        new_document = self.__add_menu_action__("새 문서")
        find_document = self.__add_menu_action__("문서 찾기")
        Convert_files = self.__add_menu_action__("변환")
        Open_File = self.__add_menu_action__("파일 열기")
        configuration = self.__add_menu_action__("프로그램 설정")
        documentMenu.addAction(new_project)
        documentMenu.addAction(open_project)
        documentMenu.addAction(new_document)
        documentMenu.addAction(find_document)
        documentMenu.addAction(Convert_files)
        documentMenu.addAction(Open_File)
        documentMenu.addAction(configuration)
    def __new_project__(self):
        file_path = QFileDialog.getSaveFileName(self, "새 프로젝트", "새 프로젝트", "EMSW File(*.emsw)")
        self.project.new_project_files(file_path[0])
    def __open_project__(self):
        file_path = QFileDialog.getOpenFileName(self, "프로젝트 열기", "", "EMSW File(*.emsw)")
        self.project.open_project(dir=file_path[0], name=file_path[0])
        self.hub.programe_signal.emit(ProgrameAction.OpenProjectSuccess)
        print(self.project.getPosition())
    def __ProjectOpening__(self):
        pass
    # 캐릭터 매뉴를 정의하는 메소드
    def __set_character_menu__(self, characterMenu: QMenu):
        new_character = self.__add_menu_action__('새 캐릭터')
        new_character.triggered.connect(self.__create_persona__)
        load_character = self.__add_menu_action__("캐릭터 불러오기")
        load_character.triggered.connect(self.__load_perusona__)
        delete_character = self.__add_menu_action__("캐릭터 편집하기")
        delete_character.triggered.connect(self.__delete_perusona__)
        build_a_world = self.__add_menu_action__('세계관 구축')
        export_file = self.__add_menu_action__('세계관 내보내기')
        load_file = self.__add_menu_action__('세계관 불러오기')
        characterMenu.addAction(new_character)
        characterMenu.addAction(load_character)
        characterMenu.addAction(delete_character)
        characterMenu.addAction(build_a_world)
        characterMenu.addAction(export_file)
        characterMenu.addAction(load_file)
    def __set_view_menu__(self, views: QMenu):
        ChatView = self.__add_menu_action__('AI 챗 뷰 추가')
        views.addAction(ChatView)
    # project Update
    def update_Title(self, title:str):
        self.setWindowTitle(title)
    # 새 AI 설정 창을 여는 메소드
    def __create_persona__(self):
        self.newPersona = True
        ok = self.setProfile()
        if not ok:
            QMessageBox.information(self, "생성 취소", "캐릭터 생성을 취소하였습니다.")
            self.hub.programe_signal.emit(ProgrameAction.CancleCreateAIPerusona)
            return
        else:
            print('프로파일 설정이 완료되었습니다.')
            self.hub.programe_signal.emit(ProgrameAction.SuccessBaigicSetupAIPerusona)
    def __load_perusona__(self):
        print('load perusona')
    def __delete_perusona__(self):
        print('delete perusona')
        self.deleteView = Persona_delete_window(self.project)
        self.deleteView.show()
    # AI 캐릭터를 만드는 기능
    def setProfile(self):
        name, ok = QInputDialog.getText(self, '이름 입력', "이름을 입력해 주세요.")
        if ok and name:
            ok = not self.project.SearchPerusonaName(name)
            if ok and 2 < len(name):
                self.project.updatePerusonaName(name)
            else:
                return False
        else:
            return False
        age, ok = QInputDialog.getInt(self, '나이 입력', '나이를 입력해 주세요, : ', 0)
        if ok and age:
            if ok:
                self.project.updatePerusonaAge(name, age)
        items = ['남자', '여자']
        item, ok = QInputDialog.getItem(self, '성별 선택', '성별을 선택해 주세요. : ', items, 0, False)
        if ok and item:
            if ok:
                print(item)
                self.project.updatePerusonaSex(name, item)
            else:
                return False
        hobby, ok = QInputDialog.getText(self, '취미 입력', '취미를 입력해 주세요.(,로 복수개 입력하거나 비울 수도 있습니다.) : ')
        if ok:
            if len(hobby) == 0:
                self.project.updatePerusonaHobby(name, '취미가 없습니다.')
            elif 0 < len(hobby):
                self.project.updatePerusonaHobby(name, hobby)
            else:
                return False
        else:
            self.project.updatePerusonaHobby(name, '취미가 없습니다.')
        personality, ok = QInputDialog.getText(self, '성격 입력', '성격을 입력해 주세요.(비울 수 없습니다.) : ')
        if ok:
            if 0 < len(personality):
                self.project.updatePerusonaPersonality(name, personality)
            else:
                return False
        tendency, ok = QInputDialog.getText(self, '성향 입력', '성향을 입력해 주세요.(비울 수 없습니다.) : ')
        if ok:
            if 0 < len(tendency):
                self.project.updatePerusonaTendency(name, tendency)
            else:
                return False
        body, ok = QInputDialog.getText(self, '신체 묘사', '신체를 묘사해 주세요.')
        if ok and body:
            if 0 < len(body):
                print(1)
                if ':' in body:
                    body = body.split(',')
                    t = {}
                    for key, value in body:
                        if len(body[0]) == 0:
                            self.hub.programe_signal.emit(ProgrameAction.FailedCreateAIPerusona)
                            self.hub.message = name
                            return False
                        t[key] = value
                    self.project.updatePerusonaBody(name, t, dict)
                elif ',' in body:
                    self.project.updatePerusonaBody(name, body.split(', '), list)
                else:
                    self.project.updatePerusonaBody(name, body, str)
        print(self.project.getPerusonaDict())
        self.project.__save_Project__()
        return True
    def __setup_selfImage__(self):
        print('self image')
    def __fixed__update__(self):
        if not self.projectOpen:
            self.__update_windows_pos_scale__()
    def __update__(self):
        self.__fixed__update__()
    def __last_update__(self):
        pass
    # UI를 설정한다. 또한, 각 객체가 모습을 바꿀 때마다 __last_update__를 통해 호출된다.
    def initUI(self):
        hLayout = QHBoxLayout()
        mainboard = QWidget()
        mainboard.setLayout(hLayout)
        self.setCentralWidget(mainboard)
        self.show()

class Persona_delete_window(QWidget):
    def __init__(self, project:ProjectConfig):
        super().__init__()
        self.resize(800, 600)
        self.setStyleSheet("background: #F0F2F5")
        self.project = project
        self.__start__()
        self.init_ui()
    def __start__(self):
        self.table = QTableWidget()
        self.table.setSortingEnabled(False)
        names = self.project.getPerusonaDict().keys()
        values = self.project.getPerusonaDict()
        self.__create_tables__(names, values)
    def __create_tables__(self, names:list, value:dict):
        columns = ['이름', '나이', '성별', '취미', '성격', '성향', '외모']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        print(value)
        if value['body_data_type'] == dict:
            for n in names:
                if n == 'sample' or n == 'body_data_type':
                    continue
                else:
                    count = self.table.rowCount()
                    self.table.insertRow(count)
                    item = [n, f"{value[n]['age']}", value[n]['sex'], value[n]['hobby'], value[n]['personality'], value[n]['tendency'] ,"\n".join(([f"{k}:{v}" for k, v in zip(value[n]['body'].keys(), value[n]['body'].values())]))]
                    for col_index, data in enumerate(item):
                        item = QTableWidgetItem(data)
                        if 5 < col_index:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                            flags = item.flags()
                            item.setFlags(flags | Qt.ItemFlag.NoItemFlags)
                        self.table.setItem(count, col_index, item)
                        self.table.resizeRowToContents(count)
        elif value['body_data_type'] == list:
            for n in names:
                if n == 'sample' or n == 'body_data_type':
                    continue
                else:
                    count = self.table.rowCount()
                    self.table.insertRow(count)
                    item = [n, f"{value[n]['age']}", value[n]['sex'],value[n]['hobby'],value[n]['personality'],value[n]['tendency'],"\n".join(value[n]['body'])]
                    for col_index, data in enumerate(item):
                        item = QTableWidgetItem(data)
                        if 5 < col_index:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                            flags = item.flags()
                            item.setFlags(flags | Qt.ItemFlag.NoItemFlags)
                        self.table.setItem(count, col_index, item)
                        self.table.resizeRowToContents(count)
        elif value['body_data_type'] == str:
            for n in names:
                if n == 'sample' or n == 'body_data_type':
                    continue
                else:
                    count = self.table.rowCount()
                    self.table.insertRow(count)
                    item = [n, f"{value[n]['age']}", value[n]['sex'],value[n]['hobby'],value[n]['personality'],value[n]['tendency'],value[n]['body']]
                    for col_index, data in enumerate(item):
                        item = QTableWidgetItem(data)
                        if 5 < col_index:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                            flags = item.flags()
                            item.setFlags(flags | Qt.ItemFlag.NoItemFlags)
                        self.table.setItem(count, col_index, item)
                        self.table.resizeRowToContents(count)
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 상단 해더
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(15, 10, 15, 10)

        # 제목 라벨
        title_label = QLabel("캐릭터 목록")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #333; border: none;")

        # 검색창
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 입력...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCC;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #FAFAFA;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #ABC1D1;
            }
        """)

        # 검색 버튼
        search_btn = QPushButton("검색")
        search_btn.setFixedSize(60, 30)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #ABC1D1;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #96AAB9;
            }
        """)

        # 새로고침 버튼
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setFixedSize(80, 30)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEE500;
                color: #333;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F2D800;
            }
        """)

        top_layout.addWidget(title_label)
        top_layout.addStretch() # 빈 공간
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(search_btn)
        top_layout.addWidget(refresh_btn)

        main_layout.addWidget(top_frame)
        
        # [테이블 스타일링]
        self.table.setAlternatingRowColors(True) # 줄무늬 배경
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # 행 단위 선택
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) # 읽기 전용
        self.table.verticalHeader().setVisible(False) # 왼쪽 행 번호 숨김
        self.table.setShowGrid(False) # 격자선 숨김 (깔끔하게)
        
        # CSS 스타일시트 (헤더, 셀 디자인)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #DDD;
                border-radius: 10px;
                gridline-color: #EEE;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #000;
            }
            QHeaderView::section {
                background-color: #ABC1D1;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        # 헤더 늘리기 설정 (마지막 컬럼 채우기 등)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive) # 사용자가 조절 가능
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # '값' 컬럼을 꽉 채움

        main_layout.addWidget(self.table)


        status_layout = QHBoxLayout()
        self.count_label = QLabel("총 0개의 항목")
        self.count_label.setStyleSheet("color: #666; font-size: 12px;")
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedSize(80, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("background-color: #EEE; border-radius: 5px;")

        status_layout.addWidget(self.count_label)
        status_layout.addStretch()
        status_layout.addWidget(close_btn)

        main_layout.addLayout(status_layout)
    # ---------------------------------------------------------
    # 데이터 채우기 (UI 확인용 더미 데이터 함수)
    # ---------------------------------------------------------
    def load_dummy_data(self):
        data = [
            ("AI_Data", "sample_user", "홍길동", "테스트 유저입니다", "2024-05-20"),
            ("AI_World", "country", "Korea", "인구 5천만", "2024-05-21"),
            ("Config", "Version", "1.0.2", "현재 버전", "2024-05-22"),
            ("Timer", "Focus", "3600s", "집중 시간 데이터", "2024-05-22"),
            ("Log", "Error", "NullPointer", "치명적 오류 발생", "2024-05-23"),
        ]
        
        self.table.setRowCount(len(data))
        self.count_label.setText(f"총 {len(data)}개의 항목")

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col_idx != 2 else Qt.AlignLeft|Qt.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)