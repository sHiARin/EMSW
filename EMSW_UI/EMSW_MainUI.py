from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QInputDialog, QTreeView,
                               QTreeWidgetItem)
from PySide6.QtGui import (QKeyEvent, QAction, QStandardItemModel,
                           QStandardItem, QPalette, QColor)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QObject)
from enum import Enum, unique

from Config.config import conf

import os, json

# 메인 메뉴의 액션을 구분하기 위한 전용 클래스
@unique
class ProgrameAction(Enum):
    ### 프로그램 동작 관련 액션 시그널 ###
    # 프로그램이 열렸습니다.
    ProgrameStart = 0x0fff000
    # 프로그램이 실행중입니다.
    ProgrameDuring = 0x0fff001
    # 포커스를 벗어났습니다.
    ProgrameOut = 0x0fff002
    # 포커스를 얻었습니다.
    ProgrameIn = 0x0fff003
    ### 서브 윈도우 및 기타 메뉴 생성 관련 액션 시그널 ###
    # 서브 윈도우 창이 열렸습니다.
    SubWindowsOpened = 0x1fff000
    # 프로젝트 생성에 성공했습니다.
    ProjectCreateSuccess = 0x1fff001
    # 프로젝트 생성에 실패했습니다.
    ProjectCreateFailed = 0x1fff002
    # 프로젝트 생성을 취소했습니다.
    CancleProjectCreate = 0x1fff003
    # 프로젝트가 열리지 않았습니다.
    NotOpenedProject = 0x1fff004
    # 프로젝트 여는 것을 취소했습니다.
    CancleOpenedProject = 0x1fff005
    # 프로젝트가 열렸습니다.
    OpenProjectSuccess = 0x1fff006
    # 프로젝트 여는 것에 실패했습니다.
    CannotOpenProject = 0x1fff007
    ### 프로그램 동작 변수 관련 액션 시그널 ###
    # 프로젝트 경로가 설정되었습니다.
    SetTheProjectDir = 0x2fff000
    ### 프로그램 UI 관련 액션 시그널 ###
    # UI가 업데이트 되었습니다.
    UpdateUI = 0x3fff001
    # TreeView가 업데이트 되었습니다.
    UpdateTreeView = 0x3fff002
# 메인 매뉴의 레이아웃 사이즈를 관리하기 위한 전용 클래스
class ProgrameUIData:
    pass
# 프로젝트를 열기 위한 클래스
class OpenProject(QDialog):
    Project_dir = Signal(str)
    Action_Type = Signal(ProgrameAction)
    def __init__(self, x:int, y:int, width:int, height:int):
        super().__init__()
        self.Action_Type.emit(ProgrameAction.SubWindowsOpened)
        self.PosX = x
        self.PosY = y
        self.WidthSize = width
        self.HeightSize = height
        self.dir = ''
        self.__init_ui__()
    # UI를 생성하는 메소드
    def __init_ui__(self):
        self.setGeometry(self.PosX, self.PosY, self.WidthSize, self.HeightSize)
        self.setWindowTitle('프로젝트 열기')
        layout = QVBoxLayout()
        select_directory_dir = QHBoxLayout()
        button_layout = QHBoxLayout()
        
        # 프로젝트 경로 설정
        project_label = QLabel()
        project_label.setText('경로 : ')
        self.text = QLineEdit()
        self.text.setText(self.dir)
        select_Button = QPushButton('프로젝트 열기')
        select_Button.clicked.connect(self.directoryOpen)
        select_directory_dir.addWidget(project_label)
        select_directory_dir.addWidget(self.text)
        select_directory_dir.addWidget(select_Button)
        
        # layout 완성
        OkButton = QPushButton('확인')
        OkButton.clicked.connect(self.okBtnAction)
        CancleButton = QPushButton('취소')
        CancleButton.clicked.connect(self.cancleBtnAction)
        button_layout.addWidget(OkButton)
        button_layout.addWidget(CancleButton)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(select_directory_dir)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.show()
    # directory를 선택하는 창을 여는 메소드
    def directoryOpen(self):
        self.dir = QFileDialog.getExistingDirectory(self, '프로젝트 위치 설정', self.dir)
        self.text.setText(self.dir)
    # cancleBntAction을 정의한 메소드 프로젝트를 취소한다.
    def cancleBtnAction(self):
        self.dir = None
        self.Action_Type.emit(ProgrameAction.CancleOpenedProject)
        QMessageBox.information(self, "취소", '프로젝트 열기를 취소했습니다.', QMessageBox.StandardButton.Ok)
        self.close()
    def closeEvent(self, event):
        print("Project Open window close")
    # okBtnAction을 정의한 메소드 directory를 설정한다. 프로젝트 명이 겹치는 경우, ''을 반환한다. 
    def okBtnAction(self):
        if self.dir == '':
            self.Project_dir.emit('')
            self.Action_Type.emit(ProgrameAction.NotOpenedProject)
        elif os.path.exists(self.dir) and os.access(self.dir, os.R_OK):
            self.Project_dir.emit(self.dir)
            self.Action_Type.emit(ProgrameAction.OpenProjectSuccess)
        else:
            self.Project_dir.emit(self.dir)
            self.Action_Type.emit(ProgrameAction.CannotOpenProject)
        self.close()
