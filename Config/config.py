from enum import Enum

# 메인 메뉴의 액션을 구분하기 위한 전용 클래스
class ProgrameAction(Enum):
    ### 프로그램 동작 관련 액션 시그널 ###
    # 프로그램이 열렸다는 시그널
    ProgrameStart = 0xfff000
    # 활성화된 디스플레이를 식별한 시그널
    SetWindowPosition = 0xfff001
    # 띄울 창의 위치를 변경한 시그널
    FixedWindowPosition = 0xfff002
    # 프로그램의 UI를 만듭니다.
    MakeUI = 0xfff003
    # 프로그램이 실행중입니다.
    ProgrameDuring = 0xfff003
    # 서브 윈도우 창이 열렸습니다.
    SubWindowsOpened = 0xfff004
    # 프로젝트 생성에 성공했습니다.
    ProjectCreateSuccess = 0xfff005
    # 프로젝트 생성에 실패했습니다.
    ProjectCreateFailed = 0xfff006
    # 프로젝트 생성을 취소했습니다.
    CancleProjectCreate = 0xfff007
    # 프로젝트가 열리지 않았습니다.
    NotOpenedProject = 0xfff008
    # 프로젝트 여는 것을 취소했습니다.
    CancleOpenedProject = 0xfff009
    # 프로젝트가 열렸습니다.
    OpenProjectSuccess = 0xfff00a
    # 프로젝트 여는 것에 실패했습니다.
    CannotOpenProject = 0xfff00b
    # 파일을 생성했습니다.
    CreateFiles = 0xfff00c
    # 프로젝트 경로가 설정되었습니다.
    SetTheProjectDir = 0xfff00d
    # UI가 업데이트 되었습니다.
    UpdateUI = 0xfff00e
    # TreeView가 업데이트 되었습니다.
    UpdateTreeView = 0xfff00f
    # TreeView에서 선택이 변경되었습니다.
    SelectTreeView = 0xfff010
    # TreeView의 작업이 완료되었습니다.
    FinishedTreeViewWork = 0xfff011
    # TreeView의 갱신을 실패했습니다.
    FailedTreeViewUpdate = 0xfff012
    # 서브 윈도우가 닫혔습니다.
    SubWindowsClosed = 0xfff013
    # 서브 윈도우에서 벗어났습니다.
    SubWindowsOut = 0xfff014
    # 서브 윈도우 동작중
    SubWindowsDuring = 0xfff015
    # WikiView가 성공적으로 열렸습니다.
    WikiViewOpenedSuccess = 0xfff016
    # WikiView를 여는 것에 실패했습니다.
    WikiViewOpenedFailed = 0xfff017
    # 열린 WikiView를 확인합니다.
    WikiViewChecked = 0xfff018
    # WikiView를 엽니다.
    WikiViewOpening = 0xfff019
    # 인덱스가 추가되었습니다.
    AppendIndex = 0xfff01a
    # 인덱스가 삭제되었습니다.
    DeleteIndex = 0xfff01b
    # 인덱스 내용이 갱신되어, 업데이트가 필요합니다.
    UpdateWikiData = 0xfff01c
    # 위키 뷰의 인덱스를 로드합니다.
    LoadIndex = 0xfff01d
    # 위키 뷰를 초기화 합니다.
    UpdateWikiView = 0xfff01e
    # 위키 트리 뷰를 초기화 합니다.
    UpdateWikiTreeView = 0xfff01f
    # 키보드가 입력되었습니다.
    PressKeyboardEvent = 0xfff020
    # AI가 로드중입니다.
    LoadLLMModel = 0xfff021
    # 잘못된 AI 모델의 이름입니다.
    WrongLLMModelName = 0xfff022
    # AI 로드가 완료되었습니다.
    FinishedLoadLLM = 0xfff023
    # AI의 페르소나를 제작합니다.
    CreateAIPerusona = 0xfff024
    # AI의 페르소나가 제작취소되었습니다.
    CancleCreateAIPerusona = 0xfff025
    # AI의 이름을 설정해주세요.
    NeedToAIName = 0xfff026
    # AI의 이름을 설정했습니다.
    SetAIPerusonaName = 0xfff027
    # AI의 성별을 설정해주세요.
    NeedToAISex = 0xfff028
    # AI의 성별을 설정했습니다.
    SetAIPerusonaSex = 0xfff029
    # AI의 연령을 설정해주세요.
    NeedToAIAge = 0xfff02a
    # AI의 연령을 설정했습니다.
    SetAIPerusonaAge = 0xfff02b
    # AI의 성격을 설정해 주세요.
    NeedToAIPersonality = 0xfff02c
    # AI의 성격을 설정했습니다.
    SetAIPerusonaPersonality = 0xfff02d
    # AI의 성향을 설정해 주세요.
    NeedToAITendency = 0xfff02e
    # AI의 성향을 설정했습니다.
    SetAIPerusonaTendency = 0xfff02f
    # AI의 취미를 설정해 주세요.
    NeedToAIHubby = 0xfff030
    # AI의 취미를 설정했습니다.
    SetAIPerusonaHubby = 0xfff031
    # AI의 외형을 설정해 주세요
    NeedToAIBody = 0xfff032
    # AI의 외형을 설정했습니다.
    SetAIPerusonaBody = 0xfff033
    # AI가 스스로의 성격을 생각합니다.
    ThinkPersonalityAISelf = 0xfff034
    # AI의 성격을 정의합니다.
    AIDefineSelfPersonality = 0xfff035
    # AI의 성격을 고칩니다.
    FixedAIDefineSelfPersonality = 0xfff036
    # AI가 스스로의 성격을 생각합니다.
    ThinkTendencyAISelf = 0xfff037
    # AI의 성향을 정의합니다.
    AIDefineSelfTendency = 0xfff038
    # AI의 성향을 고칩니다.
    FixedAIDefineSelfTendency = 0xfff039
    # AI가 스스로의 외형을 생각합니다.
    ThinkBodyAISelf = 0xfff03a
    # AI의 외형을 정의합니다.
    AIDefineSelfBody = 0xfff03b
    # AI의 외형을 고칩니다.
    FixedAIDefineSelfBody = 0xfff03c
    # AI가 스스로의 자아를 생각합니다.
    ThinkSelfImageAISelf = 0xfff03d
    # AI의 자아를 정의합니다.
    AIDefineSelfImage = 0xfff03e
    # AI의 자아를 고칩니다.
    FixedAIDefineSelfImage = 0xfff03f
    # 다음 항목으로 넘어간다.
    PassNextArticles = 0xfff040
    # AI의 페르소나가 완성되었습니다.
    FinishedCreationAIPerusona = 0xfff041
    # AI에게 메시지를 보냈습니다.
    SendMessageLLM = 0xfff042
    # AI가 답변을 생성했습니다.
    CreateAnswerLLM = 0xfff043
    # AI가 대화 내용을 정리중입니다.
    ArrangementOfTalk = 0xfff044
    # 글로벌 룰을 어겼는지 검사중입니다.
    CheckingGlobalRule = 0xfff045
    # 다시 생성합니다.
    Regenerator = 0xfff046
    # AI 페르소나를 다시 만드세요.
    RemakeAIPerusona = 0xfff047
    # AI 패르소나를 불러옵니다.
    LoadAIPerusona = 0xfff048
    # JsonFile에 오류가 발생했습니다.
    ErrorFileJson = 0xfff049
    # 파일을 저장하라는 메시지를 보냅니다.
    SaveTheFile = 0xfff04a
    # 프로그램의 위치를 변경합니다.
    ChangeProgramePosition = 0xfff04b

