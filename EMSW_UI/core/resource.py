"""
    resource.py는 실제 로컬 시스템 및 필요한 프로그램의 동작에서 활용하는 데이터 파일을 관리하는 동작을 수행합니다.
    일반적으로, 모니터의 해상도, 그래픽 카드의 존재 여부, 메모리의 잔여량 등이 여기에 해당합니다.
    개발 당시의 컴퓨터 스팩은 ultra 9 285k, ram 64, RTX 5060ti 16gb, ssd 1tb(main), ssd 2tb(sub), ssd 1tb(extract disk)이며, macmini m2 pro 16gb, 512gb 이다.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Signal, QObject
from Config.config import ProgrameAction

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOllama

import platform, os, json, zipfile, io

"""
    중앙에서 시그널 정보를 처리하는 싱글톤 클래스
"""
class GlobalSignalHub(QObject):
    #메인 윈도우에서 받아서 처리할 programe_signal 정의
    #ProgrameAction은 모든 서브 윈도우와 서브 프로그램의 윈도우 클래스가 정의되어 있다.
    #mainWindow와 subWindow와 양방향 통신용 시그널이다.
    programe_signal = Signal(ProgrameAction)
    # global project dir로 공유하는 메소드
    dir = Signal(str)

    # 싱글턴 패턴
    _instance = None
    @staticmethod
    def instance():
        if GlobalSignalHub._instance is None:
            GlobalSignalHub._instance = GlobalSignalHub()
        return GlobalSignalHub._instance

"""
    프로젝트 파일을 읽어오는 클래스입니다.
    프로젝트를 생성할때 최초 생성되고, 프로젝트 내의 정보를 json으로 읽어들입니다.
    프로젝트 파일은 .emsw로 하여 ziplib으로 관리합니다.
"""
class ProjectConfig:
    def __init__(self, **kwargs):
        self.buffer = io.BytesIO()
        self.Save = False
        self.dir = ''
        if (len(kwargs) == 0):
            self.AI_Perusona = {
                                    'sample' : {
                                                    "date" : {
                                                                "hour" : {
                                                                    "name" : "context",
                                                                    "user" : "context",
                                                                }
                                                    },
                                                    "summary" : {
                                                                "date" : "Context",
                                                    },
                                    },
                                }
            self.AI_Word = {
                                'sample' :{
                                    'contry' : {
                                                    "name" : "content",
                                                    "populate" : 0,
                                                    "political_system" : "content",
                                                    "citis" : [],
                                                    "low" : [],
                                                    "economic_system"  : "content",
                                                    "leader" : "content",
                                                    "cultural_level" : "content",                 
                                    },
                                    "world" : {
                                                    "continent" : "",
                                                    "continent_name" : [],
                                                    "continent_populate" : {"name":"content"},
                                                    "continent_contries" : {"name":["content"]},
                                                    "continent_resource" : {"name":["content"]},
                                                    "continent_ecosystem_level" : {"name":["content"]},
                                    },
                                },
                            }
            self.AI_Perusona = {
                                    'sample' : {
                                                "age" : 0,
                                                "sex" : 'content',
                                                'personality' : "content",
                                                'hobby' : 'content',
                                                'tendency' : 'content',
                                                'body' : 'content',
                                                'self_body' : [],
                                                'self_personality' : [],
                                                'self_tendency' : [],
                                                'self_image' : [],
                                                'note' : [],
                                            },

                                }
            self.documents = {
                                'sample' : {
                                            'title' : 'content',
                                            'index' : 'content',
                                            'text' : 'content',
                                        },
                              }
            self.data = {
                            'sample' : {
                                'type' : 'content',
                            }
                        }
            self.timer = {
                            'name' : {
                                'input_time' : 0,
                                'focus_time' : 0,
                                'active_time' : 0,
                            }
                        }
            self.metadata = {
                                "ProgrameData" : {
                                    'windows_pos' : {
                                                        'x':100,
                                                        'y':100
                                                    },
                                    'windows_scale' : {
                                                    'width':800,
                                                    'height':500
                                                },
                                },
                                "ProjectItems" : {
                                    "AI_Perusona" : ['sample'],
                                    "AI_World" : ['sample'],
                                    "AI_Data" : ['sample'],
                                    "documents" : ['sample'],
                                    "data" : ['sample'],
                                    "timer" : ['sample'],
                                },
                            }
            with zipfile.ZipFile(self.buffer, "w", zipfile.ZIP_DEFLATED) as file:
                file.writestr("METADATA", f"{self.metadata}")
                file.writestr("AI_Perusona/", "{}")
                file.writestr("AI_World/", "{}")
                file.writestr("AI_Data/", "{}")
                file.writestr("documents/", "{}")
                file.writestr("data/", "{}")
                file.writestr("timer/", "{}")
        elif len(kwargs) == 2 and self.__key_check__(kwargs, ['dir','file']):
            pass
    def __key_check__(self, meta:dict, keys:list):
        for k in keys:
            if k not in meta.keys():
                return False
        return True
    def __meta_check__(self):
        for k in self.metadata['Project_Files'].keys():
            if k not in os.listdir(self.dir):
                self.__MakeMetaGroup__(k)
    def __MakeMetaGroup__(self, nmae:dir):
        os.mkdir(f"{self.dir}/{nmae}")
    def __save_meta__(self):
        if 1 < len(self.metadata_dir.split('/')):
            with open(self.metadata_dir, 'w', encoding='utf-8') as file:
                json.dump(self.metadata, file)
    def __open_project__(self):
        pass
    def __create_project__(self):
        os.makedirs(self.dir)
        with open(f"{self.dir}/METADATA", 'w', encoding='utf-8') as file:
            json.dump(self.metadata, file)
        self.__meta_check__()
    def ProjectFiles(self):
        return self.metadata['Project_Files']
    def ProgrameData(self):
        return self.metadata['ProgrameData']
    def updatePosition(self, x, y):
        self.metadata['ProgrameData']['windows_pos']['x'] = x
        self.metadata['ProgrameData']['windows_pos']['y'] = y
        self.updatebuffer()
    def updateScale(self, width, height):
        self.metadata['ProgrameData']['windows_scale']['width'] = width
        self.metadata['ProgrameData']['windows_scale']['height'] = height
        self.updatebuffer()
    def updatebuffer(self):
            self.buffer.flush()
            with zipfile.ZipFile(self.buffer, "w", zipfile.ZIP_DEFLATED) as file:
                file.writestr('METADATA', self.metadata)
                for name, context in self.metadata['ProjectItems'].items():
                    file.writestr('ProjectItems' + name + '/' + context, self.ProjectItems[context])
    def __del__(self):
        print(self.dir)
        if len(self.dir) == 0:
            pass
        else:
            with open(self.dir, "wb") as f:
                f.write(self.buffer.getvalue())
"""
    프로그램 동작에 필요한 json 파일을 관리하는 클래스 입니다.
    programe_config로 하여 실행되는 OS를 확인하고, OS에 따른 설정을 관리합니다.
