from PySide6.QtWidgets import (QMainWindow, QMenuBar, QWidget,
                               QTreeView, QHBoxLayout, QVBoxLayout,
                               QInputDialog, QMessageBox, QLabel,
                               QTextBrowser, QSplitter)
from PySide6.QtCore import (Signal, QTimer, Qt, QModelIndex)
from PySide6.QtGui import (QAction, QStandardItemModel, QStandardItem)
from Config.config import WikiDocuments, ProgrameAction

import json

class WikiIndex(QWidget):
    Action_Type = Signal(ProgrameAction)
    def __init__(self, title:str, config:WikiDocuments):
        super().__init__()
        self.config = config
        self.title = title
        self.model = QStandardItemModel()
        self.CreateWindows()
        self.__init_ui__()
    def CreateWindows(self):
        self.IndexView = QTreeView()
        self.makeIndex()
    # 목차를 만듭니다.
    def makeIndex(self):
        if self.model is not None:
            self.model.clear() # 기존 모델 초기화
            parents = QStandardItem(self.title)
            for t in self.config.getKeys('index'):
                children = QStandardItem(t)
                parents.appendRow(children)
            self.model.appendRow(parents)
            self.IndexView.setModel(self.model)
            self.IndexView.expandAll()
    # 목차에 새 항목을 추가하고 모델을 재생성합니다.
    def addIndex(self, new:str):
        if new not in self.config.getKeys('index'):
            self.config.AppendIndex(new)
            self.resetIndex()
            self.makeIndex()
        else:
            self.resetIndex()
            self.makeIndex()
        print('addIndex')
    # 모델을 초기화 합니다.
    def resetIndex(self):
        if self.model:
            self.model.clear()
    def __init_ui__(self):
        vLayout = QVBoxLayout()
        layout = QHBoxLayout()
        if type(self.IndexView) is QTreeView:
            self.IndexView.setHeaderHidden(True)
            vLayout.addWidget(self.IndexView)

        layout.addLayout(vLayout)
        
        self.setLayout(layout)

class WikiMainWindow(QWidget):
    def __init__(self, config:WikiDocuments):
        self.config = config
    
class WikiView(QMainWindow):
    Action_Type = Signal(ProgrameAction)
    Close_Title = Signal(str)
    def __init__(self, dir:str, name : str):
        super().__init__()
        self.Update = False
        self.dir = dir
        self.title = name
        self.IndexView = None
        self.config = None
        self.__start__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__update__)
        self.timer.start(16)

        self.init_UI()
    def __start__(self):
        self.setWindowTitle(self.title)
        self.Load_Data()
        self.IndexView = WikiIndex(self.title, self.config)
        self.programeSignal = ProgrameAction.SubWindowsOpened
        self.setWindowTitle(self.title)

        self.makeMenu()
    #data를 로드하는 메소드
    def Load_Data(self):
        if self.config is None:
            self.config = WikiDocuments(self.dir)
        
        self.setGeometry(self.config.getKeys('xPos'), self.config.getKeys['yPos'], self.config.getKeys['width'], self.config.getKeys['height'])
        print('Load Data')
    def WindowScaleCheck(self):
        
        if self.data['xPos'] != self.x():
            self.data['xPos'] = self.x()
            self.Update = True
        if self.data['yPos'] != self.y():
            self.data['yPos'] = self.y()
            self.Update = True
        if self.data['width'] != self.width():
            self.data['width'] = self.width()
            self.Update = True
        if self.data['height'] != self.height():
            self.data['height'] = self.height()
            self.Update = True
    def Action_Progress(self):
        if self.programeSignal is ProgrameAction.UpdateWikiTreeView:
            self.Signal_Update(ProgrameAction.UpdateWikiView)
            print('Action Progress Update Wiki Tree View')
        elif self.programeSignal is ProgrameAction.UpdateWikiData:
            self.IndexView.repaint()
            self.Signal_Update(ProgrameAction.UpdateWikiView)
            print('Action Progress Update Wiki Data')
    def __fixed_update__(self):
        self.Action_Progress()
        if self.Update:
            self.Update = False
    def Update_Action_Progress(self):
        if self.programeSignal is ProgrameAction.UpdateWikiView:
            print(self.IndexView.index.__len__() == self.index.__len__())
            self.Signal_Update(ProgrameAction.SubWindowsDuring)
            print('Update Action Progress update wiki view')
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
            self.Signal_Update(ProgrameAction.UpdateWikiData)
            print('Signal check Append Index')
    def makeMenu(self):
        Menu = self.menuBar()
        self.editMenuBar(Menu.addMenu('Edit'))
        print('make Menu')
    # edit Menu를 추가하는 메소드
    def editMenuBar(self, menu:QMenuBar):
        addIndex = QAction('목차 추가', self)
        addIndex.triggered.connect(self.AppendIndex)

        menu.addAction(addIndex)
        print('edit menu bar')
    # index를 추가하는 메소드
    def AppendIndex(self):
        text, ok = QInputDialog.getText(self, '새 목차', '새 목차를 입력해 주세요')
        if ok:
            l = True
            for t in self.data['index']:
                if t == text:
                    l = False
            if l:
                self.data['index'].append(text)
                self.update_index()
                self.IndexView.addIndex(text)
                self.Signal_Update(ProgrameAction.AppendIndex)
                QMessageBox.information(self, '확인', '목차가 추가되었습니다.', QMessageBox.StandardButton.Ok)
        elif text in self.data['index']:
            QMessageBox.information(self, '경고', '목차 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
            print('not append index')
        else:
            QMessageBox.information(self, '경고', '알 수 없는 오류가 발생했습니다.', QMessageBox.StandardButton.Ok)
            print('programe wrong')
    # Prgraome Signal을 체인지하고, Program Action의 값을 emit하는 메소드
    def Signal_Update(self, signal:ProgrameAction):
        self.programeSignal = signal
        self.Action_Type.emit(signal)
        print('signal update')
    def init_UI(self):

        if self.IndexView is None:
            QMessageBox.critical(self, '오류', 'UI 위젯 초기화 실패')
            self.Signal_Update(ProgrameAction.UpdateWikiTreeView)
            return
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.IndexView)

        splitter.setStretchFactor(0, 1)
        
        self.setCentralWidget(splitter)
        self.IndexView.IndexView.clicked.connect(self.on_index_clicked)
        self.show()
    def on_index_clicked(self, index:QModelIndex):
        item = self.IndexView.model.itemFromIndex(index)
        if item and item.parent(): 
            page_title = item.text()
            print(f"Clicked page: {page_title}")
            self.ContentView.show_page(page_title)
    def focusOutEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop() # <--- [수정] self.time -> self.timer
        return super().focusOutEvent(event)
    def closeEvent(self, event):
        print(f"x : {self.x()} \ny : {self.y()} \nwidth : {self.width()} \nheight : {self.height()} \nindex : {self.data['index']} \nbody : {self.data['body']}")
        self.WindowScaleCheck()
        self.Action_Type.emit(ProgrameAction.SubWindowsClosed)
        self.Close_Title.emit(self.title)
        del self.config