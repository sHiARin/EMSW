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

from pathlib import Path
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
    message = Signal(str)
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
    # 기본 데이터 구조 정의 (상수)
    DEFAULT_PROJECT_ITEMS = {
        'AI_Data': {
            'sample': {
                "date": {"time": {"name": "content", "user": "content"}},
                "summary": {"date": "summary_data"},
            }
        },
        'AI_World': {
            'sample': {
                'contry': {'name': 'content', 'populate': 'number', 'political_system': 'content', 'citis': [], 'low': [], 'economic_system': 'content', 'leader': 'content', 'cultural_level': []},
                'world': {'continent': [], 'continent_name': {}, 'continent_populate': {}, 'continent_contries': {}, 'continent_resource': {}, 'continent_ecosystem': {}}
            }
        },
        'AI_Persona': {
            'sample': {
                "age": 0, "sex": 'content', 'personality': "content", 'hobby': 'content', 'tendency': 'content', 'body': 'content',
                'self_body': [], 'self_personality': [], 'self_tendency': [], 'self_image': [], 'note': [],
                'hobby_data_type': 'str', 'personality_data_type': "str", 'tendency_data_type': "str", 'body_data_type': "str",
            }
        },
        'documents': {'sample': {'title': 'content', 'index': 'content', 'text': 'content'}},
        'data': {'sample': {'type': 'content'}},
        'timer': {'sample': {'input_time': 0, 'focus_time': 0, 'active_time': 0}},
        'wiki': {"sample": {"index": [], "bodies": []}}
    }

    DEFAULT_METADATA = {
        "ProgrameData": {
            'windows_pos': {'x': 100, 'y': 100},
            'windows_scale': {'width': 800, 'height': 500},
            'Persona_editing_windows': {'rows_width': [], 'row_height': 300, 'x': 100, 'y': 100, 'w': 400, 'h': 300},
        },
        "ProjectItems": {
            k: ['sample'] for k in DEFAULT_PROJECT_ITEMS.keys()
        }
    }

    def __init__(self, program_data: dict, tz_str: str):
        self.tz = pytz.timezone(tz_str)
        self.project_dir = Path('')
        self.project_name = ''
        
        # 데이터 초기화 (Deep Copy로 참조 문제 방지)
        self.project_items = copy.deepcopy(self.DEFAULT_PROJECT_ITEMS)
        self.metadata = copy.deepcopy(self.DEFAULT_METADATA)

        # 마지막 프로젝트 열기 시도
        last_project_path = program_data.get('Last Open Project', '')
        if last_project_path and os.path.exists(last_project_path):
            path = Path(last_project_path)
            self.open_project(str(path.parent), path.name)
        else:
            # 임시 파일 생성
            self._save_to_zip('./data/.tmp._tmsw_')

    # =========================================================================
    # File I/O (Core)
    # =========================================================================
    def new_project_files(self, file_path: str):
        path = Path(file_path)
        self.project_dir = path.parent
        self.project_name = path.name
        print(f"New Project: {path}")
        
        self.save_project()
        
        # 임시 파일 삭제
        temp_file = Path('./data/.tmp._tmsw_')
        if temp_file.exists():
            temp_file.unlink()

    def open_project(self, directory: str, name: str):
        if not directory and not name:
            return None

        path = Path(directory) / name
        if not path.exists():
            print(f"Error: File not found {path}")
            return

        temp_items = {}
        
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                for filename in zf.namelist():
                    if filename.endswith('/'): continue
                    
                    # 폴더/파일명 분리
                    parts = filename.split('/', 1)
                    folder = parts[0] if len(parts) > 1 else ''
                    fname = parts[1] if len(parts) > 1 else filename

                    with zf.open(filename) as f:
                        content = f.read().decode('utf-8')
                        try:
                            data = json.loads(content)
                        except json.JSONDecodeError:
                            data = content
                    
                    if folder not in temp_items:
                        temp_items[folder] = {}
                    temp_items[folder][fname] = data

            # 메타데이터 로드
            if 'METADATA' in temp_items.get('', {}):
                self.metadata = temp_items['']['METADATA']

            # 섹션별 데이터 복원 헬퍼
            def restore_section(section_key, ext):
                restored = {}
                # Zip 안의 폴더명과 ProjectItems 키가 같다면 바로 사용
                source = temp_items.get(section_key, {})
                for fname, content in source.items():
                    if fname.endswith(ext):
                        name_key = fname.replace(ext, '')
                        restored[name_key] = content
                self.project_items[section_key] = restored

            # 데이터 매핑 및 복원
            mapping = {
                'AI_Data': '.adata', 'AI_World': '.aworld', 'AI_Persona': '.profile',
                'documents': '.doct', 'data': '.data', 'timer': '.time', 'wiki': '.wiki'
            }
            for key, ext in mapping.items():
                restore_section(key, ext)

            self.project_dir = Path(directory)
            self.project_name = name
            
            # 임시 파일 정리
            temp_file = Path('./data/.tmp._tmsw_')
            if temp_file.exists():
                temp_file.unlink()
                
        except Exception as e:
            print(f"Failed to open project: {e}")

    def save_project(self):
        """현재 상태를 파일로 저장"""
        if not self.project_dir or not self.project_name:
            target_path = Path('./data/.tmp._tmsw_')
        else:
            target_path = self.project_dir / self.project_name
        
        self._save_to_zip(target_path)
        print(f"Saved to: {target_path}")

    def _save_to_zip(self, path):
        """실제 Zip 파일 쓰기 로직 (중복 제거됨)"""
        # 확장자 매핑
        ext_map = {
            'AI_Data': '.adata', 'AI_World': '.aworld', 'AI_Persona': '.profile',
            'documents': '.doct', 'data': '.data', 'timer': '.time', 'wiki': '.wiki'
        }

        # 디렉토리 생성
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
                # 메타데이터 저장
                z.writestr('METADATA', json.dumps(self.metadata, ensure_ascii=False, indent=4))
                
                # 각 아이템 저장
                for section, ext in ext_map.items():
                    items = self.project_items.get(section, {})
                    for name, content in items.items():
                        file_path = f"{section}/{name}{ext}"
                        z.writestr(file_path, json.dumps(content, ensure_ascii=False))
        except Exception as e:
            print(f"Save failed: {e}")

    def change_project_title(self, new_title: str):
        if not self.project_dir or not self.project_name:
            self.project_name = new_title
            return

        old_path = self.project_dir / self.project_name
        new_path = self.project_dir / new_title
        
        if old_path.exists():
            try:
                old_path.rename(new_path)
                self.project_name = new_title
            except OSError as e:
                print(f"Rename failed: {e}")

    # =========================================================================
    # Data Accessors (Getter/Setter)
    # =========================================================================
    
    # --- Metadata Access ---
    def program_data(self):
        return self.metadata['ProgrameData']

    def get_position(self):
        pos = self.metadata['ProgrameData']['windows_pos']
        return [pos['x'], pos['y']]

    def get_scale(self):
        scale = self.metadata['ProgrameData']['windows_scale']
        return [scale['width'], scale['height']]

    def update_position(self, x, y):
        self.metadata['ProgrameData']['windows_pos'].update({'x': x, 'y': y})

    def update_scale(self, width, height):
        self.metadata['ProgrameData']['windows_scale'].update({'width': width, 'height': height})
        
    def set_height(self, height):
        self.metadata['ProgrameData']['windows_scale']['height'] = height

    def set_width(self, width):
        self.metadata['ProgrameData']['windows_scale']['width'] = width

    # --- Persona Access ---
    def get_persona_dict(self):
        return self.project_items['AI_Persona']
    
    def get_persona_names(self):
        return self.project_items['AI_Perusona']

    def search_persona_name(self, name: str):
        return name in self.project_items['AI_Persona']

    def updatepersonaName(self, name: str):
        """새 페르소나 생성 (Sample 복사)"""
        print(self.project_items['AI_Persona'].keys())
        if name not in self.project_items['AI_Persona']:
            self.project_items['AI_Persona'][name] = copy.deepcopy(self.DEFAULT_PROJECT_ITEMS['AI_Persona']['sample'])
            return True
        return False

    def _update_persona_field(self, name, field, value, data_type=None):
        """페르소나 필드 업데이트 공통 로직"""
        if name in self.project_items['AI_Persona']:
            self.project_items['AI_Persona'][name][field] = value
            if data_type:
                self.project_items['AI_Persona'][name][f'{field}_data_type'] = data_type
            return True
        return False

    def updatepersonaAge(self, name, age):
        return self._update_persona_field(name, 'age', age)

    def updatepersonaSex(self, name, sex):
        return self._update_persona_field(name, 'sex', sex)

    def updatepersonaHobby(self, name, hobby, data_type):
        return self._update_persona_field(name, 'hobby', hobby, data_type)

    def updatepersonaPersonality(self, name, personality, data_type):
        return self._update_persona_field(name, 'personality', personality, data_type)

    def updatepersonaTendency(self, name, tendency, data_type):
        return self._update_persona_field(name, 'tendency', tendency, data_type)

    def updatepersonaBody(self, name, body, data_type):
        return self._update_persona_field(name, 'body', body, data_type)

    # --- Persona Setters (Self-Image) ---
    def set_ai_persona_self_body(self, name, value):
        self._update_persona_field(name, 'self_body', value)
    
    def set_ai_persona_Self_personality(self, name, value):
        self._update_persona_field(name, 'self_personality', value)
         
    def set_ai_perusona_self_tendency(self, name, value):
        self._update_persona_field(name, 'self_tendency', value)
         
    def Set_AI_Perusona_Self_Image(self, name, value):
        self._update_persona_field(name, 'self_image', value)

    # --- Persona Getters ---
    def getAge(self, name): return self.project_items['AI_Persona'][name].get('age')
    def getSex(self, name): return self.project_items['AI_Persona'][name].get('sex')
    def getPersonality(self, name): return self.project_items['AI_Persona'][name].get('personality')
    def getHobby(self, name): return self.project_items['AI_Persona'][name].get('hobby')
    def getTendency(self, name): return self.project_items['AI_Persona'][name].get('tendency')
    def getBody(self, name): return self.project_items['AI_Persona'][name].get('body')
    
    def getSelfBody(self, name): return self.project_items['AI_Persona'][name].get('self_body', [])
    def getSelfPersonality(self, name): return self.project_items['AI_Persona'][name].get('self_personality', [])
    def getSelfTendency(self, name): return self.project_items['AI_Persona'][name].get('self_tendency', [])
    def getSelfImage(self, name): return self.project_items['AI_Persona'][name].get('self_image', [])
    
    def getPerusonaEditing_windowData(self):
        return self.metadata['ProgrameData']['Persona_editing_windows']

    # =========================================================================
    # Chat Logic
    # =========================================================================
    def get_chat_history(self, name: str):
        """채팅 기록을 시간 순으로 정렬하여 리스트로 반환"""
        chat_list = []
        target_ai = self.project_items.get('AI_Data', {}).get(name, {})

        if not target_ai:
            return []

        # 날짜 정렬
        for date_key in sorted(target_ai.keys()):
            if date_key == 'summary': continue
            
            time_data = target_ai[date_key]
            # 시간 정렬
            for time_key in sorted(time_data.keys()):
                content = time_data[time_key]
                timestamp = f"{date_key} {time_key}"
                
                # User 메시지
                if content.get('user'):
                    chat_list.append({'sender': 'user', 'msg': content['user'], 'timestamp': timestamp})
                
                # AI 메시지 (키가 'name'인 부분)
                if content.get('name'):
                    chat_list.append({'sender': 'ai', 'msg': content['name'], 'timestamp': timestamp})
                    
        return chat_list

    def add_chat_message(self, ai_name: str, sender_type: str, message: str):
        """채팅 메시지 저장"""
        now = datetime.datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # 데이터 경로 안전하게 생성
        ai_data = self.project_items.setdefault('AI_Data', {}).setdefault(ai_name, {})
        date_block = ai_data.setdefault(date_str, {})
        current_block = date_block.setdefault(time_str, {'name': '', 'user': ''})

        if sender_type == 'user':
            current_block['user'] = message
        else:
            current_block['name'] = message # AI 답변

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
    def Call_AI(name: str, input_msg: str, value: int):
        # 1. AI 존재 여부 확인
        if name not in GlobalWorld.Get_AI_Names():
            return None

        # 2. 페르소나(시스템 프롬프트) 구성
        # 여러 줄의 메시지보다 하나의 잘 정리된 블록이 LLM에게 더 강력하게 작용합니다.
        ai_data = GlobalWorld.instance().AI_Memory[name]
        persona_text = f"Your name is {name}.\n"
    
        # 설정 키들을 순회하며 설명 추가
        target_keys = ['age', 'sex', 'personality', 'hobby', 'tendency', 'body']
        for k in target_keys:
            if k in ai_data:
                persona_text += f"Your {k} is {ai_data[k]}.\n"
            
        # [중요] 역할 몰입을 위한 강제 지침 추가
        persona_text += "You must strictly maintain this persona and tone throughout the conversation."

        # 시스템 메시지 생성 (가장 강력한 지침)
        system_message = ("system", persona_text)

        # 3. 사용자 입력 메시지 결정 (전략 패턴 적용)
        # value에 따른 질문 템플릿 정의
        query_map = {
            1: "정의된 네 외모를 특징과 전체 모습을 직접 정의하여 설명하라",
            2: "정의된 내용을 보고 네 성격을 직접 정의하여 설명하라.",
            3: "정의된 내용을 보고 네 성향을 직접 정의하여 설명하라.",
            4: "정의된 내용을 보고 네가 본 네 모습을 직접 정의하여 설명하라."
        }

        # input_msg가 있으면 그걸 쓰고, 없으면 value에 매핑된 질문 사용
        target_query = input_msg if input_msg else query_map.get(value, "")

        if not target_query:
            return None  # 실행할 쿼리가 없는 경우

       # 4. 프롬프트 리스트 조립 (순서가 매우 중요함)
        # [순서] 1. 시스템 설정(페르소나) -> 2. 과거 대화 기록(GlobalWorld.Prompt) -> 3. 현재 질문
        final_messages = [system_message] 
    
        # 기존 대화 내역 복사 및 추가 (기존 Prompt에 시스템 설정이 섞여있지 않다고 가정)
        # 만약 GlobalWorld.Prompt에 이미 system 메시지가 있다면 중복될 수 있으니 주의 필요
        final_messages.extend(copy.deepcopy(GlobalWorld.instance().Prompt))
    
        # 마지막에 사용자 입력 플레이스홀더 추가
        final_messages.append(('user', '{input}'))

        # 5. LangChain 체인 생성 및 실행
        prompt_template = ChatPromptTemplate.from_messages(final_messages)
        output_parser = StrOutputParser()
        chain = prompt_template | GlobalWorld.instance().llm | output_parser

        # 실행
        return chain.invoke({'input': target_query})
    # Create_AI_Memory 
    def Create_AI_Memory(name:str):
        if name not in GlobalWorld.instance().AI_Memory.keys():
            GlobalWorld.instance().AI_Memory = {name : {}}
        return GlobalWorld.instance().AI_Memory is not None
    # 기존에 저장된 페르소나를 입력받는 메소드
    def Create_AI_Persona(name:str, Persona:dict):
        key_list = ['age', 'sex', 'personality', 'hobby', 'tendency', 'body', 'self_body', 'self_personality', 'self_tendency', 'self_image']
        for k in key_list:
            GlobalWorld.instance().AI_Memory[name][k] = Persona[k]
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
    def check_Persona(name:str, key:list):
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
            if k not in GlobalWorld.Get_AI_Persona(name).keys():
                return -1
            else:
                if checking_type(GlobalWorld.Get_AI_Persona(name)[k] == 1):
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Persona(name)[k]) == 2):
                    if len(checking_type) == 0:
                        return code_return[k]
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Persona(name)[k]) == 3):
                    if len(checking_type.keys()) == 0:
                        return code_return[k]
                    continue
                elif (checking_type(GlobalWorld.Get_AI_Persona(name)[k]) == 4):
                    if len(checking_type) == 0:
                        return code_return[k]
                    continue
                elif checking_type(GlobalWorld.Get_AI_Persona(name)[k] == -1):
                    return -12
                else:
                    continue
        return True
    # Self_body, 즉 AI가 대화를 통해 정의한 자신의 외형을 설정하는 메소드
    def Set_AI_Persona_Self_body(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_body'] = data
    # Self_personality, 즉 AI가 대화를 통해 정의한 자신의 성격을 설정하는 메소드
    def Set_AI_Persona_Self_Personality(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_personality'] = data
    # Self_Tendency, 즉 AI가 대화를 통해 정의한 자신의 성향을 설정하는 메소드
    def Set_AI_Persona_Self_Tendency(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_tendency'] = data
    # Self_Image, 즉 AI가 대화를 통해 정의한 자신의 이미지를 설정하는 메소드
    def Set_AI_Persona_Self_Image(name:str, data:str):
        GlobalWorld.instance().AI_Memory[name]['self_image'] = data
    # AI Persona를 반환하는 메소드.
    def Get_AI_Persona(name:str):
        return GlobalWorld.instance().AI_Memory[name]
    # 실행중인 AI Persona의 정보의 key를 받아오는 메소드
    def Get_AI_Names():
        return GlobalWorld.instance().AI_Memory.keys()
    def Get_last_talk():
        return GlobalWorld.instance().Prompt[-1]
    # 생성자
    def __init__(self):
        self.AI_Memory = {}
    @staticmethod
    # singleton 패턴 인스턴스
    def instance():
        if GlobalWorld._instance is None:
            GlobalWorld._instance = GlobalWorld()
        return GlobalWorld._instance