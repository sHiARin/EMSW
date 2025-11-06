from PySide6.QtWidgets import (QMainWindow, QMenuBar, QWidget,
                               QTreeView)
from PySide6.QtCore import (Signal, QTimer)
from PySide6.QtGui import (QAction)
from Config.config import ProgrameAction

import json

class WikiIndex(QWidget):
    def __init__(self):
        pass
    
class WikiView(QMainWindow):
    Action_Type = Signal(ProgrameAction)
    Close_Title = Signal(str)
    def __init__(self, dir:str, name : str):
        super().__init__()
        self.Update = False
        self.dir = dir
        self.title = name
        self.data = None
        self.__start__()
        self.time = QTimer(self)
        self.time.timeout.connect(self.__update__)
        self.time.start(16)
        self.init_UI()
    def __start__(self):
        self.programeSignal = ProgrameAction.SubWindowsOpened
        self.setWindowTitle(self.title)
        with open(self.dir, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
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
        print(f"x : {self.x()} \ny : {self.y()} \nwidth : {self.width()} \nheight : {self.height()}")
        self.setGeometry(self.data['xPos'], self.data['yPos'], self.data['width'], self.data['height'])
        self.IndexView = WikiIndex()
        self.makeMenu()
    def Save_Data(self):
        with open(self.dir, 'w', encoding='utf-8') as file:
            json.dump(self.data, file)
    def WindowScaleCheck(self):
        self.data['xPos'] = self.x()
        self.data['yPos'] = self.y()
        self.data['width'] = self.width()
        self.data['height'] = self.height()
        self.Update = True
    def __fixed_update__(self):
        if self.Update:
            self.Save_Data()
            self.Update = False
    def __update__(self):
        self.__fixed_update__()
        self.__last_update__()
    def __last_update__(self):
        self.WindowScaleCheck()
    def makeMenu(self):
        Menu = self.menuBar()
        self.editMenuBar(Menu.addMenu('Edit'))
    # edit Menu를 추가하는 메소드
    def editMenuBar(self, menu:QMenuBar):
        addIndex = QAction('목차 추가', self)
        addIndex.triggered.connect(self.AppendIndex)

        menu.addAction(addIndex)
    def AppendIndex(self):
        print('Append Index')
    def init_UI(self):
        self.show()
    def focusOutEvent(self, event):
        self.time.stop()
        return super().focusOutEvent(event)
    def closeEvent(self, event):
        print(f"x : {self.x()} \ny : {self.y()} \nwidth : {self.width()} \nheight : {self.height()}")
        self.Action_Type.emit(ProgrameAction.SubWindowsClosed)
        self.Close_Title.emit(self.title)
        self.Save_Data()