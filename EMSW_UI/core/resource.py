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

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from pathlib import Path
from typing import Union, Dict, List, Any
import copy, os, json, zipfile, time, pytz, requests, subprocess

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
        'documents': {'sample': {'title': {}, 'index': {}, 'text': {}, 'range':0}},
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
            self._save_to_file('./data/.tmp._tmsw_')

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

    # 문서 파일을 추가했을 때 문서 파일의 데이터를 추가하면서 수행할 작업
    def open_document_files(self, name:str, title:str, text:str):
        file = copy.deepcopy(self.DEFAULT_PROJECT_ITEMS['documents']['sample'])
        file['tilte'] = {title : 1}
        file['index'] = {1 : title}
        file['text'] = {1 : text}
        file['range'] += 1
        self.project_items['documents'][name] = file
        
        # 자동 저장.
        self.save_project()

    def save_project(self):
        """현재 상태를 파일로 저장"""
        if not self.project_dir or not self.project_name:
            target_path = Path('./data/.tmp._tmsw_')
        else:
            target_path = self.project_dir / self.project_name
        
        self._save_to_file(target_path)
        print(f"Saved to: {target_path}")

    def _save_to_file(self, path):
        """file 파일 쓰기 로직 (중복 제거됨)"""
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
    
    def set_Persona_editing_windows_geometry(self, x, y, w, h):
        self.metadata['ProgrameData']['Persona_editing_windows'].update(zip(['x', 'y', 'w', 'h'], [x, y, w, h]))
    
    def update_document_title(self, name, title:str, range:int):
        self.project_items['documents'][name]['title'][title] = range
    
    def update_index(self, name, title:str):
        l = len(self.project_items['documents'][name]['index'].keys())
        self.project_items['documents'][name]['index'][l] = title

    # --- Persona Access ---
    def get_persona_dict(self):
        return self.project_items['AI_Persona']
    
    def get_persona_names(self):
        return self.project_items['AI_Persona'].keys()

    def search_persona_name(self, name: str):
        return name in self.project_items['AI_Persona']

    def update_persona_Name(self, name: str):
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
    
    def getPersonaEditing_WindowData(self): return self.metadata['ProgrameData']['Persona_editing_windows']

    # --- documents Getters ---

    def get_documents_name(self): return [item for item in self.project_items['documents'].keys() if 'sample' not in item]
    def get_documents_title(self, name:str): return self.project_items['documents'][name]['title']
    def get_documents_index(self, name:str): return self.project_items['documents'][name]['index']
    def get_documents_text(self, name:str): return self.project_items['documents'][name]['text']
    def get_documents_range(self, name:str): return self.project_items['documents'][name]['range']

    # --- loader GlobalWorld ---

    def load_global(self):
        """
            기존에 생성된 AI를 Global로 업로드 함.
        """
        names = self.get_persona_names()
        if len(names) == 0:
            return False
        
        for n in names:
            GlobalWorld().create_ai_memory(n)
            GlobalWorld().set_persona_data(name = n, persona_data = self.get_persona_dict()[n])

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

