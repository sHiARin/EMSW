from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget)

from Config.config import conf

import sys



class WikiView(QMainWindow):
    def __init__(self, config:conf, name : str):
        super().__init__()
        self.config = config
        self.title = name
        self.__start__()
    def __checkingTag__(self):
        self.config.checkTag('Wiki Title', self.title)
        self.config.checkTag('Wiki width Size', 600)
        self.config.checkTag('Wiki height Size', 300)
        self.config.checkTag('Wiki pos X', 100)
        self.config.checkTag('Wiki pos Y', 100)
    def __Read_Windows_infomation__(self):
        self.wiki_x = self.config.getValueToTag('Wiki pos X')
        self.wiki_y = self.config.getValueToTag('Wiki pos Y')
        self.wiki_width = self.config.getValueToTag('Wiki width Size')
        self.wiki_height = self.config.getValueToTag('Wiki height Size')
        self.wiki_title = self.config.getValueToTag('Wiki Title')
    def __start__(self):
        self.__checkingTag__()
    def init_UI(self):
        self.show()
