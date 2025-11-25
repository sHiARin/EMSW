from EMSW_UI.EMSW_MainUI import EMSW
from EMSW_UI.core.resource import ProjectConfig
from PySide6.QtWidgets import QApplication

import sys, os, json

def main():
    app = QApplication(sys.argv)
    if 'ProjectData' not in os.listdir('./'):
        m_app = EMSW(ProjectConfig())
    else:
        with open('./ProjectData', 'r', encoding='utf-8') as file:
            data = file.read()
            key = data.keys()
            if 'LastOpenProject' in 
    app.exec()

if __name__ == '__main__':
    main()