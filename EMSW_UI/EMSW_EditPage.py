from PySide6.QtWidgets import (QMainWindow, QMenuBar, QWidget,
                               QTreeView, QHBoxLayout, QVBoxLayout,
                               QInputDialog, QMessageBox, QSplitter,
                               QAbstractItemView, QGraphicsScene, QGraphicsView,
                               QStatusBar)
from PySide6.QtCore import (Signal, QTimer, Qt, QModelIndex)
from PySide6.QtGui import (QAction, QStandardItemModel, QStandardItem,
                           QPalette, QColor, QFont,
                           QPen, QBrush, QPainter)
from Config.config import WikiDocuments, ProgrameAction, ProgrameEventChecker

import os

class WikiIndex(QWidget):
    Action_Type = Signal(ProgrameAction)
    def __init__(self, title:str, config:WikiDocuments):
        super().__init__()
        self.config = config
        self.title = title
        self.model = QStandardItemModel()
        self.CreateWindows()
        self.__init_ui__()
    def CreateWindows(self):
        self.IndexView = QTreeView()
        self.makeIndex()
    # 목차를 만듭니다.
    def makeIndex(self):
        if self.model is not None:
            self.model.clear() # 기존 모델 초기화
            parents = QStandardItem(self.title)
            for t in self.config.getKeys('index'):
                children = QStandardItem(t)
                parents.appendRow(children)
            self.model.appendRow(parents)
            self.IndexView.setModel(self.model)
            self.IndexView.expandAll()
            self.IndexView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    # 목차에 새 항목을 추가하고 모델을 재생성합니다.
    def addIndex(self, new:str):
        if new not in self.config.getKeys('index'):
            self.config.AppendIndex(new)
            self.resetIndex()
            self.makeIndex()
        else:
            self.resetIndex()
            self.makeIndex()
        print('addIndex')
    # 모델을 초기화 합니다.
    def resetIndex(self):
        if self.model:
            self.model.clear()
    def __init_ui__(self):
        vLayout = QVBoxLayout()
        layout = QHBoxLayout()
        if type(self.IndexView) is QTreeView:
            self.IndexView.setHeaderHidden(True)
            vLayout.addWidget(self.IndexView)

        layout.addLayout(vLayout)
        
        self.setLayout(layout)

"""
    이 클래스는 QGraphics View를 사용하여 DSL을 랜더링하는 콘탠츠 뷰 위젯이다.
    데이터는 모두 DocumentsData에서 실시간 관리되며, 창을 닫을 때, DocumentsData에서
    DocumentView로, 다시 DocumentsView에서 Config의 WikiDocuments로 전달되어 저장된다.
    또한, 실시간으로 저장되는 시간을 정할 수 있으며, 저장이 되어있지 않은 경우 닫으려고 할 때 저장하시겠습니까?
    메시지를 띄운다.
"""
class DocumentView(QWidget):
    keyboardSignal = Signal(str)
    Action_Type = Signal(ProgrameAction)
    DEFAULTS = {
        'box' : {
            'x' : 10, 'y' : 10, 'w' : 280, 'h' : 480,
            'bg_color': '#FFFFFF',
            'pen_color' : '#AAAAAA', #엷은 회색 태두리
            'font_size': 10, 'font_wight': 'normal', 'font_family':'Arial'
        },
        'note' : {
            'x' : 10, 'y' : 10, 'w' : 280, 'h' : 50,
            'bg_color': '#E1FFE1', # Note 기본색
            'pen': QPen(QColor("#008800"), 1, Qt.PenStyle.DashLine), # 초록색 점선
            'font_size': 10, 'font_weight': 'normal', 'font_family': 'Arial'
        }
    }
    def __init__(self, title:str, config:WikiDocuments):
        super().__init__()
        print('wiki documents view')
        self.config = config
        self.editPage = None
        self.index = title
        self.TBoard = None
        self.__start__()
        self.__init_ui__()
    # 키보드의 이벤트를 감지하는 이벤트 함수
    def keyPressEvent(self, event):
        self.keyboardSignal.emit(event.key())
        self.Action_Type.emit(ProgrameAction.PressKeyboardEvent)
        print(event.key())
        return super().keyPressEvent(event)
    def __init_ui__(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.view)
        self.setLayout(layout)
    def __start__(self):
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackGroundColor()
    
    def setBackGroundColor(self):
        """
            이 뷰의 배경색을 설정하는 메소드입니다.

            :Documents_View_Color의 값으로 저장되어 있으며, 일반적으로 16진수 RGB 값으로 저장되어 있습니다.
        """
        try:
            color = QColor(self.config.getKeys('Document_View_Color'))
            if not color.isValid():
                QMessageBox.information(self, "경고", f"잘못된 색상 코드({self.config.getKeys('Document_View_Color')}. 기본 색인 흰색으로 설정합니다.)", QMessageBox.StandardButton.Ok)
                color = QColor("#ffffff")
            self.scene.setBackgroundBrush(QBrush(color))
            self.view.setStyleSheet(f"background-color: {self.config.getKeys('Document_View_Color')}; border: none;")
            
        except Exception as e:
            QMessageBox.information(self, "오류", f"배경색 설정 오류 : {e}", QMessageBox.StandardButton.Ok)
            self.scene.setBackgroundBrush(QBrush(QColor("#ffffff")))
    def append_Text(self, key:str, value:str):
        print('append text')
    def update_Text(self):
        pass
    def setBody(self, index:str):
        if index in self.config.bodys().keys():
            self.editPage = index
        else:
            self.editPage = None