# 프로젝트를 생성하기 위한 클래스
class CreateProject(QDialog):
    Project_dir = Signal(str)
    Action_Type = Signal(ProgrameAction)
    def __init__(self, x:int, y:int, width:int, height:int):
        super().__init__()
        self.Action_Type = ProgrameAction.SubWindowsOpened
        self.PosX = x
        self.PosY = y
        self.WidthSize = width
        self.HeightSize = height
        self.dir = r'C:\Users\asuna\OneDrive\문서'
        self.name = '새 프로젝트'
        self.__init_ui__()
    def __init_ui__(self):
        # UI 생성
        self.setGeometry(self.PosX, self.PosY, self.WidthSize, self.HeightSize)
        self.setWindowTitle('프로젝트 생성')
        layout = QVBoxLayout()
        select_directory_dir = QHBoxLayout()
        project_name = QHBoxLayout()
        button_layout = QHBoxLayout()
        # 프로젝트 경로 설정
        project_label = QLabel()
        project_label.setText('프로젝트 경로 : ')
        self.prodir = QLineEdit()
        self.prodir.setText(self.dir)
        self.prodir.setReadOnly(True)
        select_Button = QPushButton('경로 변경')
        select_Button.clicked.connect(self.directoryOpen)
        select_directory_dir.addWidget(project_label)
        select_directory_dir.addWidget(self.prodir)
        select_directory_dir.addWidget(select_Button)
        # 프로젝트 이름 설정
        name_label = QLabel()
        name_label.setText('프로젝트 이름 : ')
        self.name_text = QLineEdit()
        self.name_text.setText(self.name)
        project_name.addWidget(name_label)
        project_name.addWidget(self.name_text)
        # layout 완성
        OkButton = QPushButton('확인')
        OkButton.clicked.connect(self.okBtnAction)
        CancleButton = QPushButton('취소')
        CancleButton.clicked.connect(self.cancleBtnAction)
        button_layout.addWidget(OkButton)
        button_layout.addWidget(CancleButton)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(select_directory_dir)
        layout.addLayout(project_name)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.show()
    # directory를 선택하는 창을 여는 메소드
    def directoryOpen(self):
        self.dir = QFileDialog.getExistingDirectory(self, '프로젝트 위치 설정', self.dir)
        self.prodir.setText(self.dir)
    # cancleBntAction을 정의한 메소드 프로젝트를 취소한다.
    def cancleBtnAction(self):
        self.project_dir = None
        QMessageBox.information(self, "취소", '프로젝트 생성을 취소했습니다.', QMessageBox.StandardButton.Ok)
        self.close()
    # okBtnAction을 정의한 메소드 directory를 설정한다. 프로젝트 명이 겹치는 경우, ''을 반환한다. 
    def okBtnAction(self):
        self.dir = self.prodir.text()
        self.name = self.name_text.text()
        if self.__make_directory__():
            QMessageBox.information(self, "확인", "프로젝트가 성공적으로 생성되었습니다.", QMessageBox.StandardButton.Ok)
            self.dir = f'{self.dir}\\{self.name}'
            self.Project_dir.emit(self.dir)
        else:
            self.Project_dir.emit('')
            QMessageBox.critical(self, "경고", "프로젝트 생성이 실패했습니다. (프로젝트 이름이 중복입니다.)", QMessageBox.StandardButton.Ok)
        self.close()
    # 프로젝트를 생성하는 메소드로, dir링크를 받아서 직접 생성한다. 이때, 생성에 성공한 경우 False를 반환하고, 생성에 실패한 경우 True를 반환한다.
    def __make_directory__(self):
        #print('make_directory')
        if os.path.isdir(rf"{self.dir}\\{self.name}"):
            return False
        os.makedirs(rf"{self.dir}\\{self.name}")
        return True
    # 프로젝트를 닫는 메소드 현 이벤트에 따라 데이터를 다시 한번 교정한다.
    def closeEvent(self, event):
        if self.Project_dir == '':
            self.Action_Type.emit(ProgrameAction.ProjectCreateFailed)
        elif self.Project_dir == None:
            self.Action_Type.emit(ProgrameAction.CancleProjectCreate)
        else:
            self.Action_Type.emit(ProgrameAction.ProjectCreateSuccess)
        event.accept()
