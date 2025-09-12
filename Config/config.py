import json, os

class conf:
    def __init__(self):
        if 'data' not in os.listdir('./'):
            os.mkdir('./data')
        dir_lists = os.listdir('./data')
        self.openError = False
        if 'windows_config.json' not in dir_lists:
            self.startWindows()
        if 'ProjectDirectories.json' not in dir_lists:
            self.programeLoad()
        try:
            if os.path.isfile('./data/windows_config.json'):
                with open('./data/windows_config.json', mode='r', encoding='utf-8') as file:
                    self.windows_config = json.load(file)
        except:
            self.open
        try:
            if os.path.isfile('./data/ProjectDirectories.json'):
                with open('./data/ProjectDirectories.json', mode='r', encoding='utf-8') as file:
                    self.programe_data = json.load(file)
        except:
            self.openError = True
        self.checkConfig()
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
        df['treeview_width'] = 80
        df['treeviwe_height'] = self.windows_config['windows_scale_width'] / 5
        df['treeview_height'] = self.windows_config['windows_scale_height'] - 50
        with open('./data/windows_config.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    # ProjectDirectories.json 파일 체크를 수행하는 메소드
    def programeLoad(self):
        df = {}
        df['ProjectDirs'] = [r'C:\Users']
        df['LastOpenDir'] = r'C:\Users'
        with open('./data/ProjectDirectories.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    # jsonfile을 확인하고, 최종적으로 정정하는 메소드
    def checkConfig(self):
        if self.openError:
            self.startWindows()
            self.programeLoad()
        if 'treeview_width' not in self.windows_config.keys():
            self.windows_config['treeview_width'] = self.windows_config['windows_scale_width'] / 5
        if 'treeviwe_height' not in self.windows_config.keys():
            self.windows_config['treeview_height'] = self.windows_config['windows_scale_height'] - 50
        if 'widget_align' not in self.windows_config.keys():
            self.windows_config['widget_align'] = 'left'
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
        print(dirs)
        if dir in dirs:
            pass
        else:
            dirs.append(dir)
            self.programe_data['ProjectDirs'] = dirs
        if dir != self.programe_data['LastOpenDir']:
            self.programe_data['LastOpenDir'] = dir
        self.updated = True
    def __del__(self):
        print(self.programe_data.values())
        if self.updated:
            with open('./data/windows_config.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            with open('./data/ProjectDirectories.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