"""
class config:
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
            if 'create_ai_perusona_window_width' not in self.windows_config.keys():
                self.windows_config['create_ai_perusona_window_width'] = 500
            if 'create_ai_perusona_window_height' not in self.windows_config.keys():
                self.windows_config['create_ai_perusona_window_height'] = 600
        else:
            print('None Exception')
    def find_window_config_keys(self, key:str):
        return key in self.windows_config.keys()
    def getCreateAIPerusonaWindowScale(self):
        return int(self.windows_config['create_ai_perusona_window_width']), int(self.windows_config['create_ai_perusona_window_height'])
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
        if x != self.windows_config['windows_pos_x'] or y != self.windows_config['windows_pos_y']:
            self.windows_config['windows_pos_x'] = x
            self.windows_config['windows_pos_y'] = y
            self.updated = True
        else:
            self.update = False
    # scale을 업데이트하는 메소드
    def updateScale(self, width:int, height:int):
        if width != self.windows_config['windows_scale_width'] or height != self.windows_config['windows_scale_height']:
            self.windows_config['windows_scale_width'] = width
            self.windows_config['windows_scale_height'] = height
            self.update = True
        else:
            self.updated = False
    def save_window_data(self):
        with open('./data/windows_config_win.json', 'w', encoding='utf-8') as file:
            json.dump(self.windows_config, file)
    def getScale(self):
        return self.windows_config['windows_scale_width'], self.windows_config['windows_scale_height']
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
    # windows_config 태그를 체크하는 메소드
    def checkTag(self, key:str, data):
        tags = self.windows_config.keys()
        if key not in tags:
            self.windows_config[key] = data
            return True
        else:
            return False
    # windows_config 태그 키를 통해서 데이터를 반환하는 메소드
    def getValueToTag(self, key:str):
        tags = self.windows_config.keys()
        if key not in tags:
            return None
        else:
            return self.windows_config[key]
    def Save_config(self):
        if self.updated and (not self.openError) and platform.system() == 'Darwin' and self.updated:
            print('Update')
            with open('./data/windows_config_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            print(self.windows_config)
            with open('./data/ProjectDirectories_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
        elif self.updated and (not self.openError) and platform.system() == "Windows" and self.updated:
            with open('./data/windows_config_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            with open('./data/ProjectDirectories_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
    # 객체가 삭제될 때 최종적으로 호출하는 메소드
    def __del__(self):
        if self.updated and (not self.openError) and platform.system() == 'Darwin' and self.updated:
            print('Update')
            with open('./data/windows_config_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            print(self.windows_config)
            with open('./data/ProjectDirectories_mac.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)
        elif self.updated and (not self.openError) and platform.system() == "Windows" and self.updated:
            with open('./data/windows_config_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.windows_config, file)
            with open('./data/ProjectDirectories_win.json', 'w', encoding='utf-8') as file:
                json.dump(self.programe_data, file)

"""
    AI_Perusona를 관리하는 클래스이다.
    이 클래스는 AI의 Perusona를 직접 관리하는 클래스이다.