class WikiView(QMainWindow):
    Action_Type = Signal(ProgrameAction)
    Close_Title = Signal(str)
    def __init__(self, dir:str, name : str):
        super().__init__()
        self.Focused = False
        self.dir = dir
        self.title = name
        self.IndexView = None
        self.MainView = None
        self.config = None
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.documentRatio = 50
        self.bodies = None
        self.__start__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__update__)
        self.timer.start(16)

        self.init_UI()
    def __start__(self):
        self.setWindowTitle(self.title)
        self.Load_Data()
        self.IndexView = WikiIndex(self.title, self.config)
        self.MainView = DocumentView(self.title, self.config)
        self.programeSignal = ProgrameAction.SubWindowsOpened
        self.setWindowTitle(self.title)

        self.makeMenu()
        statusBar = QStatusBar()
        statusBar.showMessage('편집창이 열렸습니다.', 5000)
        self.setStatusBar(statusBar)
    #포커스가 이 페이지에 들어올 때 사용하는 이벤트
    def focusInEvent(self, event):
        self.Focused = True
        return super().focusInEvent(event)
    #포커스가 이 페이지에서 나갈때 사용하는 이벤트
    def focusOutEvent(self, event):
        self.Focused = False
        return super().focusOutEvent(event)
    #data를 로드하는 메소드
    def Load_Data(self):
        print(self.dir)
        if self.config is None and os.path.exists(self.dir):
            self.config = WikiDocuments(self.dir)
        if len(self.config.DocumentRatio()) == 0:
            self.config.documentRatio(self.documentRatio)
        elif len(self.config.DocumentRatio()) == 1:
            self.config.documentRatio(self.documentRatio)
        else:
            self.documentRatio = self.config.DocumentRatios()
        if self.bodies is None:
            self.bodies = [self.config.parse_context(self.config.Body(index)) for index in self.config.indexs()]
        print([t for t in self.bodies])
        self.setGeometry(self.config.X(), self.config.Y(), self.config.Width(), self.config.Height())
        print('Load Data')
    def WindowScaleCheck(self):
        if self.config.X() != self.x():
            self.config.x(self.x())
        if self.config.Y() != self.y():
            self.config.y(self.y())
        if self.config.Width() != self.width():
            self.config.width(self.width())
        if self.config.Height() != self.height():
            self.config.height(self.height())
    def Action_Progress(self):
        if self.programeSignal is ProgrameAction.UpdateWikiTreeView:
            self.Signal_Update(ProgrameAction.UpdateWikiView)
            self.update_Bodies()
        elif self.programeSignal is ProgrameAction.UpdateWikiData:
            self.IndexView.repaint()
            self.Signal_Update(ProgrameAction.UpdateWikiView)
            print('Action Progress Update Wiki Data')
        if self.programeSignal is ProgrameAction.SubWindowsDuring:
            print(1)
    # EditView에서 입력이 발생했는지 하지 않았는지 체크하는 메소드
    def check_EditView_Action(self):
        self.MainView.Action_Type.connect(self.Signal_Update)
    def __fixed_update__(self):
        d = self.splitter.sizes()
        self.config.documentRatios(d[0], d[1])
        self.Action_Progress()
    def Update_Action_Progress(self):
        if self.programeSignal is ProgrameAction.UpdateWikiView:
            self.Signal_Update(ProgrameAction.SubWindowsDuring)
            print('Update Action Progress update wiki view')
        if self.programeSignal is ProgrameAction.PressKeyboardEvent:
            print(1)
            statusBar = QStatusBar()
            statusBar.showMessage('keyboard signal')
            self.setStatusBar(statusBar, 1000)
            self.Signal_Update(ProgrameAction.SubWindowsDuring)
    def __update__(self):
        self.__fixed_update__()
        self.Update_Action_Progress()
        self.__last_update__()
    def __last_update__(self):
        self.WindowScaleCheck()
        self.Signal_Check()
    def update_Bodies(self):
        self.bodies = [self.config.Body(index) for index in self.config.indexs()]
    def Signal_Check(self):
        if self.programeSignal is ProgrameAction.AppendIndex:
            self.Signal_Update(ProgrameAction.UpdateWikiData)
            print('Signal check Append Index')
    def makeMenu(self):
        Menu = self.menuBar()
        self.editMenuBar(Menu.addMenu('Edit'))
        print('make Menu')
    # edit Menu를 추가하는 메소드
    def editMenuBar(self, menu:QMenuBar):
        addIndex = QAction('목차 추가', self)
        addIndex.triggered.connect(self.AppendIndex)
        menu.addAction(addIndex)
        print('edit menu bar')
    # index를 추가하는 메소드
    def AppendIndex(self):
        text, ok = QInputDialog.getText(self, '새 목차', '새 목차를 입력해 주세요')
        if ok:
            l = True
            for t in self.data['index']:
                if t == text:
                    l = False
            if l:
                self.data['index'].append(text)
                self.update_index()
                self.IndexView.addIndex(text)
                self.Signal_Update(ProgrameAction.AppendIndex)
                QMessageBox.information(self, '확인', '목차가 추가되었습니다.', QMessageBox.StandardButton.Ok)
        elif text in self.data['index']:
            QMessageBox.information(self, '경고', '목차 이름이 중복입니다.', QMessageBox.StandardButton.Ok)
            print('not append index')
        else:
            QMessageBox.information(self, '경고', '알 수 없는 오류가 발생했습니다.', QMessageBox.StandardButton.Ok)
            print('programe wrong')
    # Prgraome Signal을 체인지하고, Program Action의 값을 emit하는 메소드
    def Signal_Update(self, signal:ProgrameAction):
        ProgrameEventChecker(signal.value)
        self.programeSignal = signal
        self.Action_Type.emit(signal)
        print('signal update')
    def init_UI(self):
        if self.IndexView is None and self.MainView is None:
            QMessageBox.critical(self, '오류', 'UI 위젯 초기화 실패')
            self.Signal_Update(ProgrameAction.UpdateWikiTreeView)
            return
        
        self.splitter.addWidget(self.IndexView)
        self.splitter.addWidget(self.MainView)

        self.splitter.setSizes(self.documentRatio)
        
        self.setCentralWidget(self.splitter)
        self.IndexView.IndexView.clicked.connect(self.on_index_clicked)
        self.show()
    def on_index_clicked(self, index:QModelIndex):
        item = self.IndexView.model.itemFromIndex(index)
        if item and item.parent(): 
            page_title = item.text()
            statusBar = QStatusBar()
            statusBar.showMessage(f"Clicked page: {page_title}", 5000)
            self.setStatusBar(statusBar)
            self.MainView.setBody(page_title)
        self.Action_Type.emit(ProgrameAction.UpdateTreeView)
    def focusOutEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        return super().focusOutEvent(event)
    def closeEvent(self, event):
        self.WindowScaleCheck()
        print(self.config.DocumentRatios())
        self.timer.stop()
        self.Action_Type.emit(ProgrameAction.SubWindowsClosed)
        self.Close_Title.emit(self.title)
        del self.config