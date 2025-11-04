from PySide6.QtWidgets import (QMainWindow, QWidget)
from PySide6.QtCore import (Signal, QTimer)
from Config.config import ProgrameAction

import json

class WikiView(QMainWindow):
    Action_Type = Signal(ProgrameAction)
    Close_Title = Signal(str)
    def __init__(self, dir:str, name : str):
        super().__init__()
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
        with open(self.dir, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        print(type(self.data))
    def __fixed_update__(self):
        pass
    def __update__(self):
        self.__fixed_update__()
    def init_UI(self):
        self.setGeometry(100, 100, 100, 100)
        self.show()
    def focusOutEvent(self, event):
        self.time.stop()
        return super().focusOutEvent(event)
    def closeEvent(self, event):
        self.Action_Type.emit(ProgrameAction.SubWindowsClosed)
        self.Close_Title.emit(self.title)