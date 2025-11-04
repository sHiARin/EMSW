from EMSW_UI.EMSW_MainUI import EMSW
from Config.config import conf
from PySide6.QtWidgets import QApplication

import sys

def main():
    config = conf()
    app = QApplication(sys.argv)
    m_app = EMSW(config)
    app.exec()

if __name__ == '__main__':
    main()