class GlobalWorld:
    """
    중앙 AI LLM 제어 및 설정 관리 클래스 (Singleton).
    Ollama 프로세스 관리, AI 메모리, 프롬프트 생성 및 실행을 담당합니다.
    """
    _instance = None

    # 상수 설정
    OLLAMA_HOST = "http://127.0.0.1:11434"
    DEFAULT_TEMPERATURE = 0.7
    
    # 데이터 키 정의
    PERSONA_KEYS = [
        'age', 'sex', 'personality', 'hobby', 'tendency', 
        'body', 'self_body', 'self_personality', 'self_tendency', 'self_image'
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalWorld, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
            
        self.ai_memory: Dict[str, Dict[str, Any]] = {}
        self.prompt_history: List[tuple] = []
        self.llm = None
        self._initialized = True

    # =========================================================================
    # Ollama Process Management
    # =========================================================================
    def is_ollama_running(self) -> bool:
        """Ollama 서버가 실행 중인지 확인합니다."""
        try:
            response = requests.get(f"{self.OLLAMA_HOST}/api/tags", timeout=1)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_ollama(self) -> bool:
        """Ollama 서버를 서브 프로세스로 실행합니다."""
        if self.is_ollama_running():
            print("✔ Ollama 서버가 이미 실행 중입니다.")
            return True

        try:
            cmd = ["ollama", "serve"]
            # Windows: CREATE_NEW_CONSOLE flags (subprocess.CREATE_NEW_CONSOLE is approx 16)
            creation_flags = subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            
            subprocess.Popen(cmd, creationflags=creation_flags)
            
            # 서버 시작 대기 (최대 10초)
            for _ in range(10):
                if self.is_ollama_running():
                    print("✔ Ollama 서버 실행됨.")
                    return True
                time.sleep(1)
            
            print("❌ Ollama 서버 실행 실패 (타임아웃).")
            return False
        except Exception as e:
            print(f"❌ Ollama 실행 중 오류 발생: {e}")
            return False

    # =========================================================================
    # LLM & Prompt Management
    # =========================================================================
    def get_llm(self, model_name: str, temperature: float = DEFAULT_TEMPERATURE):
        """LangChain ChatOllama 인스턴스를 반환하거나 생성합니다."""
        # 모델이나 설정이 바뀌면 재생성 필요 (단순 싱글톤 유지가 아니라 팩토리 성격이 필요할 수 있음)
        # 여기서는 기존 로직을 유지하되 인스턴스가 없으면 생성
        if self.llm is None:
            self.llm = ChatOllama(model=model_name, temperature=temperature)
        return self.llm

    def init_prompt_data(self):
        """기본 시스템 프롬프트를 초기화합니다."""
        if not self.prompt_history:
            self.prompt_history = [("system", "You are a helpful assistant.")]
            return True
        return False

    def add_prompt(self, role: str, message: str) -> bool:
        """프롬프트 히스토리에 메시지를 추가합니다."""
        if self.prompt_history is None:
             self.init_prompt_data()
        self.prompt_history.append((role, message))
        return True
    
    def get_last_talk(self):
        """가장 최근 대화 내용을 반환합니다."""
        return self.prompt_history[-1] if self.prompt_history else None

    def call_ai(self, name: str, input_msg: str, mode_value: int):
        """
        AI 모델을 호출하여 응답을 생성합니다.
        mode_value: 0=Chat, 1=Body, 2=Personality, 3=Tendency, 4=Image
        """
        # 1. AI 존재 확인
        if name not in self.ai_memory:
            return None

        # 2. 페르소나(시스템 프롬프트) 구성
        ai_data = self.ai_memory[name]
        persona_text = f"Your name is {name}.\n"
        
        for k in ['age', 'sex', 'personality', 'hobby', 'tendency', 'body']:
            if k in ai_data:
                persona_text += f"Your {k} is {ai_data[k]}.\n"
        
        persona_text += "You must strictly maintain this persona and tone throughout the conversation."
        system_message = ("system", persona_text)

        # 3. 질문 템플릿 선택 (Query Map)
        query_map = {
            1: "정의된 네 외모를 특징과 전체 모습을 직접 정의하여 설명하라",
            2: "정의된 내용을 보고 네 성격을 직접 정의하여 설명하라.",
            3: "정의된 내용을 보고 네 성향을 직접 정의하여 설명하라.",
            4: "정의된 내용을 보고 네가 본 네 모습을 직접 정의하여 설명하라."
        }
        
        # 입력 메시지가 있으면 우선 사용, 없으면 모드에 따른 쿼리 사용
        target_query = input_msg if input_msg else query_map.get(mode_value, "")
        
        if not target_query:
            return None

        # 4. 프롬프트 메시지 조립
        # [System Persona] + [History] + [Current Input]
        final_messages = [system_message]
        final_messages.extend(copy.deepcopy(self.prompt_history))
        final_messages.append(('user', '{input}'))

        # 5. 실행
        if self.llm is None:
            # LLM이 초기화되지 않았으면 기본값으로 초기화 시도 (혹은 에러 처리)
            return None

        prompt_template = ChatPromptTemplate.from_messages(final_messages)
        output_parser = StrOutputParser()
        chain = prompt_template | self.llm | output_parser

        return chain.invoke({'input': target_query})

    # =========================================================================
    # Memory & Persona Management
    # =========================================================================
    def create_ai_memory(self, name: str) -> bool:
        """새로운 AI 메모리 공간을 생성합니다."""
        if name not in self.ai_memory:
            self.ai_memory[name] = {}
            return True
        return True # 이미 존재해도 성공으로 간주

    def get_ai_names(self):
        """메모리에 등록된 AI 이름 목록을 반환합니다."""
        return self.ai_memory.keys()

    def get_ai_persona(self, name: str) -> Dict:
        """특정 AI의 페르소나 데이터를 반환합니다."""
        return self.ai_memory.get(name, {})

    def set_persona_data(self, name: str, persona_data: dict) -> bool:
        """
        딕셔너리 형태의 페르소나 데이터를 한 번에 설정하고 필수 키를 검증합니다.
        """
        if name not in self.ai_memory:
            self.create_ai_memory(name)
            
        # 데이터 복사 및 설정
        target_memory = self.ai_memory[name]
        for k in self.PERSONA_KEYS:
            if k in persona_data:
                target_memory[k] = persona_data[k]
        
        # 필수 Self 데이터 검증
        required_self_keys = ['self_body', 'self_personality', 'self_tendency', 'self_image']
        for key in required_self_keys:
            val = target_memory.get(key)
            if not val or len(val) == 0:
                return False
        return True

    def check_persona_integrity(self, name: str, keys_to_check: list) -> Union[int, bool]:
        """
        페르소나 데이터의 무결성을 검사합니다.
        Return: 0(성공), 음수(에러 코드)
        """
        if name not in self.ai_memory:
            return -1

        # 에러 코드 매핑
        error_codes = {
            'age': -2, 'sex': -3, 'personality': -4, 'hobby': -5, 
            'tendency': -6, 'body': -7, 'self_body': -8, 
            'self_personality': -9, 'self_tendency': -10, 'self_image': -11
        }
        
        persona = self.ai_memory[name]

        for k in keys_to_check:
            if k not in persona:
                return error_codes.get(k, -12)
            
            value = persona[k]
            
            # 타입 및 데이터 존재 여부 확인 (Pythonic하게 단순화)
            # 빈 문자열, 빈 리스트, 빈 딕셔너리는 False로 평가됨
            if not value and not isinstance(value, int): # int 0은 데이터가 있는 것으로 간주할 경우 주의
                 return error_codes.get(k, -12)

        return 0 # 성공

    # =========================================================================
    # Setters (개별 설정)
    # =========================================================================
    def set_ai_persona_self_body(self, name: str, data: str):
        self.ai_memory[name]['self_body'] = data

    def set_ai_persona_self_personality(self, name: str, data: str):
        self.ai_memory[name]['self_personality'] = data

    def set_ai_persona_self_tendency(self, name: str, data: str):
        self.ai_memory[name]['self_tendency'] = data

    def set_ai_persona_self_image(self, name: str, data: str):
        self.ai_memory[name]['self_image'] = data