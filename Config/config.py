import json, os, platform, re
from enum import Enum, unique

# 프로그램 config 파일을 읽어오는 클래스
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
#프로젝트의 Config를 읽어오는 클래스
class ProjectConfig:
    def __init__(self, config_dir:str):
        self.update_dir = False
        self.root_dir = config_dir
        self.opened_file = 'programeWindows.json'
        self.can_open = False
        if not self.__start__():
            print("can not open windows")
    def __start__(self):
        self.__check__()
        if self.__open_Check__() == None:
            print('Can not Open Window')
            return False
    def __check__(self):
        if platform.system() == 'Windows':
            if self.opened_file not in os.listdir(self.root_dir):
                self.WIN_Create_Files()
            else:
                self.WIN_Read_Files()
    def __open_Check__(self):
        print(type(self.data))
        return None
    def WIN_Create_Files(self):
        File_Tag = {}
        File_Tag['title'] = self.root_dir.split('\\')[-1]
        File_Tag['opened_Window'] = []
        groups = []
        for f in os.listdir(self.root_dir):
            if os.path.isdir(f"{self.root_dir}/{f}"):
                groups.append(f)
                File_Tag[f] = os.listdir(f"{self.root_dir}/{f}")
        File_Tag['groups'] = groups
        
        with open(self.root_dir + '/' + self.opened_file, 'w', encoding='utf-8') as file:
            json.dump(File_Tag, file)
        self.data = File_Tag
    def WIN_Read_Files(self):
        file_dir = self.root_dir + '/' + self.opened_file
        if os.path.exists(file_dir):
            with open(file_dir, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        else:
            self.WIN_Create_Files()
            self.WIN_Read_Files()
    def OpenWindow(self, dir:str):
        if 'opened_Window' in self.data.keys():
            opened = self.data['opened_Window']
            if dir not in opened:
                self.data['opened_Window'].append(dir)
                self.update_dir = True
                self.can_open = True
            elif os.path.exists(dir):
                self.update_dir = False
                self.can_open = True
        else:
            self.update_dir = False
            self.can_open = False
    def getOpenWindow(self):
        if 'opened_Window' in self.data.keys():
            return self.data['opened_Window']
        else:
            return []
    def __del__(self):
        if self.update_dir:
            with open(self.root_dir + '/' + self.opened_file, 'w', encoding='utf-8') as file:
                json.dump(self.data, file)
# 위키 도큐멘트를 해독하고 저장하며 관리하는 클래스
class WikiDocuments:
    """
    사용자 정의 DSL 텍스트를 파싱하여
    씬(Scene)에 그릴 객체 정보(dict)의 리스트로 변환합니다.

    Body DSL 형식
    <body type:[box,x:10,y:40,w:280,h:480]>
        <title>
            title
        </title>
        <text:10px,nomal,nanumgodic>
        
        </text>
    </Body>
    """
    # 1. <Body ...> </Body>의 블록 전체를 찾음 (대소문자 무시)
    BODY_Block_RE = re.compile(r"<body(.*?>(.*?)</body>)", re.IGNORECASE | re.DOTALL)
    # 2. <body> 태그 내부의 type 속성을 찾음
    TYPE_ATTR_RE = re.compile(r'type:\[(.*?)\]', re.IGNORECASE)
    # 3. type:[...] 내부의 key:value를 찾음
    ATTR_KV_RE = re.compile(r"(\w+):([\w\d\.-]+)")
    # 4. <body> 내용물에서 <title> </title>을 찾음
    TITLE_TAG_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
    # 5. <text> 내용물에서 <text:...>...</text>를 찾음
    # 첫번째 그룹 : Style 속성
    # 두번째 그룹 : 텍스트 내용
    TEXT_TAG_RE = re.compile(r"<text:(.*?)>(.*?)</text>", re.IGNORECASE | re.DOTALL)

    @staticmethod
    def parse_context(content_str:str):
        """DSL 텍스트를 파싱하여 객체 정보 딕셔너리의 리스트로 반환합니다."""
        body = []
        if not content_str:
            return body
        for body_match in WikiDocuments.BODY_Block_RE.finditer(content_str):
            body_attributes_str = body_match.group(1)
            body_content_str = body_match.group(2)

            obj_data = {}

            type_match = WikiDocuments.TYPE_ATTR_RE.search(body_attributes_str)
            if not type_match:
                continue # type이 없는 body는 무시

            type_val_str = type_match.group(1) # 예 : box,x:10,y:40...
            type_parts = type_val_str.split(',')
            
            obj_data['type'] = type_parts[0].lower().strip() # box
            for part in type_parts[1:]:
                kv_match = WikiDocuments.ATTR_KV_RE.search(part)
                if kv_match:
                    key = kv_match.group(1).lower().strip()
                    value = kv_match.group(2).lower().strip()
                    try:
                        obj_data[key] = float(value)
                    except ValueError:
                        obj_data[key] = value
            title_match = WikiDocuments.TITLE_TAG_RE.search(body_content_str)
            if title_match:
                obj_data['title'] = title_match.group(1).strip()
            
            text_match = WikiDocuments.TEXT_TAG_RE.search(body_content_str)
            if text_match:
                style_str = text_match.group(1) # 10px.nomal.nanumgodic
                obj_data['text'] = text_match.group(2) # 텍스트 내용
                # 스타일 문자 파싱
                try:
                    style_parts = [s.strip() for s in style_str.split(',')]
                    obj_data['font_size'] = style_parts[0].replace('px', '')
                    obj_data['font_weight'] = style_parts[1].lower()
                    obj_data['font_family'] = style_parts[2]
                except(IndexError, AttributeError):
                    print(f'텍스트 파싱 오류 : {style_str}')
                body.append(obj_data)
        return body
    def __init__(self, dir:str):
        self.file_dir = dir
        self.__start__()
    def __start__(self):
        self.OpenFile()
        self.Check_keys()
    def Check_keys(self):
        if 'height' not in self.file_data.keys():
            self.file_data['height'] = 400
        if 'width' not in self.file_data.keys():
            self.file_data['width'] = 500
        if 'xPos' not in self.file_data.keys():
            self.file_data['xPos'] = 100
        if 'yPos' not in self.file_data.keys():
            self.file_data['yPos'] = 100
        if 'index' not in self.file_data.keys():
            self.file_data['index'] = []
        if 'body' not in self.file_data.keys():
            self.file_data['body'] = {}
        if 'documents_ratio' not in self.file_data.keys():
            self.file_data['documents_ratio'] = {}
    def documentRatio(self, x:int):
        if 1000 < x:
            self.file_data['documents_ratio']['first_width'] = 50
            self.file_data['documents_ratio']['second_width'] = 50
        else:
            self.file_data['documents_ratio'] = {'first_width' : x}
            self.file_data['documents_ratio']['second_width'] = 100 - x
        self.Save_Data()
    def documentRatios(self, x1: int, x2:int):
        self.file_data['documents_ratio']['first_width'] = x1
        self.file_data['documents_ratio']['second_width'] = x2
        self.Save_Data()
    def MakeNewBoxBody(self, title:str):
        return f"<body type:[box,x:10,y:40,w:280,h:480]><title>{title}</title><text:10px,nomal,nanumgodic> </text></Body>"
    def Body(self, index:str):
        if index not in self.file_data['index']:
            return None
        elif index in self.file_data['index'] and index not in self.file_data['body'].keys():
            self.file_data['body'][index] = {self.MakeNewBoxBody}
        elif index in self.file_data['index'] and len(self.file_data['body'][index]) == 0:
            self.file_data['body'][index] = self.MakeNewBoxBody(index)
        return self.file_data['body'][index]
    def DocumentRatio(self):
        return self.file_data['documents_ratio']
    def DocumentRatios(self):
        return [self.file_data['documents_ratio']['first_width'], self.file_data['documents_ratio']['second_width']]
    def getBody(self, key:str):
        if key not in self.file_data['body'].keys():
            return None
        else:
            return self.file_data['body'].keys()
    def keys(self):
        return self.file_data.keys()
    def indexs(self):
        return self.file_data['index']
    def bodys(self):
        return self.file_data['body']
    def AppendKey(self, value, new_index : str):
        self.file_data[new_index] = value
        self.Save_Data()
    def getKeys(self, key:str):
        if key not in self.file_data.keys():
            return None
        else:
            return self.file_data[key]
    def DocumentViewColor(self):
        if 'Document_View_Color' not in self.file_data.keys():
            return None
        else:
            self.file_data['Document_View_Color']
    def DocumentFontColor(self):
        if 'Document_Font_Color' not in self.file_data.keys():
            return None
        else:
            self.file_data['Document_Font_Color']
    def x(self, x:int):
        self.file_data['xPos'] = x
        self.Save_Data()
    def y(self, y:int):
        self.file_data['yPox'] = y
        self.Save_Data()
    def width(self, width:int):
        self.file_data['width'] = width
        self.Save_Data()
    def height(self, height:int):
        self.file_data['height'] = height
        self.Save_Data()
    def X(self):
        return self.file_data['xPos']
    def Y(self):
        return self.file_data['yPos']
    def Width(self):
        return self.file_data['width']
    def Height(self):
        return self.file_data['height']
    def OpenFile(self):
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            self.file_data = json.load(file)
    def AppendIndex(self, new:str):
        if type(self.file_data) is dict:
            if new not in self.file_data['index']:
                self.file_data['index'].append(new)
                self.file_data['body'][new] = []
                self.Save_Data()
                return True
            else:
                return False
        print(self.file_data)
        self.Save_Data()
    def FindBody(self, index:str):
        return index in self.file_data['body'].keys()
    def index_len(self):
        return len(self.file_data['index'])
    def swap_index(self, i, j):
        if i <= len(self.file_data['index']) and j <= len(self.file_data['index']):
            self.file_data['index'][i], self.file_data['index'][j] = self.file_data['index'][j], self.file_data['index'][i]
            self.Save_Data()
            return True
        else:
            return False
    def InsertBody(self, index:str, sentence:str, Code:list):
        print(Code)
        if index not in self.file_data['index'] or index not in self.file_data['body'].keys():
            return False
        else:
            body = None
            l = len(self.file_data['body'][index]) + 1
            if len(Code) == 0:
                body = f'<text style:nomal,body,10-{l}>{sentence}</text>'
                self.file_data['body'][index].append(body)
            else:
                body = f'<text style:{','.join([c for c in Code])}-{l}>{sentence}</text>'
            self.file_data['body'][index] = body
            self.Save_Data()
            return True
    def Save_Data(self):
        with open(self.file_dir, 'w', encoding='utf-8') as file:
            json.dump(self.file_data, file)
    def __del__(self):
        self.Save_Data()
        print('Wiki Document delete')
# 메인 메뉴의 액션을 구분하기 위한 전용 클래스
@unique
class ProgrameAction(Enum):
    ### 프로그램 동작 관련 액션 시그널 ###
    # 프로그램이 열렸습니다.
    ProgrameStart = 0x0fff000
    # 프로그램이 실행중입니다.
    ProgrameDuring = 0x0fff001
    # 포커스를 벗어났습니다.
    ProgrameOut = 0x0fff002
    # 포커스를 얻었습니다.
    ProgrameIn = 0x0fff003
    ### 서브 윈도우 및 프로그램 동작 변수 관련 액션 시그널 ###
    # 서브 윈도우 창이 열렸습니다.
    SubWindowsOpened = 0x1fff000
    # 프로젝트 생성에 성공했습니다.
    ProjectCreateSuccess = 0x1fff001
    # 프로젝트 생성에 실패했습니다.
    ProjectCreateFailed = 0x1fff002
    # 프로젝트 생성을 취소했습니다.
    CancleProjectCreate = 0x1fff003
    # 프로젝트가 열리지 않았습니다.
    NotOpenedProject = 0x1fff004
    # 프로젝트 여는 것을 취소했습니다.
    CancleOpenedProject = 0x1fff005
    # 프로젝트가 열렸습니다.
    OpenProjectSuccess = 0x1fff006
    # 프로젝트 여는 것에 실패했습니다.
    CannotOpenProject = 0x1fff007
    # 파일을 생성했습니다.
    CreateFiles = 0x1fff008
    # 프로젝트 경로가 설정되었습니다.
    SetTheProjectDir = 0x1fff009
    # UI가 업데이트 되었습니다.
    UpdateUI = 0x1fff00a
    # TreeView가 업데이트 되었습니다.
    UpdateTreeView = 0x1fff00b
    # TreeView에서 선택이 변경되었습니다.
    SelectTreeView = 0x1fff00c
    # TreeView의 작업이 완료되었습니다.
    FinishedTreeViewWork = 0x1fff00d
    # TreeView의 갱신을 실패했습니다.
    FailedTreeViewUpdate = 0x1fff00e
    # 서브 윈도우가 닫혔습니다.
    SubWindowsClosed = 0x1fff00f
    # 서브 윈도우에서 벗어났습니다.
    SubWindowsOut = 0x1fff010
    # 서브 윈도우 동작중
    SubWindowsDuring = 0x1fff011
    # WikiView가 성공적으로 열렸습니다.
    WikiViewOpenedSuccess = 0x1fff012
    # WikiView를 여는 것에 실패했습니다.
    WikiViewOpenedFailed = 0x1fff013
    # 열린 WikiView를 확인합니다.
    WikiViewChecked = 0x1fff014
    # WikiView를 엽니다.
    WikiViewOpening = 0x1fff015
    # 인덱스가 추가되었습니다.
    AppendIndex = 0x1fff016
    # 인덱스가 삭제되었습니다.
    DeleteIndex = 0x1fff017
    # 인덱스 내용이 갱신되어, 업데이트가 필요합니다.
    UpdateWikiData = 0x1fff018
    # 위키 뷰의 인덱스를 로드합니다.
    LoadIndex = 0x1fff019
    # 위키 뷰를 초기화 합니다.
    UpdateWikiView = 0x1fff01a
    # 위키 트리 뷰를 초기화 합니다.
    UpdateWikiTreeView = 0x1fff01b