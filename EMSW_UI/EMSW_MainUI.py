from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QInputDialog, QTreeView,
                               QAbstractItemView, QMenu, QSpinBox,
                               QCheckBox)
from PySide6.QtGui import (QKeyEvent, QAction, QStandardItemModel,
                           QStandardItem, QPalette, QColor,
                           QGuiApplication)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QModelIndex, QObject)
from Config.config import ProgrameAction, ProgrameEventChecker
from EMSW_UI.core.resource import ProjectConfig, AI_Perusona, Display, GlobalSignalHub

import os

class EMSW(QMainWindow):
    def __init__(self, project:ProjectConfig):
        super().__init__()
        self.project = project
        print(self.project.dir)
        self.new_ai_config = None
        self.ActionRoop = {
                                ProgrameAction.ProgrameStart: self.__get_activate_window_position__,
                                ProgrameAction.SetWindowPosition: self.__fixed_monitor_position__,
                                ProgrameAction.FixedWindowPosition: self.__finish_initialization__,
                                ProgrameAction.CreateAIPerusona: self.__create_persona__,
                            }
        self.ErrorRoop = {
                            ProgrameAction.ErrorFileJson : self.__jsonFileError_notice__,
                        }
        self.hub = GlobalSignalHub.instance()
        self.hub.programe_signal.connect(self.__process_initialization_action__)
        self.hub.programe_signal.connect(self.__make_UI__)

        self.hub.programe_signal.emit(ProgrameAction.ProgrameStart)
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
            self.project.updatePosition(100, 100)
        self.hub.programe_signal.emit(ProgrameAction.FixedWindowPosition)
        return 1
    #process signal을 처리합니다.
    def __process_initialization_action__(self, signal:ProgrameAction):
        if signal in self.ActionRoop.keys():
            self.ActionRoop[signal]()
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
        file_path = QFileDialog.getSaveFileName(self, "새 프로젝트", "새 프로젝트", "EMSW File(*.emsw)")[0]
        self.project.new_project(file_path)
    # 캐릭터 매뉴를 정의하는 메소드
    def __set_character_menu__(self, characterMenu: QMenu):
        new_character = self.__add_menu_action__('새 캐릭터')
        new_character.triggered.connect(self.__new_character_action__)
        load_character = self.__add_menu_action__("캐릭터 불러오기")
        build_a_world = self.__add_menu_action__('세계관 구축')
        export_file = self.__add_menu_action__('세계관 내보내기')
        load_file = self.__add_menu_action__('세계관 불러오기')
        characterMenu.addAction(new_character)
        characterMenu.addAction(load_character)
        characterMenu.addAction(build_a_world)
        characterMenu.addAction(export_file)
        characterMenu.addAction(load_file)
    def __set_view_menu__(self, views: QMenu):
        ChatView = self.__add_menu_action__('AI 챗 뷰 추가')
        views.addAction(ChatView)
    # 새 AI 설정 창을 여는 메소드
    def __create_persona__(self):
        pass
    # 새 AI 프로파일을 만드는 메소드
    def __create_new_profile__(self):
        tdir = '/'.join([t for t in dir.split('/')][0:-1])
        print(tdir)
        if os.path.exists(tdir):
            self.new_ai_config = AI_Perusona(self.project.dir)
            self.hub.programe_signal.connect(self.__Action_method__)
            self.hub.message.emit(dir)
            self.hub.programe_signal.emit(ProgrameAction.CreateAIPerusona)
    # AI 캐릭터를 만드는 동작 메소드
    def __new_character_action__(self):
        file_path = QFileDialog.getSaveFileName(self, "AI 프로파일 만들기", "", "Profile File(*.profile)")
        print(file_path[0])
        self.__create_new_profile__(file_path[0])
    def __fixed__update__(self):
        self.__update_windows_pos_scale__()
        if not os.path.exists(self.project.dir):
            
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

