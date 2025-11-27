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

import platform, os, json, zipfile, io, datetime

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
    windows_data = {'x' : 100, 'y' : 100, 'width' : 600, 'height' : 800}
    # 현재 활성화된 인스턴스를 보관 (Project Config 객체)
    active_project = None
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
        self.title = ''
        self.ProjectItems = {
                                'AI_Data' : {
                                        'sample' : {
                                                "date" : {
                                                    "time" : {
                                                            "name" : "content",
                                                            "user" : "content",
                                                            },
                                                        },
                                                "summary" : {
                                                    "date" : "summary_data",
                                                },
                                            },
                                }, "AI_World" :{
                                        'sample' : {
                                            'contry' : {
                                                'name' : 'content',
                                                'populate' : 'number',
                                                'political_system' : 'content',
                                                'citis' : [],
                                                'low' : [],
                                                'economic_system'  : 'content',
                                                'leader' : 'content',
                                                'cultural_level' : [],
                                            },
                                            'world' : {
                                                'continent' : [],
                                                'continent_name' : {},
                                                'continent_populate' : {},
                                                'continent_contries' : {},
                                                'continent_resource' : {},
                                                'continent_ecosystem' : {},
                                            }
                                        }
                                
                                }, "AI_Perusona" : {
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
                                }, "documents" : {
                                                    'sample' : {
                                                        'title' : 'content',
                                                        'index' : 'content',
                                                        'text' : 'content',
                                                },
                              }, 'data' : {
                                            'sample' : {
                                                            'type' : 'content',
                                                        }
                            }, "timer" : {
                                    'sample' : {
                                        'input_time' : 0,
                                        'focus_time' : 0,
                                        'active_time' : 0,
                                    }
                                },
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
        if (len(kwargs) == 0):
            with zipfile.ZipFile(self.buffer, "w", zipfile.ZIP_DEFLATED) as file:
                file.writestr("METADATA", f"{self.metadata}")
                file.writestr("AI_Perusona/", "{}")
                file.writestr("AI_World/", "{}")
                file.writestr("AI_Data/", "{}")
                file.writestr("documents/", "{}")
                file.writestr("data/", "{}")
                file.writestr("timer/", "{}")
        elif len(kwargs) == 2 and self.__key_check__(kwargs, ['dir','file']):
            self.open_project(kwargs['dir'], kwargs['file'])
            self.updatebuffer()
    def get_chat_history(self, name:str):
        """
        특정 AI 페르소나의 채팅 기록을 시간 순서대로 정렬하여 반환
        Return : list of dict [{'sender' : 'user' | 'ai', 'msg':'text, 'time':str}, ...]
        """
        chat_list = []
        ai_data_root = self.ProjectItems.get('AI_Data, {}')
        target_ai = ai_data_root.get(name, [])

        if not target_ai:
            return []
        dates = sorted(target_ai.keys())
        
        for date_key in dates:
            if date_key == 'summary': continue # summary 키 제외
            
            time_data = target_ai[date_key]
            # 3. 시간별 정렬 (Keys: HH:MM:SS)
            times = sorted(time_data.keys())
            
            for time_key in times:
                content = time_data[time_key]
                
                # 구조: { 'name': 'ai_msg', 'user': 'user_msg' }
                # 시간 순서상 User가 먼저 말하고 AI가 답했다고 가정하거나,
                # 데이터가 있는 것만 리스트에 추가
                
                # 사용자 메시지
                if 'user' in content and content['user']:
                    chat_list.append({
                        'sender': 'user',
                        'msg': content['user'],
                        'timestamp': f"{date_key} {time_key}"
                    })
                
                # AI 메시지 (key가 'name'이라고 되어있는 부분)
                if 'name' in content and content['name']:
                    chat_list.append({
                        'sender': 'ai',
                        'msg': content['name'],
                        'timestamp': f"{date_key} {time_key}"
                    })
                    
        return chat_list
    def add_chat_message(self, ai_name: str, sender_type: str, message: str):
        """
        채팅 메시지를 구조에 맞게 저장하고 버퍼를 갱신함
        sender_type: 'user' or 'ai'
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # 1. 경로 확보 (AI_Data -> ai_name -> date -> time)
        if 'AI_Data' not in self.ProjectItems:
            self.ProjectItems['AI_Data'] = {}
            
        if ai_name not in self.ProjectItems['AI_Data']:
            self.ProjectItems['AI_Data'][ai_name] = {}
            
        if date_str not in self.ProjectItems['AI_Data'][ai_name]:
            self.ProjectItems['AI_Data'][ai_name][date_str] = {}
            
        # 2. 해당 시간 데이터 생성
        # 같은 초(sec)에 대화가 오갈 수 있으므로, 기존 키가 있으면 병합하거나 덮어씀
        current_block = self.ProjectItems['AI_Data'][ai_name][date_str].get(time_str, {})
        
        if sender_type == 'user':
            current_block['user'] = message
            # AI 응답 자리가 없으면 빈칸으로 두거나 유지
            if 'name' not in current_block:
                current_block['name'] = ""
        else:
            current_block['name'] = message # 'name' 키가 AI의 답변 내용
            if 'user' not in current_block:
                current_block['user'] = ""

        self.ProjectItems['AI_Data'][ai_name][date_str][time_str] = current_block
        
        # 3. 변경 사항을 zip buffer에 반영 (ProjectConfig의 updatebuffer 호출)
        self.updatebuffer()
        # print(f"Saved: {self.ProjectItems['AI_Data'][ai_name][date_str][time_str]}")
    def ProjectName(self, name:str):
        self.title = name
    def ProjectDir(self, dir:str):
        self.dir = dir
    def __key_check__(self, meta:dict, keys:list):
        for k in keys:
            if k not in meta.keys():
                return False
        return True
    def change_project_title(self, title):
        old_path = f"{self.dir}/{self.title}"
        self.title = title
        if os.path.exists(old_path) and self.title:
            new_path = f"{self.dir}/{self.title}"
            try:
                os.rename(old_path, new_path)
            except OSError as e:
                print("이름 변경 실패!")
    def __MakeMetaGroup__(self, nmae:dir):
        os.mkdir(f"{self.dir}/{nmae}")
    def __save_meta__(self):
        if 1 < len(self.metadata_dir.split('/')):
            with open(self.metadata_dir, 'w', encoding='utf-8') as file:
                json.dump(self.metadata, file)
    def open_project(self, dir:str, name:str):
        with zipfile.ZipFile(f"{dir}/{name}", 'r') as file:
            file_list = file.namelist()
            tdict = {}
            for f in file_list:
                if '/' in f:
                    print(f)
                    t = f.split('/')
                    if t[0] not in tdict.keys():
                        tdict[t[0]] = {t[0] : {}}
                    if t[1] not in tdict.keys():
                        data = file.read(f).decode('utf-8')
                        tdict[t[0]] = {t[1] : json.loads(data)}
            self.metadata = json.loads(file.read('METADATA').decode('utf-8'))
        self.dir = dir
        self.name = name
    def ProjectFiles(self):
        return self.metadata['Project_Files']
    def ProgrameData(self):
        return self.metadata['ProgrameData']
    def getPosition(self):
        return [self.metadata['ProgrameData']['windows_pos']['x'], self.metadata['ProgrameData']['windows_pos']['y']]
    def getScale(self):
        return [self.metadata['ProgrameData']['windows_scale']['width'], self.metadata['ProgrameData']['windows_scale']['height']]
    def setHeight(self, height):
        print(self.metadata['ProgrameData']['windows_scale']['height'], height)
        self.metadata['ProgrameData']['windows_scale']['height'] = height
        self.updatebuffer()
    def setWidth(self, width):
        print(self.metadata['ProgrameData']['windows_scale']['width'], width)
        self.metadata['ProgrameData']['windows_scale']['width'] = width
        self.updatebuffer()
    def updatePosition(self, x, y):
        self.metadata['ProgrameData']['windows_pos']['x'] = x
        self.metadata['ProgrameData']['windows_pos']['y'] = y
        self.updatebuffer()
    def updateScale(self, width, height):
        self.metadata['ProgrameData']['windows_scale']['width'] = width
        self.metadata['ProgrameData']['windows_scale']['height'] = height
        self.updatebuffer()
    def updatebuffer(self):
        self.buffer = io.BytesIO()
        with zipfile.ZipFile(self.buffer, "w", zipfile.ZIP_DEFLATED) as file:
            file.writestr('METADATA', json.dumps(self.metadata, ensure_ascii=False))
            for name, context in self.metadata['ProjectItems'].items():
                for c in context:
                    file.writestr(f"{name}/{c}", json.dumps(self.ProjectItems[name][c], ensure_ascii=False))
    def __del__(self):
        self.updatebuffer()
        print(f"{self.dir}/{self.title}")
        if len(self.dir) == 0 or len(self.title) == 0:
            pass
        else:
            with open(f"{self.dir}/{self.title}", "wb") as f:
                f.write(self.buffer.getvalue())
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