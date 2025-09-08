from ctypes import WinDLL, c_wchar_p, POINTER, Structure, c_int, c_bool

#DLL 로드

class Stack(Structure):
    pass
    
Stack._fields_ = [
        ("txt", c_wchar_p),
        ("node", POINTER(Stack))
    ]
class NativeTools:
    def __init__(self):
        self.dll = WinDLL(r"D:\Project\EMSW(Echo Mind SubWriter)\EMSW_UI\core\NativeTools\libDataTools.dll")
class CharStack(NativeTools):
    # dll을 초기화하고, makeStack 반환형을 지정.
    def __init__(self):
        super().__init__()
        self.dll.makeStack.restype = POINTER(Stack)
        self.stack = self.dll.makeStack()
    # push의 args와 return type을 설정하고, push를 래핑한다.
    def push(self, text:str):
        if text.__len__() != 1:
            raise ValueError('1개의 문자만 입력할 수 있습니다.')
        self.dll.push.argtypes=[POINTER(Stack), c_wchar_p]
        self.dll.push.restype=POINTER(Stack)

        self.stack = self.dll.push(self.stack, c_wchar_p(text))
    # 문장을 스텍에 push하는 것이다.
    def pushSentence(self, text:str):
        if text.__len__() == 1:
            raise ValueError('2개 이상의 문자만 입력할 수 있습니다.')
        self.dll.push.argtypes=[POINTER(Stack), c_wchar_p]
        self.dll.push.restype=POINTER(Stack)
        
        for t in text:
            tmp = c_wchar_p(t)
            self.stack = self.dll.push(self.stack, tmp)
    # Stack에서 Pop 기능을 래핑한다.
    def pop(self):
        self.dll.pop.argtypes = [POINTER(POINTER(Stack))]
        self.dll.pop.restype = c_wchar_p
        return self.dll.pop(self.stack)
    #stack의 데이터를 리버스해서 그대로 또 다른 Stack을 반환함
    def get_reverse(self):
        tmp = []
        for t in self.__iter__():
            tmp.append(t)
        print(tmp)
        stack = CharStack()
        for t in tmp:
            stack.push(t)
        return stack
    # Stack 그 자체를 string으로 반환함.
    def get_String(self):
        self.dll.pop.argtypes = [POINTER(POINTER(Stack))]
        self.dll.pop.restype = c_wchar_p
        text = []
        tmp = ''
        while tmp != 'None':
            tmp = self.pop()
            if tmp != 'None':
                text.append(tmp)
        return ''.join(text)
    # Stack를 뒤집어서 하여 str로 반환한다.
    def get_reverseString(self):
        self.dll.pop.argtypes = [POINTER(POINTER(Stack))]
        self.dll.pop.restype = c_wchar_p
        text = []
        tmp = ''
        while tmp != 'None':
            tmp = self.pop()
            if tmp != 'None':
                text.append(tmp)
        text.reverse()
        return ''.join(text)
    # stack 내의 문서 내용을 반환한다.
    # 단, stack에 노드는 삭제하지 않는다.
    def __str__(self):
        if self.stack == None:
            return None
        txt = [t for t in self.__iter__()]
        return ''.join(txt)
    # stack 내의 문서 내용을 거꾸로 반환한다.
    # 단, stack의 노드는 삭제하지 않는다.
    def __to_reverse_str__(self):
        txt = [t for t in self.__iter__()]
        txt.reverse()
        return ''.join(txt)
    # iter로 반환한다. (pop과는 다름)
    def __iter__(self):
        current = self.stack
        while current:
            if current is None:
                break
            yield current.contents.txt
            current = current.contents.node
    def __get__(self):
        return self.stack
    # stack의 길이를 반환한다.
    def len(self):
        t = [t for t in self.__iter__()]
        return t.__len__()
    # 똑같은 값을 갖는 다른 스택을 반환한다.
    def copy(self):
        self.dll.copy.argtypes = [POINTER(Stack)]
        self.dll.copy.restype = POINTER(Stack)
        self.dll.freeStack.argtypes = [POINTER(Stack)]
        tmp = CharStack()
        self.dll.freeStack(tmp.stack)
        tmp.stack = self.dll.copy(self.stack)
        return tmp
    # 스텍의 메모리를 리스트로 반환한다.
    def list_ptr(self):
       self.dll.getPtr.argtypes = [POINTER(Stack)]
       self.dll.getPtr.restype = POINTER(Stack)
       return [self.dll.getPtr(t) for t in self.__iter__()]
    # 스택의 주소값의 iterator로 만들어준다.
    def __iter_node__(self):
        current = self.stack
        while current:
            yield current
            current = current.contents.node
    # 순차적으로 모든 스택을 지운다. 클래스가 삭제될때 항상 호출된다.
    def __del__(self):
        self.dll.freeStack.argtypes = [POINTER(Stack)]
        for t in self.__iter_node__():
            self.dll.freeStack(t)
    # stack을 콜 하면 stack 구조체 그 자체를 반환한다.
    def __call__(self):
        if self.stack is None:
            raise('NULL Data')
        return self.stack
    # set을 호출하면 stack 구조체를 받아서 스텍 값으로 삽입한다.
    def setStack(self, stack:POINTER(Stack)):
        self.stack = stack