class NewCharacterSetting_window(QWidget):
    def __init__(self, perusona:AI_Perusona, x:int, y:int, width:int, height:int):
        super().__init__()
        self.setGeometry(x, y, width, height)
        self.setWindowTitle("새 캐릭터 만들기")
        self.perusona = perusona
        self.initUI()
    def initUI(self):
        VLayout = QVBoxLayout()

        name = QHBoxLayout()
        name.addWidget(QLabel('이름 : '))
        self.nameBox = QLineEdit()
        name.addWidget(self.nameBox)

        age = QHBoxLayout()
        self.agebox = QSpinBox()
        self.agebox.setRange(16, 30)
        self.agebox.setSuffix(" 세")
        age.addWidget(self.agebox)
        
        sex = QHBoxLayout()
        sex.addWidget(QLabel('성별'))
        self.male = QCheckBox('남성(Male)')
        self.female = QCheckBox('여성(female)')
        self.male.clicked.connect(self.on_male_trigger)
        self.female.clicked.connect(self.on_female_trigger)
        sex.addWidget(self.male)
        sex.addWidget(self.female)
        
        personality = QHBoxLayout()
        personality.addWidget(QLabel('성격 : '))
        self.personalityBox = QLineEdit('성격을 정의하는 키워드를 입력하세요')
        personality.addWidget(self.personalityBox)
        
        hobby = QHBoxLayout()
        hobby.addWidget(QLabel('취미 : '))
        self.hobbyBox = QLineEdit('취미를 정의하는 키워드를 입력하세요')
        hobby.addWidget(self.hobbyBox)
        
        tendency = QHBoxLayout()
        tendency.addWidget(QLabel('성향 : '))
        self.tendencyBox = QLineEdit("성향을 정의하는 키워드를 입력하세요")
        tendency.addWidget(self.tendencyBox)
        
        body = QHBoxLayout()
        body.addWidget(QLabel("신체 정보 : "))
        self.bodyBox = QLineEdit("신체 정보를 정의하는 키워드를 입력하세요")
        body.addWidget(self.bodyBox)

        okBox = QPushButton()
        okBox.setText("저장")
        okBox.clicked.connect(self.okBnt)

        VLayout.addLayout(name)
        VLayout.addLayout(age)
        VLayout.addLayout(sex)
        VLayout.addLayout(personality)
        VLayout.addLayout(hobby)
        VLayout.addLayout(tendency)
        VLayout.addLayout(body)
        VLayout.addWidget(okBox)

        self.setLayout(VLayout)
    def on_female_trigger(self, checked):
        if checked:
            self.male.setChecked(False)
        else:
            self.male.setChecked(True)
    def on_male_trigger(self, checked):
        if checked:
            self.female.setChecked(False)
        else:
            self.female.setChecked(True)
    def okBnt(self):
        close = True
        if len(self.nameBox.text()) < 2:
            QMessageBox.information(self, '정보', '이름을 2글자 이상 입력하세요.')
            close = False
        else:
            text = self.nameBox.text()
            if ':' in text:
                self.perusona.set_name(text.split(':'))
        self.perusona.set_age(self.agebox.value())
        if self.male.checkState():
            self.perusona.set_sex(['남자','man'])
        elif self.female.checkState():
            self.perusona.set_sex(['여자', 'woman'])
        else:
            QMessageBox.information(self, '정보', '성별을 선택해 주세요.')
            close = False
        if len(self.personalityBox.text()) == 0:
            QMessageBox.information(self, '정보', '성격 키워드를 입력하세요.')
            close = False
        else:
            if ':' in self.personalityBox.text():
                self.perusona.set_personality(self.personalityBox.text().split(':'))
            else:
                self.perusona.set_personality([self.personalityBox.text()])
        if len(self.hobbyBox.text()) == 0:
            self.perusona.set_hobby(['없음', 'None'])
        else:
            if ':' in self.hobbyBox.text():
                self.perusona.set_hobby(self.hobbyBox.text().split(':'))
            else:
                self.perusona.set_hobby([self.hobbyBox.text()])
        if len(self.tendencyBox.text()) == 0:
            QMessageBox.information(self, '정보', '성향 키워드를 입력하세요.')
            close = False
        else:
            if ':' in self.tendencyBox.text():
                self.perusona.set_tendency(self.tendencyBox.text().split(':'))
            else:
                self.perusona.set_Tendency([self.tendencyBox.text()])

        if close:
            self.closeEvent(self.event)