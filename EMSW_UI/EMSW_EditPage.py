from PySide6.QtWidgets import (QMainWindow, QMenuBar, QWidget,
                               QTreeView, QHBoxLayout, QVBoxLayout,
                               QInputDialog, QMessageBox, QLabel)
from PySide6.QtCore import (Signal, QTimer, Qt)
from PySide6.QtGui import (QAction, QStandardItemModel, QStandardItem)
from Config.config import ProgrameAction

import json

class WikiIndex(QWidget):
    Action_Type = Signal(ProgrameAction)
    def __init__(self, index:list, title):
        super().__init__()
        self.index = index
        self.title = title
        self.CreateWindows()
        self.__init_ui__()
    def CreateWindows(self):
        self.IndexView = QTreeView()
        self.makeIndex()
    def makeIndex(self):
        parents = self.IndexView.model()
        if parents is None:
            parents = QStandardItemModel()
            for t in self.index:
                children = QStandardItem(t)
                parents.appendRow(children)
            self.IndexView.setModel(parents)
    def addIndex(self, new:str):
        if new not in self.index:
            self.index.append(new)
    def __init_ui__(self):
        vLayout = QVBoxLayout()
        layout = QHBoxLayout()
        if type(self.IndexView) is QTreeView:
            self.IndexView.setHeaderHidden(True)
            vLayout.addWidget(QLabel(self.title))
            vLayout.addWidget(self.IndexView)

        layout.addLayout(vLayout)
        
        self.setLayout(layout)

class WikiMainWindow(QWidget):
    def __init__(self, body:dict):
        self.body = body
    
class WikiView(QMainWindow):
    Action_Type = Signal(ProgrameAction)
    Close_Title = Signal(str)
    def __init__(self, dir:str, name : str):
        super().__init__()
        self.Update = False
        self.dir = dir
        self.title = name
        self.IndexView = None
        self.__start__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__update__)
        self.timer.start(16)
        self.init_UI()
    def __start__(self):
        self.setWindowTitle(self.title)
        self.Load_Data()
        self.index = self.data['index']
        self.IndexView = WikiIndex(self.index, self.title)
        self.programeSignal = ProgrameAction.SubWindowsOpened
        self.setWindowTitle(self.title)

        self.makeMenu()
    #data를 로드하는 메소드
    def Load_Data(self):
        with open(self.dir, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        if self.data is None:
            self.data = {}
        key = self.data.keys()
        if 'height' not in key:
            self.Update = True
            self.data['height'] = 100
        if 'width' not in key:
            self.Update = True
            self.data['width'] = 100
        if 'xPos' not in key:
            self.Update = True
            self.data['xPos'] = 100
        if 'yPos' not in key:
            self.Update = True
            self.data['yPos'] = 100
        self.setGeometry(self.data['xPos'], self.data['yPos'], self.data['width'], self.data['height'])
        if 'index' not in self.data.keys():
            self.data['index'] = []
        print(f"x : {self.x()} \ny : {self.y()} \nwidth : {self.width()} \nheight : {self.height()} \nindex : {self.data['index']}")

    # 변경된 데이터를 저장하는 메소드
    def Save_Data(self):
        with open(self.dir, 'w', encoding='utf-8') as file:
            json.dump(self.data, file)
    def WindowScaleCheck(self):
        self.data['xPos'] = self.x()
        self.data['yPos'] = self.y()
        self.data['width'] = self.width()
        self.data['height'] = self.height()
        self.Update = True
    def Action_Progress(self):
        if self.programeSignal == ProgrameAction.UpdateWikiTreeView:
            print('Action Progress')
            self.Signal_Update(ProgrameAction.UpdateWikiView)
        elif self.programeSignal == ProgrameAction.UpdateWikiData:
            self.repaint()
            self.Signal_Update(ProgrameAction.SubWindowsDuring)
    def __fixed_update__(self):
        self.Action_Progress()
        if self.Update:
            self.Save_Data()
            self.Update = False
    def Update_Action_Progress(self):
        if self.programeSignal is ProgrameAction.UpdateWikiView:
            self.update()
            self.repaint()
            self.Signal_Update(ProgrameAction.SubWindowsDuring)
            print('Update Action Progress')
    def __update__(self):
        self.__fixed_update__()
        self.Update_Action_Progress()
        self.__last_update__()
    def __last_update__(self):
        self.WindowScaleCheck()
        self.Signal_Check()
    def Signal_Check(self):
        if self.programeSignal is ProgrameAction.AppendIndex:
            self.Update = True
    def makeMenu(self):
        Menu = self.menuBar()
        self.editMenuBar(Menu.addMenu('Edit'))
    # edit Menu를 추가하는 메소드
    def editMenuBar(self, menu:QMenuBar):
        addIndex = QAction('목차 추가', self)
        addIndex.triggered.connect(self.AppendIndex)

        menu.addAction(addIndex)
    # index를 추가하는 클래스
    def AppendIndex(self):
        text, ok = QInputDialog.getText(self, '새 목차', '새 목차를 입력해 주세요')
        if ok:
            l = True
            for t in self.index:
                if t == text:
                    l = False
            if l:
                self.index.append(text)
                self.IndexView.addIndex(text)
                self.Signal_Update(ProgrameAction.AppendIndex)
                QMessageBox.information(self, '확인', '목차가 추가되었습니다.', QMessageBox.StandardButton.Ok)
        elif text in self.index:
            QMessageBox.information(self, '경고', '목차 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, '경고', '알 수 없는 오류가 발생했습니다.', QMessageBox.StandardButton.Ok)
    # Prgraome Signal을 체인지하고, Program Action의 값을 emit하는 메소드
    def Signal_Update(self, signal:ProgrameAction):
        self.programeSignal = signal
        self.Action_Type.emit(signal)
    def init_UI(self):
        WindowLayout = QHBoxLayout()
        IndexLayout = QVBoxLayout()
        print(self.IndexView is not None)
        if type(self.IndexView) is WikiIndex:
            IndexLayout.addWidget(self.IndexView)
        else:
            self.Signal_Update(ProgrameAction.UpdateWikiTreeView)
        WindowLayout.addLayout(IndexLayout)
        centralWidget = QWidget()
        centralWidget.setLayout(WindowLayout)
        self.setCentralWidget(centralWidget)
        self.show()
    def focusOutEvent(self, event):
        self.time.stop()
        return super().focusOutEvent(event)
    def closeEvent(self, event):
        print(f"x : {self.x()} \ny : {self.y()} \nwidth : {self.width()} \nheight : {self.height()}")
        self.WindowScaleCheck()
        self.Action_Type.emit(ProgrameAction.SubWindowsClosed)
        self.Close_Title.emit(self.title)
        self.Save_Data()