# treeView는 QWidget을 받아서 처리한다.
# EMSWTreeView는 QWidget에서 관리하며, TreeView는 상속받은 별도의 class로 처리한다.
class EMSWTreeView(QWidget):
    def __init__(self, root_dir:str):
        super().__init__()
        self.blakTr = True
        self.colorText = '#0fffff'
        if root_dir != '':
            self.root = root_dir
            self.child = os.listdir(root_dir)
            self.treeView = QTreeView(self)
            self.model = QStandardItemModel()
            self.blakTr = False
            self.__start__()
            self.init_ui()
        else:
            self.root = 'blank'
            self.child = []
            self.treeView = QTreeView(self)
            self.model = QStandardItemModel()
            self.__start__
            self.init_ui()
    def __start__(self):
        self.novels = []
        if 0 < len(self.root):
            self.root_name = self.root.split('/')[-1]
            self.makeTree()
    def getChild(self, dirs:str):
        print(os.listdir(dirs))
    def makeTree(self):
        self.root_tree = QStandardItem(self.root_name)
        for t in self.child:
            if os.path.isdir(f"{self.root}/{t}"):
                self.novels.append(QStandardItem(t))
        for n in self.novels:
            self.root_tree.appendRow([n])
        self.updateModels()
    def setWidth(self, width:int):
        self.width = width
        self.setFixedWidth(width)
    def setHeight(self, height:int):
        self.height = height
        self.setFixedHeight(height)
    def updateSize(self, width, height):
        self.width = width
        self.height = height
        self.resize(width, height)
    def updateModels(self):
        self.model.appendRow([self.root_tree])
    def setRoot(self, root:str):
        self.root = root
        self.child = os.listdir(self.root)
        title = self.root.split('/')[-1]
        if len(self.child) == 0:
            text, ok = QInputDialog.getText(None, '새 소설의 이름을 지정해주세요.', '소설 이름을 입력하세요.')
            if ok:
                js_data = {}
                js_data['title'] = text
                with open(self.root + f'/{title}.json', 'w', encoding='utf-8') as file:
                    json.dump(js_data, file)
                print(self.root + f'/{text}')
                os.mkdir(self.root + f'/{text}')
                self.child = os.listdir(self.root)
            else:
                print('cancel new Novel')
        else:
            print(self.child.__len__())
    def setColorText(self, color:str):
        self.colorText = color
    def init_ui(self):
        if not self.blakTr:
            vlayout = QVBoxLayout()
            vlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_novel = QPushButton('새 소설')
            self.treeView.setModel(self.model)
            vlayout.addWidget(new_novel)
            vlayout.addWidget(self.treeView)
            self.setLayout(vlayout)
        else:
            vlayout = QVBoxLayout()
            vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            new_novel = QPushButton('새 소설')
            self.treeView.setModel(self.model)
            label = QLabel()
            label.setText('빈 소설')
            vlayout.addWidget(new_novel)
            vlayout.addWidget(label)
            self.setLayout(vlayout)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colorText))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