EVENT_MAPPING = {
    ProgrameAction.ProgrameStart: "ProgrameAction",
    ProgrameAction.ProgrameDuring: "ProgrameDuring",
    ProgrameAction.ProgrameStart: "ProgrameStart",
    ProgrameAction.ProgrameDuring: "ProgrameDuring",
    ProgrameAction.SubWindowsOpened: "SubWindowsOpened",
    ProgrameAction.ProjectCreateSuccess: "ProjectCreateSuccess",
    ProgrameAction.ProjectCreateFailed: "ProjectCreateFailed",
    ProgrameAction.CancleProjectCreate: "CancleProjectCreate",
    ProgrameAction.NotOpenedProject: "NotOpenedProject",
    ProgrameAction.CancleOpenedProject: "CancleOpenedProject",
    ProgrameAction.OpenProjectSuccess: "OpenProjectSuccess",
    ProgrameAction.CannotOpenProject: "CannotOpenProject",
    ProgrameAction.CreateFiles: "CreateFiles",
    ProgrameAction.SetTheProjectDir: "SetTheProjectDir",
    ProgrameAction.UpdateUI: "UpdateUI",
    ProgrameAction.UpdateTreeView: "UpdateTreeView",
    ProgrameAction.SelectTreeView: "SelectTreeView",
    ProgrameAction.FinishedTreeViewWork: "FinishedTreeViewWork",
    ProgrameAction.FailedTreeViewUpdate: "FailedTreeViewUpdate",
    ProgrameAction.SubWindowsClosed: "SubWindowsClosed",
    ProgrameAction.SubWindowsOut: "SubWindowsOut",
    ProgrameAction.SubWindowsDuring: "SubWindowsDuring",
    ProgrameAction.WikiViewOpenedSuccess: "WikiViewOpenedSuccess",
    ProgrameAction.WikiViewOpenedFailed: "WikiViewOpenedFailed",
    ProgrameAction.WikiViewChecked: "WikiViewChecked",
    ProgrameAction.WikiViewOpening: "WikiViewOpening",
    ProgrameAction.AppendIndex: "AppendIndex",
    ProgrameAction.DeleteIndex: "DeleteIndex",
    ProgrameAction.LoadIndex: "LoadIndex",
    ProgrameAction.UpdateWikiView: "UpdateWikiView",
    ProgrameAction.UpdateWikiTreeView: "UpdateWikiTreeView",
    ProgrameAction.PressKeyboardEvent: "PressKeyboardEvent",
    ProgrameAction.LoadLLMModel: "LoadLLMModel",
    ProgrameAction.WrongLLMModelName: "WrongLLMModelName",
    ProgrameAction.FinishedLoadLLM: "FinishedLoadLLM",
    ProgrameAction.CreateAIPerusona: "CreateAIPerusona",
    ProgrameAction.SetAIPerusonaName: "SetAIPerusonaName",
    ProgrameAction.SetAIPerusonaSex: "SetAIPerusonaSex",
    ProgrameAction.SetAIPerusonaPersonality: "SetAIPerusonaPersonality",
    ProgrameAction.SetAIPerusonaTendency: "SetAIPerusonaTendency",
    ProgrameAction.SetAIPerusonaHubby: "SetAIPerusonaHubby",
    ProgrameAction.SetAIPerusonaBody: "SetAIPerusonaBody",
    ProgrameAction.AIDefineSelfPersonality:"AIDefineSelfPersonality",
    ProgrameAction.AIDefineSelfTendency:"AIDefineSelfTendency",
    ProgrameAction.AIDefineSelfBody:"AIDefineSelfBody",
    ProgrameAction.AIDefineSelfImage:"AIDefineSelfImage",
    ProgrameAction.FinishedCreationAIPerusona: "FinishedCreationAIPerusona",
    ProgrameAction.SendMessageLLM: "SendMessageLLM",
    ProgrameAction.CreateAnswerLLM: "CreateAnswerLLM",
    ProgrameAction.ArrangementOfTalk: "ArrangementOfTalk",
}

def ProgrameEventChecker(event_code:ProgrameAction):
    action_string = EVENT_MAPPING[event_code]
    if action_string:
        print(action_string)