from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget)

import sys
from Config.config import conf


class WikiView(QMainWindow):
    def __init__(self, config:conf, name : str):
        super().__init__()
        # conf를 입력받는다.
        self.config = config
        self.title = name
        self.__start__()

    def __start__(self):
        self.config.checkTag('WikiTitle', self.title)
        self.config.checkTag('Wiki width Size', 600)
        self.config.checkTag('wiki height Size', 300)
        self.config.checkTag('Wiki pos X', 100)
        self.config.checkTag('Wiki pos Y', 100)
    def init_UI(self):
        self.show()

# 위키 Tree를 테스트하기 위해 사용하는 클래스
# 일반적으로 타이머의 
if __name__ == '__main__':
    config = conf()
    app = QApplication(sys.argv)
    w_app = WikiView(config)
    app.exec()