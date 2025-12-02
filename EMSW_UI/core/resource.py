"""
    resource.py는 실제 로컬 시스템 및 필요한 프로그램의 동작에서 활용하는 데이터 파일을 관리하는 동작을 수행합니다.
    일반적으로, 모니터의 해상도, 그래픽 카드의 존재 여부, 메모리의 잔여량 등이 여기에 해당합니다.
    개발 당시의 컴퓨터 스팩은 ultra 9 285k, ram 64, RTX 5060ti 16gb, ssd 1tb(main), ssd 2tb(sub), ssd 1tb(extract disk)이다.
"""

from datetime import datetime

from PySide6.QtWidgets import (QApplication)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Signal, QObject
from Config.config import ProgrameAction

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

import copy, os, json, zipfile, io, pytz, requests, subprocess

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
    # global message를 공유하는 변수
    message = ''
    windows_data = {'x' : 100, 'y' : 100, 'width' : 600, 'height' : 800}
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
    def __init__(self, PROGRAME_DATA:dict, tz_:str):
        self.tz_ = pytz.timezone(tz_)
        self.buffer = io.BytesIO()
        self.Save = False
        self.dir = ''
        self.name = ''
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
                                                            'hobby_data_type' : 'str',
                                                            'personality_data_type' : "str",
                                                            'tendency_data_type' : "str",
                                                            'body_data_type' : "str",
                                                    }
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
                                }, "wiki" : {
                                    "sample" : {
                                        "index" : [],
                                        "bodies" : []
                                    }
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
                                'perusona_editing_windows' : {
                                    'rows_width' : [],
                                    'row_height' : 300,
                                    'x' : 100,
                                    'y' : 100,
                                    'w' : 400,
                                    'h' : 300,
                                },
                            },
                            "ProjectItems" : {
                                "AI_Perusona" : ['sample'],
                                "AI_World" : ['sample'],
                                "AI_Data" : ['sample'],
                                "documents" : ['sample'],
                                "data" : ['sample'],
                                "timer" : ['sample'],
                                "wiki" : [ "sample" ]
                            },
                        }
        if len(PROGRAME_DATA['Last Open Project']) == 0 and not os.path.exists(PROGRAME_DATA['Last Open Project']):
            with zipfile.ZipFile(self.buffer, "w", zipfile.ZIP_DEFLATED) as file:
                file.writestr("METADATA", f"{self.metadata}")
                file.writestr("AI_Perusona/", "{}")
                file.writestr("AI_World/", "{}")
                file.writestr("AI_Data/", "{}")
                file.writestr("documents/", "{}")
                file.writestr("data/", "{}")
                file.writestr("timer/", "{}")
                file.writestr("wiki/", "{}")
        if len(PROGRAME_DATA['Last Open Project']) != 0 and os.path.exists(PROGRAME_DATA['Last Open Project']):
            self.open_project('/'.join(PROGRAME_DATA['Last Open Project'].split['/'][0:-1]), PROGRAME_DATA['Last Open Project'].split('/')[-1])
        self.__save_Project__()
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
        # print(f"Saved: {self.ProjectItems['AI_Data'][ai_name][date_str][time_str]}")
    def ProjectName(self, name:str):
        self.name = name
    def ProjectDir(self, dir:str):
        self.dir = dir
    def __key_check__(self, meta:dict, keys:list):
        for k in keys:
            if k not in meta.keys():
                return False
        return True
    def change_project_title(self, title):
        old_path = f"{self.dir}/{self.name}"
        self.name = title
        if os.path.exists(old_path) and self.name:
            new_path = f"{self.dir}/{self.name}"
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
    def __update_project_items_to_metadata__(self):
        self.ProjectItems = self.metadata['ProjectItems']
    def open_project(self, dir:str, name:str):
        if len(dir) == 0 and len(name) == 0:
            return None
        path = os.path.join(dir, name)
        tdict = {}

        with zipfile.ZipFile(path, 'r') as zf:
            file_list = zf.namelist()
            for f in file_list:
                if f.endswith('/'):
                    continue
                if '/' in f:
                    folder, filename = f.split('/', 1)
                else:
                    folder, filename = '', f
                with zf.open(f) as inner:
                    raw = inner.read().decode('utf-8')
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = raw
                if folder not in tdict:
                    tdict[folder] = {}
                tdict[folder][filename] = data
        metaroot = tdict.get('', {})
        self.metadata = metaroot.get('METADATA', self.metadata)

        def _restore_section(folder_name: str, project_key: str, ext: str):
            section = {}
            folder_dict = tdict.get(folder_name, {})
            for filename, content in folder_dict.items():
                name_part, file_ext = os.path.splitext(filename)
                if file_ext == ext:
                    section[name_part] = content
            self.ProjectItems[project_key] = section

        _restore_section('AI_Data',     'AI_Data',     '.adata')
        _restore_section('AI_World',    'AI_World',    '.aworld')
        _restore_section('AI_Perusona', 'AI_Perusona', '.profile')
        _restore_section('documents',   'documents',   '.doct')
        _restore_section('data',        'data',        '.data')
        _restore_section('timer',       'timer',       '.time')

        self.dir = dir
        self.name = name

        print(self.metadata)
        print(self.ProjectItems)

        os.remove('./data/.tmp._tmsw_')
    def new_project_files(self, dir:str):
        self.dir = '/'.join(dir.split('/')[0:-1])
        self.name = dir.split('/')[-1]
        print(f"{'/'.join(dir.split('/')[0:-1])}/{dir.split('/')[-1]}")
        self.__save_Project__()
        os.remove('.\data\.tmp._tmsw_')
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
    def setWidth(self, width):
        print(self.metadata['ProgrameData']['windows_scale']['width'], width)
        self.metadata['ProgrameData']['windows_scale']['width'] = width
    def updatePosition(self, x, y):
        self.metadata['ProgrameData']['windows_pos']['x'] = x
        self.metadata['ProgrameData']['windows_pos']['y'] = y
    def updateScale(self, width, height):
        self.metadata['ProgrameData']['windows_scale']['width'] = width
        self.metadata['ProgrameData']['windows_scale']['height'] = height
    def SearchPerusonaName(self, name:str):
        return name in self.ProjectItems['AI_Perusona'].keys()
    def updatePerusonaName(self, name:str):
        self.ProjectItems['AI_Perusona'].keys()
        if name not in self.ProjectItems['AI_Perusona'].keys():
            source_data = self.ProjectItems['AI_Perusona']['sample']
            new_data = copy.deepcopy(source_data)
            self.ProjectItems['AI_Perusona'][name] = new_data
            return True
        else:
            return False
    def updatePerusonaAge(self, name:str, age:int):
        if self.SearchPerusonaName(name):
            self.ProjectItems['AI_Perusona'][name]['age'] = age
            return True
        else:
            return False 
    def updatePerusonaSex(self, name:str, sex:str):
        if self.SearchPerusonaName(name):
            self.ProjectItems['AI_Perusona'][name]['sex'] = sex
            return True
        else:
            return False
    def updatePerusonaHobby(self, name:str, hobby, data_type:str):
        if self.SearchPerusonaName(name):
            self.ProjectItems['AI_Perusona'][name]['hobby'] = hobby
            self.ProjectItems['AI_Perusona'][name]['hobby_data_type'] = data_type
            return True
        else:
            return False
    def updatePerusonaPersonality(self, name:str, personality, data_type:str):
        if self.SearchPerusonaName(name):
            if data_type == "str" or data_type == "dict" or data_type == "list":
                self.ProjectItems['AI_Perusona'][name]['personality'] = personality
                self.ProjectItems['AI_Perusona'][name]['personality_data_type'] = data_type
                return True
            else: return False
        else: return False
    def updatePerusonaTendency(self, name:str, tendency, data_type:str):
        if self.SearchPerusonaName(name):
            if data_type == "str" or data_type == "dict" or data_type == "list":
                self.ProjectItems['AI_Perusona'][name]['tendency'] = tendency
                self.ProjectItems['AI_Perusona'][name]['tendency_data_type'] = data_type
        else:
            return False
    def updatePerusonaBody(self, name:str, body, data_type:str):
        if self.SearchPerusonaName(name):
            if data_type == "str" or data_type == "dict" or data_type == "list":
                self.ProjectItems['AI_Perusona'][name]['body'] = body
                self.ProjectItems['AI_Perusona'][name]['body_data_type']  = data_type
                return True
            else:
                return False
        else:
            return False
    def updatePerusonaEditWindowColumnsLength(self, columns:list):
        self.metadata['ProgrameData']['rows_width'] = columns
    def updatePerusonaEditWindowPosition(self, x:int, y:int):
        self.metadata['ProgrameData']['x'] = x
        self.metadata['ProgrameData']['y'] = y
    def updatePerusonaEditWindowScale(self, w:int, h:int):
        self.metadata['ProgrameData']['w'] = w
        self.metadata['ProgrameData']['h'] = h
    def getPerusonaDict(self):
        return self.ProjectItems['AI_Perusona']
    def getPerusonaEditing_windowData(self):
        return self.metadata['ProgrameData']['perusona_editing_windows']
    def AIChattingList(self):
        return self.ProjectItems['AI_Data'].keys()
    def isInAIChatting(self, ai_name:str):
        return ai_name in self.ProjectItems['AI_Data'].keys()
    def sendUserMessage(self, ai_name:str, message:str, tz_:datetime.tzinfo):
        date = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        nowTime = datetime.now(tz_)
        if not self.isInAIChatting(ai_name):
            GlobalSignalHub.instance().programe_signal.emit(ProgrameAction.CreateNewAIChatting)
            return True
        else:
            self.ProjectItems[ai_name][date[nowTime.weekday()]] = {f"{nowTime.hour()}" : {f"{nowTime.minute()} : {nowTime.second()} : {nowTime.microsecond}" : {"user" : message}}}
            GlobalSignalHub.instance().programe_signal = ProgrameAction.SendMessageSuccess
            return True
    def sendAIMessage(self, ai_name:str, ai_message:str):
        date = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        if not self.isInAIChatting(ai_name):
            GlobalSignalHub.instance().programe_signal.emit(ProgrameAction.CreateNewAIChatting)
            return True
        else:
            nowTime = datetime.now(self.tz_)
            self.ProjectItems[ai_name][date[nowTime.weekday()]] = {f"{nowTime.hour()}" : {f"{nowTime.minute()} : {nowTime.second()} : {nowTime.microsecond}" : {"user" : ai_message}}}
            GlobalSignalHub.instance().programe_signal = ProgrameAction.SendMessageSuccess
            return True
    def __make_file__(self):
        ai_data_file = {}
        for k in self.ProjectItems['AI_Data'].keys():
            self.metadata['ProjectItems']['AI_Data'].append(f"{k}.adata")
            ai_data_file[k] = self.ProjectItems['AI_Data'][k]
        ai_word_file = {}
        self.metadata['ProjectItems']['AI_World'] = []
        for k in self.ProjectItems['AI_World'].keys():
            self.metadata['ProjectItems']['AI_World'].append(f"{k}.aworld")
            ai_word_file[k] = self.ProjectItems['AI_World'][k]
        ai_perusona = {}
        self.metadata['ProjectItems']['AI_Perusona'] = []
        for k in self.ProjectItems['AI_Perusona'].keys():
            self.metadata['ProjectItems']['AI_Perusona'].append(f"{k}.profile")
            ai_perusona[k] = self.ProjectItems['AI_Perusona'][k]
        documents = {}
        self.metadata['ProjectItems']['documents'] = []
        for k in self.ProjectItems['documents'].keys():
            self.metadata['ProjectItems']['documents'].append(f"{k}.doct")
            documents[k] = self.ProjectItems['documents'][k]
        data = {}
        self.metadata['ProjectItems']['data'] = []
        for k in self.ProjectItems['data'].keys():
            self.metadata['ProjectItems']['data'].append(f"{k}.data")
            data[k] = self.ProjectItems['data'][k]
        timer = {}
        self.metadata['ProjectItems']['timer'] = []
        for k in self.ProjectItems['timer'].keys():
            self.metadata['ProjectItems']['timer'].append(f"{k}.time")
            timer[k] = self.ProjectItems['timer'][k]
        return (ai_data_file, ai_word_file, ai_perusona, documents, data, timer)
    def __save_Project__(self):
        ai_data_file, ai_world_file, ai_perusona, documents, data, timer = self.__make_file__()
        print(f"{self.dir}/{self.name}")
        if os.path.exists(f"{self.dir}/{self.name}") and not (len(self.dir) == 0 or len(self.dir) == 0):
            with zipfile.ZipFile(f"{self.dir}/{self.name}", 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('METADATA', json.dumps(self.metadata, ensure_ascii=False, indent=4))
                for name, content in ai_data_file.items():
                    z.writestr(f"AI_Data/{name}.adata",
                               json.dumps(content, ensure_ascii=False))
                for name, content in ai_world_file.items():
                    z.writestr(f"AI_World/{name}.aworld",
                               json.dumps(content, ensure_ascii=False))
                for name, content in ai_perusona.items():
                    z.writestr(f"AI_Perusona/{name}.profile",
                               json.dumps(content, ensure_ascii=False))
                for name, content in documents.items():
                    z.writestr(f"documents/{name}.doct",
                               json.dumps(content, ensure_ascii=False))
                for name, content in data.items():
                    z.writestr(f"AI_Data/{name}.data",
                               json.dumps(content, ensure_ascii=False))
                for name, content in timer.items():
                    z.writestr(f"AI_Data/{name}.time",
                               json.dumps(content, ensure_ascii=False))
        else:
            if len(self.dir) == 0 and len(self.name) == 0 or not os.path.exists(f"{self.dir}/{self.name}"):
                with zipfile.ZipFile('./data/.tmp._tmsw_', 'w', zipfile.ZIP_DEFLATED) as z:
                    z.writestr('METADATA', json.dumps(self.metadata, ensure_ascii=False, indent=4))
                    for name, content in ai_data_file.items():
                        z.writestr(f"AI_Data/{name}.adata",
                            json.dumps(content, ensure_ascii=False))
                    for name, content in ai_world_file.items():
                        z.writestr(f"AI_World/{name}.aworld",
                            json.dumps(content, ensure_ascii=False))
                    for name, content in ai_perusona.items():
                        z.writestr(f"AI_Perusona/{name}.profile",
                            json.dumps(content, ensure_ascii=False))
                    for name, content in documents.items():
                        z.writestr(f"documents/{name}.doct",
                               json.dumps(content, ensure_ascii=False))
                    for name, content in data.items():
                        z.writestr(f"AI_Data/{name}.data",
                            json.dumps(content, ensure_ascii=False))
                    for name, content in timer.items():
                        z.writestr(f"AI_Data/{name}.time",
                           json.dumps(content, ensure_ascii=False))
            else:
                return False
    def __del__(self):
        print(f"{self.dir}/{self.name}")
        ai_data_file, ai_world_file, ai_perusona, documents, data, timer = self.__make_file__()
        if not (0 == len(self.name) and 0 == len(self.dir)) and os.path.exists(self.dir):
            with zipfile.ZipFile(f"{self.dir}/{self.name}", 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('METADATA', json.dumps(self.metadata, ensure_ascii=False, indent=4))
                for name, content in ai_data_file.items():
                    z.writestr(f"AI_Data/{name}.adata",
                               json.dumps(content, ensure_ascii=False))
                for name, content in ai_world_file.items():
                    z.writestr(f"AI_World/{name}.aworld",
                               json.dumps(content, ensure_ascii=False))
                for name, content in ai_perusona.items():
                    z.writestr(f"AI_Perusona/{name}.profile",
                               json.dumps(content, ensure_ascii=False))
                for name, content in documents.items():
                    z.writestr(f"documents/{name}.doct",
                               json.dumps(content, ensure_ascii=False))
                for name, content in data.items():
                    z.writestr(f"AI_Data/{name}.data",
                               json.dumps(content, ensure_ascii=False))
                for name, content in timer.items():
                    z.writestr(f"AI_Data/{name}.time",
                               json.dumps(content, ensure_ascii=False))
        else:
            os.remove(f"./data/.tmp._tmsw_")

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

# 중앙 AI LLM 제어 클래스
class GlobalWorld:
    """
    이 클래스는 사용자가 생성한 설정 내지는 기본적인 AI의 설정을 관리하며, Ollama과의 연결을 직접적으로 관리하는 instance class.
    일반적으로 프로그램이 시작될 때 시작되고, 프로그램이 끝날 때 종료된다.
    프로그램이 시작될 때 -> ollma를 호출하고, 프로그램이 종료될 때 ollama를 종료한다. 단, 사전에 ollama가 설치되어 있어야 한다.
    직접 staticmethod인 instance를 통해 호출할 수 있다.
    """

    # 싱글톤 패턴
    _instance = None

    # 전역 변수
    # 로컬 Ollama Host를 위한 주소
    OLLAMA_HOST = "http://127.0.0.1:11434"
    # 로컬 AI Memory를 저장하는 주소
    AI_Memory = None
    # AI의 프롬프트 리스트
    Prompt = None
    # 로컬 llm과 통신할 수 있도록 하는 langchain
    llm = None
    # 로컬 llm에 적용된 모델 종류
    ollama = None
    # 로컬 llm에 적용된 temperature (0 : 결정론적, 0.1~0.3 : 답이 일관적이게 변함, 0.8~1 이상 : 답에 창의성이 부여됨.)
    temperature = 0.7

    # ollama가 동작중인지 확인
    def is_ollama_running(self):
        try:
            r = requests.get(f"{self.OLLAMA_HOST}/api/tags", timeout=1)
            return r.status_code == 200
        except Exception:
            return False
    # ollama를 실행하는 메소드
    def start_ollama(self):
        cmd = ["ollama", "serve"]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        # 서버가 시작될 시간을 기다림
        for _ in range(10):
            if self.is_ollama_running():
                print("✔ Ollama 서버 실행됨.")
                return True
            self.time.sleep(1)
        return False
    # 가장 기초적인 system prompt 데이터를 만드는 메소드
    def make_prompt_data():
        if GlobalWorld.instance().Prompt is None:
            GlobalWorld.instance().Prompt = [
                ("system", "you are a helpful assistant.")
            ]
        if GlobalWorld.instance().Prompt:
            return True
        return False
    # 기초적인 프롬프트를 추가하는 메소드
    def add_prompt(type__:str, message:str):
        if (GlobalWorld.instance().Prompt is None):
            return False
        GlobalWorld.instance().Prompt.append((type__, message))
        return True
    # ollama에서 모델을 호출한다.
    def getllm(ollama_model_name:str, temperature):
        if GlobalWorld.instance().llm is None:
            GlobalWorld.instance().llm = ChatOllama(model=ollama_model_name, temperature=temperature)
        return GlobalWorld.instance().llm
    # ollama에서 llm을 호출할때, 캐릭터와 메시지, 그리고 내용에 따라 미리 정의된 'prompt'를 호출한다.
    # chain은 여기서 지역적으로 형성되며, 사라진다.
    # value : 현재 메시지의 기준이며, 데이터 점검에 해당한다.
    # 1 : set self body
    # 2 : set self personality
    # 3 : set self tendency
    # 4 : set self Image
    # 0 : nomar chatting
    def Call_AI(name:str, input_msg:str, value:int):
        text = [("system", f"your name is {name}.")]
        for k in ['age', 'sex', 'personality', 'hobby', 'tendency', 'body']:
            text.append(("system", f"your {k} is {GlobalWorld.instance().AI_Memory[name][k]}."))

        if name not in GlobalWorld.Get_AI_Names():
            return None
        elif value == 1:
            prompt = copy.deepcopy(GlobalWorld.instance().Prompt)
            for t in text:
                prompt.append(t)
            prompt.append(('user', '{input}'))
            prompt = ChatPromptTemplate.from_messages(prompt)
            output_parser = StrOutputParser()
            chain = prompt | GlobalWorld.instance().llm | output_parser

            return chain.invoke({"input":"정의된 네 외모를 특징과 전체 모습을 직접 정의하여 설명하라"})
        elif value == 2:
            prompt = copy.deepcopy(GlobalWorld.instance().Prompt)
            prompt = prompt
            for t in text:
                prompt.append(t)
            prompt.append(('user', '{input}'))
            prompt = ChatPromptTemplate.from_messages(prompt)
            output_parser = StrOutputParser()
            chain = prompt | GlobalWorld.instance().llm | output_parser
            return chain.invoke({'input' : '정의된 내용을 보고 네 성격을 직접 정의하여 설명하라.'})
        elif value == 3:
            prompt = copy.deepcopy(GlobalWorld.instance().Prompt)
            prompt = prompt
            for t in text:
                prompt.append(t)
            prompt.append(('user', '{input}'))
            prompt = ChatPromptTemplate.from_messages(prompt)
            output_parser = StrOutputParser()
            chain = prompt | GlobalWorld.instance().llm | output_parser
            return chain.invoke({'input' : '정의된 내용을 보고 네 성향을 직접 정의하여 설명하라.'})
        elif value == 4:
            prompt = copy.deepcopy(GlobalWorld.instance().Prompt)
            prompt = prompt
            for t in text:
                prompt.append(t)
            prompt.append(('user', '{input}'))
            prompt = ChatPromptTemplate.from_messages(prompt)
            output_parser = StrOutputParser()
            chain = prompt | GlobalWorld.instance().llm | output_parser
            return chain.invoke({'input' : '정의된 네용을 보고 네가 본 네 모습을 직접 정의하여 설명하라.'})
        
    # Create_AI_Memory 
    def Create_AI_Memory(name:str):
        if name not in GlobalWorld.instance().AI_Memory.keys():
            GlobalWorld.instance().AI_Memory = {name : {}}
        return GlobalWorld.instance().AI_Memory is not None
    # 기존에 저장된 페르소나를 입력받는 메소드
    def Create_AI_Perusona(name:str, perusona:dict):
        key_list = ['age', 'sex', 'personality', 'hobby', 'tendency', 'body', 'self_body', 'self_personality', 'self_tendency', 'self_image']
        for k in key_list:
            GlobalWorld.instance().AI_Memory[name][k] = perusona[k]
        if len(GlobalWorld.instance().AI_Memory[name]['self_body']) == 0:
            return False
        elif len(GlobalWorld.instance().AI_Memory[name]['self_personality']) == 0:
            return False
        elif len(GlobalWorld.instance().AI_Memory[name]['self_tendency']) == 0:
            return False
        elif len(GlobalWorld.instance().AI_Memory[name]['self_image']) == 0:
            return False
        return True
    
    """
    체크할 키 리스트를 받아, len을 조사하여 제대로 설정이 됐는지 검사
    0 : 모두 설정되어 있음.
    -1 : 이름이 존재하지 않음, 생성이 되지 않음
    -2 : 첫 번째 키가 존재하지 않음(age)
    -3 : 두 번째 키가 존재하지 않음(sex)
    -4 : 세 번째 키가 존재하지 않음(personality)
    -5 : 네 번째 키가 존재하지 않음(hobby)
    -6 : 다섯번째 키가 존재하지 않음(tendency)
    -7 : 여섯번째 키가 존재하지 않음(body)
    -8 : 일곱번째 키가 존재하지 않음(self_body)
    -9 : 여덟번째 키가 존재하지 않음(self_personality)
    -10 : 아홉번째 키가 존재하지 않음(self_tendency)
    -11 : 열번째 키가 존재하지 않음(self_image)
    -12 : 키에 데이터가 저장되어 있지 않다.
    """
    def check_perusona(name:str, key:list):
        if name not in GlobalWorld.Get_AI_Names():
            return -1
        code_return = {'age' : -2, 'sex' : -3, 'personality' : -4, 'hobby' : -5, 'tendency' : -6, 'body' : -7, 'self_body' : -8, 'self_personality' : -9, 'self_tendency' : -10, 'self_image' : -11}
        def checking_type(key):
            if k is int:
                return 1
            elif k is str:
                return 2
            elif k is dict:
                return 3
            elif k is list:
                return 4
            else:
                return -1
        for k in key:
            if k not in GlobalWorld.Get_AI_Perusona(name).keys():
                return -1
            else:
                if checking_type(GlobalWorld.Get_AI_Perusona(name)[k] == 1):
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Perusona(name)[k]) == 2):
                    if len(checking_type) == 0:
                        return code_return[k]
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Perusona(name)[k]) == 3):
                    if len(checking_type.keys()) == 0:
                        return code_return[k]
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Perusona(name)[k]) == 4):
                    if len(checking_type) == 0:
                        return code_return[k]
                    continue
                elif checking_type(GlobalWorld.Get_AI_Perusona(name)[k] == -1):
                    return -12
                else:
                    continue
        return True
    # Self_body, 즉 AI가 대화를 통해 정의한 자신의 외형을 설정하는 메소드
    def Set_AI_Perusona_Self_body(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_body'] = data
    # Self_personality, 즉 AI가 대화를 통해 정의한 자신의 성격을 설정하는 메소드
    def Set_AI_Perusona_Self_Personality(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_personality'] = data
    # Self_Tendency, 즉 AI가 대화를 통해 정의한 자신의 성향을 설정하는 메소드
    def Set_AI_Perusona_Self_Tendency(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_tendency'] = data
    # Self_Image, 즉 AI가 대화를 통해 정의한 자신의 이미지를 설정하는 메소드
    def Set_AI_Perusona_Self_Image(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_image'] = data
    # AI Perusona를 반환하는 메소드.
    def Get_AI_Perusona(name:str):
        return GlobalWorld.instance().AI_Memory[name]
    # 실행중인 AI Perusona의 정보의 key를 받아오는 메소드
    def Get_AI_Names():
        return GlobalWorld.instance().AI_Memory.keys()
    # 생성자
    def __init__(self):
        self.AI_Memory = {}
    @staticmethod
    # singleton 패턴 인스턴스
    def instance():
        if GlobalWorld._instance is None:
            GlobalWorld._instance = GlobalWorld()
        return GlobalWorld._instance