# EMSW 기능을 수행하는 MainUI.
# EMSW 기능이란 작가가 본인 스스로 데이터 맵을 구축하여 창작에 도움이 될 수 있는 프로젝트이다.
# 좀 더 목적을 밝히자면, 이전에 쓴 내용을 불러와 참고하거나, 이전에 쓴 글의 내용으로 지금 집필하는 내용의 소설에 도움을 받기 위해 사용하는 프로젝트다.
class EMSW(QMainWindow):
    def __init__(self, config:conf):
        super().__init__()
        # window의 사이즈를 정의한다.
        self.config = config
        #windows 프로그램을 시작하며, 기초 데이터를 설정하고, UI를 만든다.
        self.__start__()
        self.time = QTimer(self)
        self.time.timeout.connect(self.__update__)
        self.time.start(16)
        self.initUI()
    # 모든 키 입력을 무시한다.
    def keyPressEvent(self, event: QKeyEvent):
        event.ignore()
    # 프로그램의 포커스를 상실할 때 가장 먼저 호출되어야만 하는 동작 실행
    def focusOutEvent(self):
        self.ProgrameSignal = ProgrameAction.ProgrameOut
        self.time.stop()
        print('main Windows update timer stop')
    # 프로그램의 포커스를 가졌을 때 가장 먼저 호출되어야만 하는 동작 실행
    def focusInEvent(self):
        self.time.staRT()
    # 가장 먼저 호출되며 UI 객체에서 사용되는 기본 설정을 담당함.
    def __start__(self):
        self.windowPosX = self.config.windows_config['windows_pos_x']
        self.windowPosY = self.config.windows_config['windows_pos_y']
        self.windowSizeWidth = self.config.windows_config['windows_scale_width']
        self.windowSizeHeight = self.config.windows_config['windows_scale_height']
        self.programeInfo = self.config.programe_data['LastOpenDir']
        self.projectList = self.config.programe_data['ProjectDirs']
        if self.programeInfo != '':
            self.dir = self.programeInfo
        else:
            self.dir = ''
        if self.dir != '':
            self.trView = EMSWTreeView(self.dir)
        if self.dir == '':
            self.trView = EMSWTreeView('')
        self.ProgrameSignal = ProgrameAction.ProgrameStart
        self.MainBoard = QWidget()
        self.makeMenu()
        self.setWindowTitle('EMSW')
        self.setGeometry(self.windowPosX, self.windowPosY, self.windowSizeWidth, self.windowSizeHeight)
    def Update_windows_position(self):
        if (self.x != self.config.windows_config['windows_pos_x']) or (self.y != self.config.windows_config['windows_pos_y']):
            self.config.updatePosition(self.x, self.y)
    def Update_windows_Scale(self):
        if (self.width != self.config.windows_config['windows_scale_width']) or (self.height != self.config.windows_config['windows_scale_height']):
            self.config.updateScale(self.width, self.height)
    def __setTreeView__(self):
        self.trView.updateSize(self.config.windows_config['treeview_width'], self.config.windows_config['treeview_height'])
    # update에서 가장 빨리 호출되는 메소드.
    # 주로 데이터의 업데이트, 또는 갱신을 담당하는 메소드 또는 함수가 연결된다.
    def __fixed_update__(self):
        self.FixedUpdate()
    def FixedUpdate(self):
        if self.config.programe_data['LastOpenDir'] == '' or self.config.programe_data['LastOpenDir'] is None:
            pass
        elif self.ProgrameSignal == ProgrameAction.SetTheProjectDir:
            self.trView.setRoot(self.config.programe_data['LastOpenDir'])
            self.ProgrameSignal = ProgrameAction.ProgrameDuring
        else:
            self.ProgrameSignal = ProgrameAction.ProgrameDuring
    def windowsUpdate(self):
        if ProgrameAction.UpdateTreeView == self.ProgrameSignal:
            print(self.dir)
            self.trView.setRoot(self.dir)
            self.ProgrameSignal = ProgrameAction.ProgrameDuring
        pos = self.pos()
        scale = self.geometry()
        if ((pos.x() != self.config.windows_config['windows_pos_x']) or (pos.y() != self.config.windows_config['windows_pos_y'])):
            self.config.updatePosition(pos.x(), pos.y())
        if ((scale.width() != self.config.windows_config['windows_scale_width']) or (scale.height() != self.config.windows_config['windows_scale_height'])):
            self.config.updateScale(scale.width(), scale.height())
        try:
            if self.trView.geometry().width() != self.config.windows_config['treeview_width'] and self.trView.geometry().height() != self.config.windows_config['treeview_height'] and self.programeInfo == ProgrameAction.ProgrameDuring:
                self.programeInfo = ProgrameAction.UpdateUI
        except:
            pass
    # 주기적으로 업데이트되는 메소드. 또한, initUI를 호출하여 주기적으로 프로그램의 UI를 변경한다.
    def __update__(self):
        #모든 update가 동작하기 전, 반드시 실행해야 하는 동작은 여기에 구현
        self.windowsUpdate()
        #update가 실행되기 전, 처리해야 할 내용은 여기에 구현한다.
        self.__fixed_update__()
        # __update__에서 처리하는 내용은 여기에 구현한다.
        if self.ProgrameSignal == ProgrameAction.UpdateUI:
            self.repaint()
            print("repaint")
            self.ProgrameSignal = ProgrameAction.ProgrameDuring
        # update가 끝난 다음, 구현해야 할 내용은 여기에 구현한다.
        self.__last_update__()
    # 가장 나중에 업데이트되는 메소드. initUI 보다도 나중에 호출된다.
    def __last_update__(self):
        self.LastUpdate()
    # 가장 나중에 
    def LastUpdate(self):
        if self.ProgrameSignal == ProgrameAction.OpenProjectSuccess:
            print("작업 폴더 열기가 완료되었습니다.")
            print(f"웹소설 작업 폴더 : {self.dir}")
            if self.programeInfo != self.dir:
                self.programeInfo = self.dir
            self.trView.setRoot(self.dir)
        pass
    # Menu를 만드는 메소드
    def makeMenu(self):
        menu = self.menuBar()
        self.makeFileMenu(menu.addMenu('File'))
    # File Menu를 만드는 메소드
    def makeFileMenu(self, menu):
        open_menu = QAction('프로젝트 열기', self)
        open_menu.triggered.connect(self.openProject)
        project_menu = QAction('새 프로젝트', self)
        project_menu.triggered.connect(self.newProjectAction)
        menu.addAction(open_menu)
        menu.addAction(project_menu)
    # 프로젝트를 여는 매뉴를 호출하는 메소드
    def openProject(self):
        print('작업폴더 열기 작업이 수행되었습니다.')
        opePro = OpenProject(self.x(), self.y(), 580, 120)
        opePro.Project_dir.connect(self.getProjectDirectory)
        opePro.Action_Type.connect(self.getProgrameSignal)
        opePro.exec()
        print(f'작업폴더 열기 작업이 완료되었습니다. : {self.dir}')
    # 프로젝트를 여는 메뉴를 호출하는 메소드
    def newProjectAction(self):
        print('작업폴더 추가 작업이 수행되었습니다.')
        crepro = CreateProject(self.x(), self.y(), 580, 120)
        if crepro.exec():
            pass
    # direcotry를 받아오는 메소드
    def getProjectDirectory(self, recived_data):
        print(recived_data)
        self.dir = recived_data
        self.trView.setRoot(recived_data)
        self.config.AppenddProjectDir(recived_data)
        self.ProgrameSignal = ProgrameAction.UpdateTreeView
    # Programe Signal 데이터를 처리하는 메소드
    def getProgrameSignal(self, recived_data):
        self.ProgrameSignal = recived_data
    # 가장 마지막으로 호출되는 메소드이며, 반드시 나중에 호출되어야 하는 기능의 경우 이곳에 연결됨 
    # UI를 설정한다. 또한, 각 객체가 모습을 바꿀 때마다 __last_update__를 통해 호출된다.
    def initUI(self):
        hLayout = QHBoxLayout()
        if self.trView != None:
            hLayout.addWidget(self.trView)
        if self.config.windows_config['widget_align'] == 'left':
            hLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif self.config.windows_config['widget_align'] == 'right':
            hLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
        elif self.config.windows_config['widget_align'] == 'center':
            hLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.MainBoard.setLayout(hLayout)
        self.setCentralWidget(self.MainBoard)
        self.show()
    # 창이 닫힐때 실행되는 동작을 정의한다.
    # 프로젝트가 닫히는 절차를 정의한다.
    def closeEvent(self, event):
        pass