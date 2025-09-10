import json, os

class conf:
    def __init__(self):
        if 'data' not in os.listdir('./'):
            os.mkdir('./data')
        dir_lists = os.listdir('./data')
        if 'windows_config.json' not in dir_lists:
            self.startWindows()
        if 'ProjectDirectories' not in dir_lists:
            self.programeLoad()
        if os.path.isfile('./data/windows_config.json'):
            with open('./data/windows_config.json', mode='r', encoding='utf-8') as file:
                self.windows_config = json.load(file)
        if os.path.isfile('./data/ProjectDirectories.json'):
            with open('./data/ProjectDirectories.json', mode='r', encoding='utf-8') as file:
                self.programe_data = json.load(file)
        self.updated = False
    # windows_configs.json 파일 체크를 수행하는 메소드
    def startWindows(self):
        df = {}
        df['windows_pos_x'] = 100
        df['windows_pos_y'] = 100
        df['windows_scale_width'] = 800
        df['windows_scale_height'] = 650
        df['language'] = 'ko'
        df['model'] = 'GPT-OSS:20b'
        df['project directory'] = './ProgrameData'
        with open('./data/windows_config.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    # ProjectDirectories.json 파일 체크를 수행하는 메소드
    def programeLoad(self):
        df = {}
        df['ProjectDirs'] = [r'C:\Users']
        df['LastOpenDir'] = r'C:\Users'
        with open('./data/ProjectDirectories.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    # pos를 업데이트하는 메소드
    def updatePosition(self, x:int, y:int):
        self.windows_config['windows_pos_x'] = x
        self.windows_config['windows_pos_y'] = y
        self.updated = True
    # scale을 업데이트하는 메소드
    def updateScale(self, width:int, height:int):
        self.windows_config['windows_scale_width'] = width
        self.windows_config['windows_scale_height'] = height
        self.updated = True
    def AppenddProjectDir(self, dir:str):
        dirs = list(self.programe_data['ProjectDirs'])
        if dir not in dirs:
            dirs.append(dir)
        if dir != self.programe_data['LastOpenDir']:
            self.programe_data['LastOpenDir'] = dir
        self.updated = True
    def __del__(self):
        if self.updated:
            with open('./data/windows_config.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            with open('./data/ProjectDirectories.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
