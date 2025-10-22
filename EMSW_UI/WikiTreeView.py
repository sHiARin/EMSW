from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget)

import sys
from Config.config import conf

class WikiView(QMainWindow):
    def __init__(self, config:conf):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w_app = WikiView()
    app.exec()