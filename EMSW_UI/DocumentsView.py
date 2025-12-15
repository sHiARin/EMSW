from EMSW_UI import *


class DocumentView(QWidget):
    # 열린 문서를 관리하는 뷰
    def __init__(self, parent, project:ProjectConfig):
        super().__init__(parent=parent)
        self.parents = parent
        self.project = project
        self._names = None
        self._selected_name = None
        self.treeView = QTreeView()
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Documents"])
        self.treeView.setModel(self.model)
        self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeView.clicked.connect(self._on_tree_clicked)

        self.read_files()
        self.__init_ui__()
    # 파일을 읽는 메소드
    def read_files(self):
        try:
            self._names = self.project.get_documents_name()
        except:
            pass
    def set_names(self, names:list):
        self._names = names
        self.make_trees()
    def names(self):
        return self._names
    def name(self):
        return self._selected_name[0]
    def title_pos(self):
        return self._selected_name[1]
    # tree를 만드는 메서드
    def make_trees(self):
        # 중복 방지
        self.model.removeRows(0, self.model.rowCount())
        for n in self.names():
            if 'sample' != n:
                pass
            item = self.make_group_tree(n)
            self.model.appendRow(item)
        if self.model.columnCount() == 0:
            self.model.setRow(0, '없음')
    # tree clicked action
    def _on_tree_clicked(self, index):
        try:
            data = index.parent().data()
            pos = index.column() + 1
            if data is None:
                print('None')
            else:
                text = self.project.get_document_text(data, index.column() + 1)
                self.textWidget.setText(text)
                title = self.project.get_document_title(data, pos)
                GlobalWorld().add_documents(title, text)
                self.project.open_document_file_name = title
        except Exception as e:
            print(f"error : {type(e)}")
            pass
    # 그룹 하위의 문서를 등록하는 매서드
    def make_group_tree(self, name:str):
        item = QStandardItem(name)
        for i, k in enumerate(self.project.get_documents_title(name)):
            if i == 0:
                pass
            else:
                print(name, i)
                t = QStandardItem(self.project.get_document_title(name, i))
                item.appendRow(t)
        return item
    # 편집된 텍스트를 저장
    def saveText(self):
        if self._selected_name is not None:
            self.project.update_document_text(self._selected_name[0], self._selected_name[1], self.textWidget.toPlainText())
    # 삭제 작업 시 treeView에 접근하여 값을 갱신
    def delete_item(self):
        self.make_trees()
    def __init_ui__(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Horizontal)

        # === 왼쪽 : group List ===
        self.make_trees()
        splitter.addWidget(self.treeView)

        # === 오른쪽 : text View ===
        self.textWidget = QTextEdit(self)
        self.textWidget.setReadOnly(True)

        splitter.addWidget(self.textWidget)
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)