# C Stack 메모리를 받아 string 값만 추출해내는 함수
def stack_str(stack_ptr : POINTER(Stack)):
    tmp_Stack = CharStack()
    tmp_Stack.setStack(stack_ptr)
    return tmp_Stack.__str__()
# List 자료구조의 구조체를 정의한다.
class List(Structure):
    pass
List._fields_ = [
    ('data', POINTER(Stack)),
    ('left', POINTER(List)),
    ('right', POINTER(List)),
    ('pos', c_int)
]
# Char List를 정의한 클래스
class StackList(NativeTools):
    # List의 포인터 변수
    listPtr = POINTER(List)
    # dll을 초기화하고, makeList를 호출하여 리스트를 초기화 한다.
    def __init__(self):
        super()
        self.dll.makeList.restype = POINTER(List)
        self.list = self.dll.makeList()
    # List에 Stack 데이터를 추가한다.
    def append(self, data:CharStack):
        self.dll.appendNode.argtypes = [self.listPtr, POINTER(Stack)]
        self.dll.appendNode.restype = POINTER(List)
        res = self.dll.appendNode(self.list, data.stack)
        if not res:
            raise('Cannot Append Data!')
    # data를 stack으로 치환한다.
    def convertStack(self, stack:POINTER(Stack)):
        tmp = CharStack()
        tmp.setStack(stack)
        return tmp
    # list의 길이를 가져온다.
    def len(self):
        self.dll.len.argtypes = [POINTER(List)]
        self.dll.len.restype = c_int
        return self.dll.len(self.list)
    # 가장 앞의 노드의 데이터를 반환한다. (메모리는 지우지 않는다.)
    def forward(self):
        self.dll.getData.argtypes = [POINTER(List)]
        self.dll.getData.restype = POINTER(Stack)
        if self.list is None:
            raise ('Pointer Error! Not Initialization!')
        return self.convertStack(self.dll.getData(self.list))
    def backward(self):
        self.dll.getData.argtypes = [POINTER(List)]
        self.dll.getData.restype = POINTER(Stack)
        self.dll.rightNone.argtypes = [POINTER(List)]
        self.dll.rightNone.restype = c_bool
        self.dll.getRight.argtypes = [POINTER(List)]
        self.dll.getRight.restype = POINTER(List)
        if self.dll.rightNone(self.list):
            raise ('Pointer Error! NULL Pointer!')
        return self.convertStack(self.dll.getData(self.getRight()))
    def getLeft(self):
        self.dll.leftNone.argtypes = [POINTER(List)]
        self.dll.leftNone.restype = c_bool
        self.dll.getLeft.argtypes = [POINTER(List)]
        self.dll.getLeft.restype = POINTER(List)
        if self.dll.leftNone(self.list) is None:
            raise ('Pointer Error! NULL Pointer!')
        return self.dll.getLeft(self.list)
    def getRight(self):
        self.dll.rightNone.argtypes = [POINTER(List)]
        self.dll.rightNone.restype = c_bool
        self.dll.getRight.argtypes = [POINTER(List)]
        self.dll.getRight.restype = POINTER(List)
        if self.dll.rightNone(self.list):
            raise ('Pointer Error! NULL Pointer!')
        return self.dll.getRight(self.list)
    def appendForward(self, data:CharStack):
        self.dll.appendForward.argtypes = [POINTER(List), POINTER(Stack)]
        self.dll.appendForward.restype = POINTER(List)
        self.dll.rightNone.argtypes = [POINTER(List)]
        self.dll.rightNone.restype = c_bool
        if self.dll.rightNone(self.list):
            raise ('Pointer Error! NULL Pointer!')
        print(type(data.__call__()))
        self.list = self.dll.appendForward(self.list, data.__call__())
    def appendPos(self, data:CharStack, pos:int):
        self.dll.rightNone.argtypes = [POINTER(List)]
        self.dll.rightNone.restype = c_bool
        self.dll.posCheck.argtypes = [POINTER(List), c_int]
        self.dll.posCheck.restype = c_bool
        self.dll.getLeft.argtypes = [POINTER(List)]
        self.dll.getLeft.restype = POINTER(List)
        self.dll.getRight.argtypes = [POINTER(List)]
        self.dll.getRight.restype = POINTER(List)
        self.dll.appendLeft.argtypes = [POINTER(List), POINTER(Stack), c_int]
        self.dll.appendLeft.restype = POINTER(c_int)
        self.dll.appendRight.argtypes = [POINTER(List), POINTER(Stack), c_int]
        self.dll.appendRight.restype = POINTER(c_int)
        if (self.len() < pos):
            raise ('Value Error! Pos Over the Length')
        elif (pos < 1):
            raise ('valueError! Pos Can natural number')
        check = 0
        if (pos == 1):
            check = self.appendForward(data)
        elif ((self.len() / 2)+1 < pos):
            check = self.dll.appendRight(self.dll.getRight(self.list), data.__call__(), pos)
        elif (pos < (self.len() / 2) + 1):
            check = self.dll.appendLeft(self.dll.getLeft(self.list), data.__call__(), pos)
        if check == 0:
            raise ('Unknown Error!')
        elif check == -1:
            raise ('left is NULL! NULL Exception!')
        elif check == -2:
            raise ('next left node NULL! NULL Exception')
        elif check == -3:
            raise ('data is NULL! NULL Exception')
    def makeList(self, list:POINTER(List)):
        tmp = StackList()
        tmp.list = list
        return tmp
    def atPos(self, pos:int):
        self.dll.getLeft.argtypes = [POINTER(List)]
        self.dll.getLeft.restype = POINTER(List)
        self.dll.getRight.argtypes = [POINTER(List)]
        self.dll.getRight.restype = POINTER(List)
        self.dll.getData.argtypes = [POINTER(List)]
        self.dll.getData.restype = POINTER(Stack)
        self.dll.findDataFromPosition.argtypes = [POINTER(List), POINTER(List), c_int]
        self.dll.findDataFromPosition.restype = POINTER(Stack)
        if self.len() < pos:
            raise ('Error! over range exception!')
        elif self.len() < 1:
            raise ('Error! must able to natural numbers')
        if pos == 1:
            return stack_str(self.dll.getData(self.list))
        else:
            print(type(self.dll.findDataFromPosition(self.dll.getLeft(self.list), self.dll.getRight(self.list), pos)))
            return stack_str(self.dll.findDataFromPosition(self.dll.getLeft(self.list), self.dll.getRight(self.list), pos))
    #최초의 data의 위치를 반홚함
    def atData(self, data:CharStack):
        self.dll.findPositionFromData.argtypes = [POINTER(List), POINTER(List), POINTER(Stack)]
        self.dll.findPositionFromData.restype = c_int
        self.dll.getRight.argtypes = [POINTER(List)]
        self.dll.getRight.restype = POINTER(List)
        current = self.dll.findPositionFromData(self.list, self.dll.getRight(self.list), data.stack)
        return current
    def __iter_pos__(self):
        self.dll.getLeft.argtypes = [POINTER(List)]
        self.dll.getLeft.restype = POINTER(List)
        self.dll.leftNone.argtypes = [POINTER(List)]
        self.dll.leftNone.restype = c_bool
        current = self.list
        while True:
            yield self.dll.pos(current)
            if self.dll.leftNone(current):
                break
            current = self.dll.getLeft(current)
            if not current:
                break
    def __iter__(self):
        self.dll.getLeft.argtypes = [POINTER(List)]
        self.dll.getLeft.restype = POINTER(List)
        self.dll.getData.argtypes = [POINTER(List)]
        self.dll.getData.restype = POINTER(Stack)
        self.dll.leftNone.argtypes = [POINTER(List)]
        self.dll.leftNone.restype = c_bool
        self.dll.rightNone.argtypes = [POINTER(List)]
        self.dll.rightNone.restype = c_bool
        self.dll.pos.argtypes = [POINTER(List)]
        self.dll.pos.restype = c_int
        current = self.list
        while current:
            if not current:
                break
            yield self.convertStack(self.dll.getData(current))
            if self.dll.leftNone(current):
                break
            elif self.dll.rightNone(current):
                break
            current = self.getLeft(current)
            if self.dll.pos(current) == 1:
                break
    def __del__(self):
        self.dll.freeList.argtype = [POINTER(List)]
        self.dll.freeList(self.list)
class D_Queue(Structure):
    pass
D_Queue._fields_ = [
    ('data', POINTER(Stack)),
    ('back', POINTER(D_Queue))
]
#Data Queue는 각 데이터를 Stack으로 관리할 수 있는 데이터 구조이다.
class DataQueue(NativeTools):
    def __init__(self):
        super().__init__()
        self.dll.makeDataQueue.restype = POINTER(D_Queue)
        self.dqueue = self.dll.makeDataQueue()
    def insert(self, stack):
        self.dll.insertDataQueue.argtypes = [POINTER(D_Queue), POINTER(Stack)]
        self.dll.insertDataQueue.restype = POINTER(D_Queue)
        if not isinstance(stack, POINTER(Stack)):
            return -1
        self.dqueue = self.dll.insertDataQueue(self.dqueue, stack)
        return 0
    def __iter__(self):
        current = self.dqueue
        while current:
            if current is None:
                break
            yield current.contents.data
            current = current.contents.back