"""
class AI_Perusona:
    def __init__(self, dir:str):
        self.dir = dir
        print(dir)
        self.open_files()
    def open_files(self):
        if os.path.exists(self.dir):
            try:
                with open(self.dir, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)
            except json.JSONDecodeError:
                GlobalSignalHub.instance().programe_signal.emit(ProgrameAction.FileJsonError)
                GlobalSignalHub.instance().message.emit(self.dir)
        elif not os.path.exists(self.dir):
            if os.path.exists('/'.join(self.dir.split('/')[0:-1])):
                self.data = {}
                self.data['name'] = ''
                self.data['age'] = ''
                self.data['sex'] = ''
                self.data['personality'] = ''
                self.data['hobby'] = []
                self.data['tendency'] = ''
                self.data['body'] = []
                self.data['self_personality'] = ''
                self.data['self_tendency'] = ''
                self.data['self_body'] = ''
                self.data['self_image'] = ''
                self.save_data()
        else:
            return False
    def set_name(self, name:list):
        self.data['name'] = name
        self.save_data()
    def get_name(self):
        return self.data['name']
    def set_sex(self, sex:list):
        self.data['sex'] = sex
        self.save_data()
    def get_sex(self):
        return self.data['sex']
    def set_age(self, age:int):
        self.data['age'] = age
        self.save_data()
    def get_age(self):
        return self.data['age']
    def set_personality(self, personality:list):
        self.data['personality'] = personality
        self.save_data()
    def get_personality(self):
        return self.data['personality']
    def set_hobby(self, hobby:list):
        self.data['hobby'] = hobby
        self.save_data()
    def get_hobby(self):
        return self.data['hobby']
    def set_Tendency(self, tendency:list):
        self.data['tendency'] = tendency
        self.save_data()
    def get_Tendency(self):
        return self.data['tendency']
    def set_body(self, body:list):
        self.data['body'] = body
        self.save_data()
    def get_body(self):
        return self.data['body']
    def set_self_personality(self, personality:str):
        self.data['self_personality'] = personality
        self.save_data()
    def get_self_personality(self):
        return self.data['self_personality']
    def set_self_tendency(self, tendency:str):
        self.data['self_tendency'] = tendency
        self.save_data()
    def get_self_tendency(self):
        return self.data['self_tendency']
    def set_self_body(self, body:str):
        self.data['self_body'] = body
        self.save_data()
    def get_self_body(self):
        return self.data['self_body']
    def set_self_image(self, self_image:str):
        self.data['self_image'] = self_image
        self.save_data()
    def get_self_image(self):
        return self.data['self_image']
    def save_data(self):
        with open(self.dir, 'w', encoding='utf-8') as file:
            json.dump(self.data, file)
    def perusona(self):
        return self.data

"""
    모니터의 정보를 가져오는 함수입니다.
"""
def Display():
    def __get_all_display__():
        """
        활성화된 모든 디스플레이의 객체를 반환합니다.
        """
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return QGuiApplication.screens()
    def __get_display_count_number__():
        """
        활성화된 디스플레이의 개수를 반환합니다.
        """
        return len(__get_all_display__())
    screen = __get_all_display__()
    screen_info = []
    for i, screen in enumerate(screen):
        geometry = screen.geometry()
        info = {
            "index" : i,
            "name" : screen.name(),
            "is_primary" : screen == QGuiApplication.primaryScreen(),
            "geometry" : {'x':geometry.x(), 'y':geometry.y(),'width':geometry.width(), 'height':geometry.height()}
        }
        screen_info.append(info)
    return screen_info

# 중앙 세계관 및 AI 대화 기억 클래스
class GlobalWorld:
    # 세계관, 즉 AI가 자신이 있다고 믿는 세계관을 의미한다. (다른 것과는 상관이 없다.)
    # AI의 대화 데이터와 글로벌 system 데이터를 관리하며 관장한다.
    # AI System 메시지는 세계관에 의해 지배받는 식으로 유지된다.
    # AI의 페르소나, 즉 가장 순수한 정체성은 고유하게 관리되지만, AI의 기억은 이곳에서 접근하여 관리한다.
    # 또한, GlobalWorld System에 지배받고 있으며, 글로벌 System은 AI의 System보다 더 상위에서 지배되는 규칙이다.

    #싱글톤 패턴
    _instance = None

    # world_system과 AI_Memory가 위치하는 장소
    def __init__(self):
        self.world_system = {}
        self.AI_Memory = {}
    # 사용자가 세계관을 다듬을 때, 데이터가 있는 곳.
    def appendWorldData(self, key:str, value:str):
        self.world_system[key] = value
    # AI가 대화를 할 때 반드시 이곳의 AI Memory에 올려야 한다.
    def appendAI_Memory(self, key:str, value:str):
        self.AI_Memory[key] = value
    # AI의 답변이 Global_Rule에 저촉하는지 조사한다.
    def check_Global_Rule(self, ai_response:str):
        self.mastrule
    @staticmethod
    def instance():
        if GlobalWorld._instance is None:
            GlobalWorld._instance = GlobalWorld()
        return GlobalWorld._instance