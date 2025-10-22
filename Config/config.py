import json, os, platform

class conf:
    def __init__(self):
        self.updated = False
        self.windows_config = None
        self.programe_data = None
        if "Darwin" == platform.system():
            if 'data' not in os.listdir('./'):
                os.mkdir('./data')
            dir_lists = os.listdir('./data')
            print(dir_lists)
            self.openError = False
            if 'windows_config_mac.json' not in dir_lists:
                self.startWindowsMac()
            if 'ProjectDirectories_win.json' not in dir_lists:
                self.programeLoadMac()
            try:
                if os.path.isfile('./data/windows_config_mac.json'):
                    with open('./data/windows_config_mac.json', mode='r', encoding='utf-8') as file:
                        self.windows_config = json.load(file)
            except:
                self.openError = True
                print(self.openError)
            try:
                if os.path.isfile('./data/ProjectDirectories_mac.json'):
                    with open('./data/ProjectDirectories_mac.json', mode='r', encoding='utf-8') as file:
                        self.programe_data = json.load(file)
            except:
                self.openError = True
                print(self.openError)
            self.checkConfig_Mac()
        elif "Windows" == platform.system():
            if 'data' not in os.listdir('./'):
                os.mkdir('./data')
            dir_lists = os.listdir('./data')
            self.openError = False
            if 'windows_config_win.json' not in dir_lists:
                self.startWindowsWin()
            if 'ProjectDirectories_win.json' not in dir_lists:
                self.programeLoadWin()
            try:
                if os.path.isfile('./data/windows_config_win.json'):
                    with open('./data/windows_config_win.json', mode='r', encoding='utf-8') as file:
                        self.windows_config = json.load(file)
            except:
                print('error!')
            try:
                if os.path.isfile('./data/ProjectDirectories_win.json'):
                    with open('./data/ProjectDirectories_win.json', mode='r', encoding='utf-8') as file:
                        self.programe_data = json.load(file)
            except:
                self.openError = True
            self.checkConfig_Win()
    # windows_configs_win.json 파일 체크를 수행하는 메소드
    def startWindowsMac(self):
        df = {}
        df['windows_pos_x'] = 100
        df['windows_pos_y'] = 100
        df['windows_scale_width'] = 800
        df['windows_scale_height'] = 650
        df['language'] = 'ko'
        df['model'] = 'GPT-OSS:20b'
        df['treeview_width'] = 80
        df['treeviwe_height'] = df['windows_scale_width'] / 5
        df['treeview_height'] = df['windows_scale_height'] - 50
        with open('./data/windows_config_mac.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    def programeLoadMac(self):
        df = {}
        df['ProjectDirs'] = ['~/Documents']
        df['LastOpenDir'] = '~/Documents'
        with open('./data/ProjectDirectories_mac.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    def startWindowsWin(self):
        df = {}
        df['windows_pos_x'] = 100
        df['windows_pos_y'] = 100
        df['windows_scale_width'] = 800
        df['windows_scale_height'] = 650
        df['language'] = 'ko'
        df['model'] = 'GPT-OSS:20b'
        df['treeview_width'] = 80
        df['treeviwe_height'] = df['windows_scale_width'] / 5
        df['treeview_height'] = df['windows_scale_height'] - 50
        with open('./data/windows_config_win.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
        self.windows_config = df
    # ProjectDirectories_win.json 파일 체크를 수행하는 메소드
    def programeLoadWin(self):
        df = {}
        df['ProjectDirs'] = [r'C:\Users']
        df['LastOpenDir'] = r'C:\Users'
        with open('./data/ProjectDirectories_win.json', 'w', encoding='utf-8') as file:
            json.dump(df, file)
    # jsonfile을 확인하고, 최종적으로 정정하는 메소드
    # windows 전용 메소드
    def checkConfig_Win(self):
        if self.openError:
            self.startWindowsWin()
            self.programeLoadWin()
            if 'treeview_width' not in self.windows_config.keys():
                self.windows_config['treeview_width'] = self.windows_config['windows_scale_width'] / 5
            if 'treeview_height' not in self.windows_config.keys():
                self.windows_config['treeview_height'] = self.windows_config['windows_scale_height'] - 50
            if 'widget_align' not in self.windows_config.keys():
                self.windows_config['widget_align'] = 'left'
        elif not self.openError and self.windows_config is not None and self.programe_data is not None:
            if 'treeview_width' not in self.windows_config.keys():
                self.windows_config['treeview_width'] = self.windows_config['windows_scale_width'] / 5
            if 'treeview_height' not in self.windows_config.keys():
                self.windows_config['treeview_height'] = self.windows_config['windows_scale_height'] - 50
            if 'widget_align' not in self.windows_config.keys():
                self.windows_config['widget_align'] = 'left'
            if 'EditTextWindow' not in self.windows_config.keys():
                self.windows_config['EditTextWindow'] = []
        else:
            print('None Exception')
    # jsonFile을 확인하고, 최종적으로 정정하는 메소드
    # Mac 전용 메소드
    def checkConfig_Mac(self):
        print(self.openError)
        if self.openError:
            self.startWindowsMac()
            self.programeLoadMac()
            if self.windows_config == None:
                print('Not Dictionary is here')
            if 'treeview_width' not in self.windows_config.keys():
                self.windows_config['treeview_width'] = self.windows_config['windows_scale_width'] / 5
            if 'treeview_height' not in self.windows_config.keys():
                self.windows_config['treeview_height'] = self.windows_config['windows_scale_height'] - 50
            if 'widget_align' not in self.windows_config.keys():
                self.windows_config['widget_align'] = 'left'
        elif (not self.openError) and (self.windows_config is not None) and (self.programe_data is not None):
            print(self.windows_config.keys())
            if 'treeview_width' not in self.windows_config.keys():
                self.windows_config['treeview_width'] = int(self.windows_config['windows_scale_width'] / 5)
            if 'treeview_height' not in self.windows_config.keys():
                self.windows_config['treeview_height'] = int(self.windows_config['windows_scale_height'] - 50)
            if 'widget_align' not in self.windows_config.keys():
                self.windows_config['widget_align'] = 'left'
        if self.windows_config is None:
            print('windows_config None')
        if self.programe_data is None:
            print('programe_data None')
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
    # ProjectDir을 추가하는 메소드
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
    # TreeView의 width와 height를 업데이트하는 메소드
    def UpdateTreeViewScale(self, width:int, height:int):
        self.windows_config['treeview_width'] = width
        self.windows_config['treeview_height'] = height
    # 포지션을 확인하는 메소드
    def getPosition(self):
        return self.windows_config['windows_pos_x'], self.windows_config['windows_pos_y']
    # 객체가 삭제될 때 최종적으로 호출하는 메소드
    def __del__(self):
        if self.updated and (not self.openError) and platform.system() == 'Darwin':
            print('Update')
            with open('./data/windows_config_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            print(self.windows_config)
            with open('./data/ProjectDirectories_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
        elif self.updated and (not self.openError) and platform.system() == "Windows":
            with open('./data/windows_config_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            with open('./data/ProjectDirectories_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
