from EMSW_UI.EMSW_MainUI import EMSW
from EMSW_UI.core.resource import ProjectConfig
from PySide6.QtWidgets import QApplication

import sys, os, json

if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    # 프로젝트 로드 시뮬레이션
    project = ProjectConfig()
    
    window = EMSW(project)
    window.projectOpen = True # 테스트를 위해 강제 오픈 설정
    
    sys.exit(app.exec())