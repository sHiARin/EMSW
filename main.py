from EMSW_UI.EMSW_MainUI import EMSW

from PySide6.QtWidgets import QApplication

import sys

def main():
    app = QApplication(sys.argv)
    m_app = EMSW(150, 150, 1200, 850)
    app.exec()

if __name__ == '__main__':
    main()