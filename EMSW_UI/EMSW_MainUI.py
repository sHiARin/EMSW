from PySide6.QtWidgets import (QMainWindow, QWidget, QFileDialog,
                               QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox,
                               QDialog, QInputDialog, QTreeView,
                               QAbstractItemView)
from PySide6.QtGui import (QKeyEvent, QAction, QStandardItemModel,
                           QStandardItem, QPalette, QColor,)
from PySide6.QtCore import (Qt, Signal, QTimer,
                            QModelIndex)
from enum import Enum, unique
import xml.etree.ElementTree as ET

from Config.config import conf, ProjectConfig

import os, json, platform, hashlib

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
    # 파일을 생성했습니다.
    CreateFiles = 0x1fff008
    ### 프로그램 동작 변수 관련 액션 시그널 ###
    # 프로젝트 경로가 설정되었습니다.
    SetTheProjectDir = 0x2fff000
    ### 프로그램 UI 관련 액션 시그널 ###
    # UI가 업데이트 되었습니다.
    UpdateUI = 0x3fff001
    # TreeView가 업데이트 되었습니다.
    UpdateTreeView = 0x3fff002
    # TreeView에서 선택이 변경되었습니다.
    SelectTreeView = 0x3fff003
    # TreeView의 작업이 완료되었습니다.
    FinishedTreeViewWork = 0x3fff004
    # TreeView의 갱신을 실패했습니다.
    FailedTreeViewUpdate = 0x3fff005
