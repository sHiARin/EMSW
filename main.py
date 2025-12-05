from PySide6.QtWidgets import QApplication
from EMSW_UI.core.resource import ProjectConfig, GlobalWorld
from EMSW_UI.EMSW_MainUI import EMSW

import os, json, sys

def CreateProject(dir:str):
    if not GlobalWorld().is_ollama_running():
        result = GlobalWorld().start_ollama()
        if not result:
            print('cannot start ollama')
            exit(0)
    data = None

    if os.path.exists(dir):
        with open(dir, 'r') as file:
            data = json.load(file)
    elif not os.path.exists(dir):
        data = {}
        data["Last Open Project"] = ""
        data["Open Projects"] = []
        print(data)
        with open(dir, 'w', encoding='utf-8') as file:
            json.dump(data, file)
    return ProjectConfig(data, 'Asia/Seoul')

def main(argv):
    dir = fr"{os.getcwd()}\Data\programeData.data"
    project = CreateProject(dir)

    app = QApplication(argv)
    emsw = EMSW(project=project)
    app.exec()

if __name__ == "__main__":
    main(sys.argv)