# 디버그를 위해 Signal의 종류를 체크하는 함수
def CheckProgrameSignal(signal:int):
    if signal == ProgrameAction.ProgrameStart:
        print("프로그램이 시작되었습니다.")
    elif signal == ProgrameAction.ProgrameDuring:
        print("프로그램이 실행중입니다..")
    elif signal == ProgrameAction.ProgrameOut:
        print("포커스를 벗어났습니다.")
    elif signal == ProgrameAction.ProgrameIn:
        print("포커스를 가졌습니다.")
    elif signal == ProgrameAction.SubWindowsOpened:
        print("포커스를 가졌습니다.")
    elif signal == ProgrameAction.ProjectCreateFailed:
        print("프로젝트 생성에 실패했습니다.")
    elif signal == ProgrameAction.ProjectCreateSuccess:
        print("프로젝트 생성에 성공했습니다.")
    elif signal == ProgrameAction.CancleProjectCreate:
        print("프로젝트 생성을 취소했습니다.")
    elif signal == ProgrameAction.OpenProjectSuccess:
        print("프로젝트 열기를 성공했습니다.")
    elif signal == ProgrameAction.CannotOpenProject:
        print("프로젝트 열기를 실패했습니다.")
    elif signal == ProgrameAction.CreateFiles:
        print("파일 생성을 성공했습니다.")
    elif signal == ProgrameAction.SetTheProjectDir:
        print("프로젝트 경로가 설정되었습니다.")
    elif signal == ProgrameAction.UpdateUI:
        print("UI가 업데이트되었습니다.")
    elif signal == ProgrameAction.UpdateTreeView:
        print("TreeView가 업데이트되었습니다.")
    elif signal == ProgrameAction.SelectTreeView:
        print("TreeView 선택 항목이 변경되었습니다.")
    elif signal == ProgrameAction.FinishedTreeViewWork:
        print("TreeView의 작업이 완료되었습니다.")
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
        self.PosX = x
        self.PosY = y
        self.WidthSize = width
        self.HeightSize = height
        if platform.system() == 'windows':
            self.dir = r'C:\Users\asuna\OneDrive\문서'
        elif platform.system() == "Darwin":
            self.dir = '~\Documents'
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
            if platform.system() == 'windows':
                if not os.path.isdir(f'{self.dir}\\{self.name}'):
                    os.mkdir(f'{self.dir}\\{self.name}')
                self.Project_dir.emit(f'{self.dir}\\{self.name}')
                self.Action_Type.emit(ProgrameAction.UpdateTreeView)
                print(f'{self.dir}\\{self.name}')
            elif platform.system() == 'Darwin':
                if not os.path.isdir(f"{self.dir}/{self.name}"):
                    os.mkdir(f"{self.dir}/{self.name}")
                self.Project_dir.emit(f"{self.dir}/{self.name}")
                self.Action_Type.emit(ProgrameAction.UpdateTreeView)
                print(f"{self.dir}/{self.name}")
        else:
            self.Project_dir.emit('')
            QMessageBox.critical(self, "경고", "프로젝트 생성이 실패했습니다. (프로젝트 이름이 중복입니다.)", QMessageBox.StandardButton.Ok)
        self.close()
    # 프로젝트를 생성하는 메소드로, dir링크를 받아서 직접 생성한다. 이때, 생성에 성공한 경우 False를 반환하고, 생성에 실패한 경우 True를 반환한다.
    def __make_directory__(self):
        #print('make_directory')
        if platform.system() == 'windows':
            if os.path.isdir(rf"{self.dir}\\{self.name}"):
                return False
            os.makedirs(rf"{self.dir}\\{self.name}")
            return True
        elif platform.system() == "Darwin":
            print(f"{self.dir}/{self.name}")
            if os.path.isdir(f"{self.dir}/{self.name}"):
                return False
            os.mkdir(f"{self.dir}/{self.name}")
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
    Action_Type = Signal(ProgrameAction)
    DocumentDir = Signal(str)
    def __init__(self, root_dir:str, config:conf):
        self.config = config
        super().__init__()
        self.blakTr = True
        self.colorText = '#0fffff'
        if root_dir != '':
            self.document_dir = ''
            self.root = root_dir
            self.child = os.listdir(root_dir)
            self.treeView = QTreeView(self)
            self.model = QStandardItemModel()
            self.blakTr = False
            self.__start__()
            self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.init_ui()
        elif root_dir == r"C:\User" or root_dir == '' or "~/Documents":
            self.root = 'blank'
            self.child = []
            self.treeView = QTreeView(self)
            self.model = QStandardItemModel()
            self.__start__()
            self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.init_ui()
    def __start__(self):
        self.novels = []
        self.selectDir = None
        self.ProjectConf = ProjectConfig(self.root)
        print(self.root)
        if 0 < len(self.root):
            self.root_name = self.root.split('/')[-1]
            self.makeTree()
    def resetTree(self):
        self.model.clear()
        print(self.root)
        self.__start__()
    def getChild(self, dirs:str):
        print(os.listdir(dirs))
    def makeChildTree(self, dir:str, parents:QStandardItem):
        for file in os.listdir(dir):
            print(file)
            if os.path.isdir(f"{dir}/{file}"):
                child_Item = QStandardItem(file)
                self.makeChildTree(f"{dir}/{file}", child_Item)
                parents.appendRow(child_Item)
            elif os.path.isfile(f"{dir}/{file}"):
                child = file.split('.')[0]
                child_Item = QStandardItem(child)
                parents.appendRow(child_Item)
        return parents
    def makeTree(self):
        self.root_tree = QStandardItem(self.root_name)
        for t in self.child:
            print(t)
            if os.path.isdir(f"{self.root}/{t}"):
                t_item = QStandardItem(t)
                t_item = self.makeChildTree(f"{self.root}/{t}", t_item)
                self.novels.append(t_item)
        print(self.novels)
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
        if len(self.child) == 0:
            self.makeGroup()
        else:
            print(self.child.__len__())
    def selectGroupDir(self, index:QModelIndex, previous_index:QModelIndex):
        if index.data() in self.root:
            self.DocumentDir.emit(self.root)
            self.document_dir = self.root
        else:
            if os.path.exists(f"{self.root}/{index.data()}"):
                self.DocumentDir.emit(f"{self.root}/{index.data()}")
                self.document_dir = f"{self.root}/{index.data()}"
                self.selectDir = index.data()
            elif os.path.exists(f"{self.document_dir}/{index.data()}"):
                self.DocumentDir.emit(f"{self.document_dir}/{index.data()}")
                self.document_dir = f"{self.document_dir}/{index.data()}"
                self.selectDir = index.data()
            else:
                print(index.data())
        #print(self.document_dir)
        self.Action_Type.emit(ProgrameAction.SelectTreeView)
    def makeGroup(self):
        print(self.root)
        title = self.root.split('/')[-1]
        path = f"{self.root}/{title}.json"
        text, ok = QInputDialog.getText(None, '새 그룹의 이름을 지정해주세요.', '그룹 이름을 입력하세요.')
        print(os.listdir(self.root))
        if os.path.isfile(path):
            if ok:
                with open(path, 'r', encoding='utf-8-sig') as file:
                    js_data = json.load(file)
                print(js_data)
                if text in js_data['title']:
                    QMessageBox(self, "알림", "프로젝트 이름이 존재합니다.", QMessageBox.StandardButton.OK|QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
                js_data['title'] = list(js_data['title']).append(text)
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(js_data, file)
                print(self.root + f'/{text}')
                os.mkdir(self.root + f'/{text}')
                self.child = os.listdir(self.root)
            else:
                print('cancel new Novel')
        else:
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
    def setColorText(self, color:str):
        self.colorText = color
    def newProject(self):
        crepro = CreateProject(self.x(), self.y(), 580, 120)
        if crepro.exec():
            pass
        self.Action_Type.emit(ProgrameAction.ProjectCreateSuccess)
    def newPage(self):
        text, ok = QInputDialog.getText(None, '새 페이지의 이름을 입력해 주세요.', '새 페이지')
        if not os.path.isdir(self.document_dir):
            print(self.root)
            print(self.document_dir)
        elif ok:
            if 0 < self.document_dir.__len__() and not (text in os.listdir(f'{self.document_dir}')):
                dir = f'{self.document_dir}'
                print(dir)
                open(f'{dir}/{text}', 'w', encoding='utf-8').writelines('')
                self.UpdateTree()
            elif text in os.listdir(f'{self.document_dir}'):
                QMessageBox.information(self, '경고', '파일 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, '취소', '페이지 생성을 취소하였습니다.', QMessageBox.StandardButton.Ok)
    def CreateWiki(self, dir:str, title:str):
        data = {}
        data['title'] = title
        data['index'] = []
        data['body'] = {}
        print(dir)
        with open(f'{dir}/{title}.wiki', 'w', encoding='utf-8') as file:
            json.dump(data, file)
    def makeWikiFile(self, title:str):
        if self.document_dir == self.root:
            print('루트 directory에는 생성할 수 없습니다.')
        elif 'Wiki' not in os.listdir(self.document_dir) or 'Wiki' not in self.document_dir:
            os.mkdir(f'{self.document_dir}/Wiki')
            createDir = f'{self.document_dir}/Wiki/'
            self.CreateWiki(createDir)
        elif 'Wiki' not in self.document_dir:
            createDir = f'{self.document_dir}/Wiki/'
            self.CreateWiki(createDir, title)
    def newWiki(self):
        text, ok = QInputDialog.getText(None, "새 위키의 이름을 입력해 주세요.", "새 위키 문서")
        if os.path.isfile(self.document_dir):
            self.document_dir = f'{'/'.join(self.document_dir.split('/')[0:-1])}/Wiki'
            self.makeWikiFile()
        elif ok:
            if 0 < self.document_dir.__len__() and not (f'{text}.wiki' in os.listdir(self.document_dir)):
                print('파일이 생성되었습니다.')
                self.makeWikiFile(text)
                
            elif f'{text}.wiki' in os.listdir(self.document_dir):
                QMessageBox.information(self, '경고', '파일 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, '취소', '페이지 생성을 취소하였습니다.', QMessageBox.StandardButton.Ok)
        self.UpdateTree()
    def UpdateTree(self):
        try:
            ch = [t.split('.')[0] for t in os.listdir(self.document_dir)]
            model = self.treeView.model()
            if model is None:
                return None
            elif model:
                nowChild = []
                selectModel = None
                for t in self.model.findItems(self.selectDir, Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive):
                    if t.text() == self.selectDir:
                        selectModel = t
                        for row_index in range(t.rowCount()):
                            nowChild.append(t.child(row_index, 0).text())
                print(ch)
                for t in ch:
                    print(t)
                    if t not in nowChild:
                        qt = QStandardItem(t)
                        if selectModel:
                            selectModel.appendRow(qt)
            else:
                self.Action_Type.connect(ProgrameAction.FailedTreeViewUpdate)
        except FileNotFoundError:
            pass
    def OpenWikiFiles(self, dir:str):
        self.ProjectConf.OpenWindow(dir)
    def OpenWindows(self, index:QModelIndex):
        child_index = index
        child_text = child_index.data()
        parents_index = child_index.parent()
        if parents_index.isValid():
            parents_text = parents_index.data()
            if parents_text not in self.document_dir:
                self.document_dir = f'{self.document_dir}/{parents_text}/{child_text}'
            elif parents_text in self.document_dir and child_text not in self.document_dir:
                self.document_dir = f'{self.document_dir}/{child_text}'
            self.DocumentDir.emit(self.document_dir)
        else:
            self.document_dir = self.root
            self.DocumentDir.emit(self.document_dir)
        t_dir = self.document_dir.split(child_text)[0]
        if os.path.exists(t_dir):
            for t in os.listdir(t_dir):
                if child_text in t:
                    if '.wiki' in t:
                        self.OpenWikiFiles(f"{t_dir}{t}")
                else:
                    pass
        else:
            print(1)
    def init_ui(self):
        if not self.blakTr:
            vlayout = QVBoxLayout()
            vlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_novel = QPushButton('새 그룹')
            new_novel.clicked.connect(self.makeGroup)
            new_page = QPushButton('새 페이지')
            new_page.clicked.connect(self.newPage)
            new_wiki = QPushButton('새 위키')
            new_wiki.clicked.connect(self.newWiki)
            menuView = QHBoxLayout()
            menuView.addWidget(new_novel)
            menuView.addWidget(new_page)
            menuView.addWidget(new_wiki)
            self.treeView.setModel(self.model)
            selection_model = self.treeView.selectionModel()
            selection_model.currentChanged.connect(self.selectGroupDir)
            self.treeView.doubleClicked.connect(self.OpenWindows)
            vlayout.addLayout(menuView)
            vlayout.addWidget(self.treeView)
            self.setLayout(vlayout)
        else:
            vlayout = QVBoxLayout()
            vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            new_novel = QPushButton('새 프로젝트')
            new_novel.clicked.connect(self.newProject)
            vlayout.addWidget(new_novel)
            self.setLayout(vlayout)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colorText))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.Action_Type.emit(ProgrameAction.FinishedTreeViewWork)
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
        print('포커스를 가졌습니다.')
        self.time.staRT()
    # 가장 먼저 호출되며 UI 객체에서 사용되는 기본 설정을 담당함.
    def __start__(self):
        self.windowPosX = self.config.windows_config['windows_pos_x']
        self.windowPosY = self.config.windows_config['windows_pos_y']
        self.windowSizeWidth = self.config.windows_config['windows_scale_width']
        self.windowSizeHeight = self.config.windows_config['windows_scale_height']
        self.programeInfo = self.config.programe_data['LastOpenDir']
        self.projectList = self.config.programe_data['ProjectDirs']
        if not os.path.isdir(self.programeInfo):
            self.dir = ''
        if self.programeInfo == '~/Documents':
            self.dir = ''
        elif self.programeInfo != '':
            self.dir = self.programeInfo
        elif self.programeInfo == r'C:\User':
            self.dir = ''
        else:
            self.dir = ''
        if self.dir != '' and self.dir != r'C\:User':
            self.trView = EMSWTreeView(self.dir, self.config)
        if self.dir == '':
            self.trView = EMSWTreeView('', self.config)
        self.ProgrameSignal = ProgrameAction.ProgrameStart
        self.makeMenu()
        self.setWindowTitle('EMSW')
        self.setGeometry(self.windowPosX, self.windowPosY, self.windowSizeWidth, self.windowSizeHeight)
        self.targetDir = ''
    def Update_windows_position(self):
        if (self.x != self.config.windows_config['windows_pos_x']) or (self.y != self.config.windows_config['windows_pos_y']):
            self.config.updatePosition(self.x, self.y)
    def Update_windows_Scale(self):
        if (self.width != self.config.windows_config['windows_scale_width']) or (self.height != self.config.windows_config['windows_scale_height']):
            self.config.updateScale(self.width, self.height)
    def __setTreeView__(self):
        self.trView.updateSize(self.config.windows_config['treeview_width'], self.config.windows_config['treeview_height'])
    # TreeView 변동 사항을 검사하는 Trigger
    def setDocument(self, recived):
        self.targetDir = recived
    # TreeView를 감시하는 매소드
    def ListenTreeView(self):
        if self.trView:
            self.trView.Action_Type.connect(self.getProgrameSignal)
            if self.ProgrameSignal == ProgrameAction.SelectTreeView:
                self.trView.DocumentDir.connect(self.setDocument)
                self.ProgrameSignal = ProgrameAction.ProgrameDuring
            elif self.ProgrameSignal == ProgrameAction.UpdateTreeView:
                print(self.dir)
                self.trView.setRoot(self.dir)
                self.trView.resetTree()
                self.ProgrameSignal = ProgrameAction.SetTheProjectDir
            elif self.ProgrameSignal == ProgrameAction.FinishedTreeViewWork:
                self.ProgrameSignal = ProgrameAction.ProgrameDuring
    # update에서 가장 빨리 호출되는 메소드.
    # 주로 데이터의 업데이트, 또는 갱신을 담당하는 메소드 또는 함수가 연결된다.
    def __fixed_update__(self):
        self.FixedUpdate()
    def FixedUpdate(self):
        self.ListenTreeView()
        if self.config.programe_data['LastOpenDir'] == '' or self.config.programe_data['LastOpenDir'] is None:
            pass
        elif self.ProgrameSignal == ProgrameAction.SetTheProjectDir:
            self.trView.setRoot(self.config.programe_data['LastOpenDir'])
            self.ProgrameSignal = ProgrameAction.UpdateUI
        else:
            self.ProgrameSignal = ProgrameAction.ProgrameDuring
    # fixedUpdate 호출 이전에 반드시 먼저 호출되어야 하는 설정 변수들과 Windows 환경 변수들
    # 프로그램 설정 관련
    def windowsUpdate(self):
        pos = self.pos()
        scale = self.geometry()
        if ((pos.x() != self.config.windows_config['windows_pos_x']) or (pos.y() != self.config.windows_config['windows_pos_y'])):
            self.config.updatePosition(pos.x(), pos.y())
        if ((scale.width() != self.config.windows_config['windows_scale_width']) or (scale.height() != self.config.windows_config['windows_scale_height'])):
            self.config.updateScale(scale.width(), scale.height())
        try:
            if self.trView.geometry().width() != self.config.windows_config['treeview_width'] and self.trView.geometry().height() != self.config.windows_config['treeview_height'] and self.programeInfo == ProgrameAction.ProgrameDuring:
                self.ProgrameSignal = ProgrameAction.UpdateUI
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
    # 가장 나중에 업데이트되는 메소드. 주로 후처리 Signal을 처리한다.
    def __last_update__(self):
        self.LastUpdate()
        self.TreeViewScaleUpdate()
    # 가장 나중에 업데이트 되는 것. 일반적으로 데이터를 검증하는 작업을 처리한다.
    def LastUpdate(self):
        if self.ProgrameSignal == ProgrameAction.OpenProjectSuccess:
            if self.programeInfo != self.dir:
                self.programeInfo = self.dir
            self.trView.setRoot(self.dir)
            self.ProgrameSignal = ProgrameAction.UpdateTreeView
    # TreeView 사이즈를 변경하는 메소드 (일반적으로 MainView과 비교하여 10의 여백을 갖는다.)
    # LastUpdate에서 호출
    def TreeViewScaleUpdate(self):
        tr_width = self.config.windows_config['windows_scale_width'] - 20
        tr_height = self.config.windows_config['windows_scale_height'] - 20
        self.config.UpdateTreeViewScale(tr_width, tr_height)
        self.trView.updateSize(tr_width, tr_height)
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
        createDocuments = QAction('새 문서', self)
        createDocuments.triggered.connect(self.newDocumentsAction)
        openWiki = QAction("위키 열기", self)
        openWiki.triggered.connect(self.openWikitree)
        menu.addAction(open_menu)
        menu.addAction(project_menu)
        menu.addAction(createDocuments)
    # 위키트리 뷰를 여는 메소드
    def openWikitree(self):
        pass
    # 프로젝트를 여는 매뉴를 호출하는 메소드
    def openProject(self):
        print('작업폴더 열기 작업이 수행되었습니다.')
        opePro = OpenProject(self.x(), self.y(), 580, 120)
        opePro.Project_dir.connect(self.getProjectDirectory)
        opePro.Action_Type.connect(self.getProgrameSignal)
        opePro.exec()
        print(f'작업폴더 열기 작업이 완료되었습니다. : {self.dir}')
        self.ProgrameSignal = ProgrameAction.UpdateTreeView
    # 프로젝트를 여는 메뉴를 호출하는 메소드
    def newProjectAction(self):
        print('프로젝트 추가 작업이 수행되었습니다.')
        crepro = CreateProject(self.x(), self.y(), 580, 120)
        crepro.Project_dir.connect(self.getProjectDirectory)
        crepro.Action_Type.connect(self.getProgrameSignal)
        crepro.exec()
        print(f'프로젝트 추가 작업이 완료되었습니다. : {self.dir}')
        self.ProgrameSignal = ProgrameAction.UpdateTreeView
    def newDocumentsAction(self):
        print('파일 추가 작업이 수행되었습니다.')
        if self.targetDir == '':
            QMessageBox.information(self, '취소', '올바르지 않은 선택이 발생했습니다.', QMessageBox.StandardButton.Ok)
        else:
            text, ok = QInputDialog.getText(None, '새 페이지의 이름을 입력해 주세요', '새 페이지')
            if ok:
                dir = f'{self.targetDir}/{text}.txt'
                print(self.targetDir)
                if os.path.isdir(self.targetDir) and not f"{text}.txt" in os.listdir(self.targetDir):
                    open(dir, 'w', encoding='utf-8').writelines('')
                elif os.path.isfile(f"{self.targetDir}.txt"):
                    t = f"{''.join(self.targetDir.split('/')[0::-1])}/{text}.txt"
                    open(t, 'w', encoding='utf-8').writelines('')
                elif text in os.listdir(self.targetDir):
                    QMessageBox.Information(self, '경고', '페이지 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(self, '취소', '페이지 생성을 취소하셨습니다.', QMessageBox.StandardButton.Ok)
        self.ProgrameSignal = ProgrameAction.UpdateTreeView
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
        mainboard = QWidget()
        mainboard.setLayout(hLayout)
        self.setCentralWidget(mainboard)
        self.show()
    # 창이 닫힐때 실행되는 동작을 정의한다.
    # 프로젝트가 닫히는 절차를 정의한다.
    def closeEvent(self, event):
        print(self.config.getPosition())
        print(self.width, self.height)
        self.config.updateScale(self.width, self.height)