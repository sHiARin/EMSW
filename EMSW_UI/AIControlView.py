from EMSW_UI import *

class PersonaSettingWindow(QWidget):
    """ persona의 세부 사항을 설정하고 편집하는 동작을 담당하는 위젯"""
    def __init__(self, parent, project):
        super().__init__()
        self.edit_cell = False
        self.edit_list = []
        self.clickedNum = 0
        self.project = project
        self.parents = parent
        
        # 테이블 키 설정
        self.persona_keys = ['name', 'age', 'sex', 'hobby', 'personality', 'tendency', 'body', 'self_body', 'self_personality', 'self_tendency', 'self_image']

        # 윈도우 초기 설정
        window_data = self.project.getPersonaEditing_WindowData()
        self.move(window_data.get('x', 100), window_data.get('y', 100))
        self.resize(window_data.get('w', 800), window_data.get('h', 600))
        self.setWindowTitle("캐릭터 관리")
        self.setStyleSheet("background: #F0F2F5")

        # UI 및 데이터 로드
        self.init_ui()
        self.load_table_data()

    def init_ui(self):
        """UI 레이아웃 및 스타일 설정"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. 상단 헤더 영역 (제목 + 검색 + 버튼)
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel("캐릭터 목록")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; border: none;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("이름으로 검색...")
        self.search_input.setStyleSheet("""
            QLineEdit { border: 1px solid #CCC; border-radius: 5px; padding: 5px 10px; background-color: #FAFAFA; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #ABC1D1; }
        """)
        self.search_input.textChanged.connect(self.filter_table) # 검색 기능 연결

        search_btn = QPushButton("검색")
        search_btn.setFixedSize(60, 30)
        self._apply_btn_style(search_btn, "#ABC1D1", "white")
        search_btn.clicked.connect(lambda: self.filter_table(self.search_input.text()))

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setFixedSize(80, 30)
        self._apply_btn_style(refresh_btn, "#FEE500", "#333")
        refresh_btn.clicked.connect(self.load_table_data)

        self.edit_btn = QPushButton("편집")
        self.edit_btn.setFixedSize(60, 30)
        self._apply_btn_style(self.edit_btn, "#00E0F0", "#333")
        self.edit_btn.clicked.connect(self.edit_button)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(search_btn)
        top_layout.addWidget(self.edit_btn)
        top_layout.addWidget(refresh_btn)
        main_layout.addWidget(top_frame)

        # 2. 테이블 위젯 설정
        self.columns = ['이름', '나이', '성별', '취미', '성격', '성향', '외모', '설정']
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        
        # 테이블 옵션
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        # 테이블 스타일
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #DDD; border-radius: 10px; gridline-color: #EEE; font-size: 12px; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F0F0; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #000; }
            QHeaderView::section { background-color: #ABC1D1; color: white; padding: 8px; border: none; font-weight: bold; font-size: 13px; }
        """)
        
        main_layout.addWidget(self.table)

        # 3. 하단 상태바
        status_layout = QHBoxLayout()
        self.count_label = QLabel("총 0개의 항목")
        self.count_label.setStyleSheet("color: #666; font-size: 12px;")
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedSize(80, 30)
        close_btn.setStyleSheet("background-color: #EEE; border-radius: 5px;")
        close_btn.clicked.connect(self.close)

        status_layout.addWidget(self.count_label)
        status_layout.addStretch()
        status_layout.addWidget(close_btn)
        main_layout.addLayout(status_layout)

    def edit_button(self):
        self.edit_cell = not self.edit_cell
        if self.edit_cell:
            self.edit_btn.setText('저장')
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)
            self.table.itemClicked.connect(self._handle_dobule_clicked_)
        else:
            self.edit_btn.setText('편집')
            # 편집 모드 종료
            # 트리거 연결 해제, 오류 우회를 위한 except pass
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            try:
                self.table.itemClicked.disconnect(self._handle_clicked_)
            except:
                pass
            for item in self.edit_list:
                name = self.table.item(item.row(), 0).text()
                content = item.text()
                if item.column() == 0:
                    pass
                elif item.column() < 3:
                    self.project._update_persona_field(name, self.persona_keys[item.column()], content)
                    self.project.save_project()
                else:
                    content, type_str = self.parents._parse_input_string(content)
                    self.project._update_persona_field(name, self.persona_keys[item.column()], content, type_str)
                    self.project.save_project()

    def _handle_dobule_clicked_(self, item):
        self.clickedNum += 1
        self.edit_list.append(item)
        is_save_mode = (self.edit_btn.text() == '저장')
        if not is_save_mode:
            self.table.setItem(item.row(), item.column(), item)
            self.clickedNum = 0

    def load_table_data(self):
        """데이터를 불러와 테이블을 채웁니다."""
        self.table.setRowCount(0) # 초기화
        persona_dict = self.project.get_persona_dict()
        
        for name, data in persona_dict.items():
            if name == 'sample':
                continue
            
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # 데이터 포맷팅 및 셀 생성
            # 컬럼 순서: 이름, 나이, 성별, 취미, 성격, 성향, 외모
            cell_values = [
                name,
                str(data.get('age', '')),
                str(data.get('sex', '')),
                self._format_value(data.get('hobby'), '취미가 없습니다.'),
                self._format_value(data.get('personality')),
                self._format_value(data.get('tendency')),
                self._format_value(data.get('body'))
            ]

            # 텍스트 셀 추가
            for col_idx, value in enumerate(cell_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setSelected(False)
                self.table.setItem(row_idx, col_idx, item)

            # 마지막 컬럼: 설정 버튼
            btn = self._create_setup_button(name)
            self.table.setCellWidget(row_idx, len(self.columns)-1, btn)

        # 데이터 로드 후 레이아웃 조정
        self.count_label.setText(f"총 {self.table.rowCount()}개의 항목")
        self._adjust_column_sizes()

    def _format_value(self, value, default_msg=""):
        """데이터 타입(str, list, dict)에 따라 적절한 문자열로 변환합니다."""
        if value is None:
            return default_msg
        
        if isinstance(value, list):
            return '\n'.join([str(t) for t in value])
        elif isinstance(value, dict):
            return '\n'.join([f"{k} : {v}" for k, v in value.items()])
        
        # 문자열이거나 기타 타입
        return str(value)

    def _create_setup_button(self, name):
        """설정 버튼 생성"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button = QPushButton('설정')
        button.setFixedSize(60, 24)
        button.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        button.clicked.connect(lambda: self._open_ego_setup(name))
        
        layout.addWidget(button)
        return container

    def _open_ego_setup(self, name):
        """EgoSetup 창 열기"""
        self.egosetup = EgoSettup(self.project, name)
        # self.egosetup.show() # EgoSettup 내부에서 show()를 호출하지 않는다면 여기서 호출

    def _adjust_column_sizes(self):
        """테이블의 행/열 크기를 내용에 맞게 조정합니다."""
    
        # 열 너비(Width)를 내용에 맞게 자동 조정
        self.table.resizeColumnsToContents()
    
        # 행 높이(Height)를 내용(개행 포함)에 맞게 자동 조정
        self.table.resizeRowsToContents()

        # 행 높이를 내용에 맞게 '고정' (사용자가 마우스로 조절 불가능하게)
        # 내용이 바뀌면 자동으로 늘어나고 줄어듦
        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 특정 항목은 최대 길이를 막어 무한정 불어나는 것을 막습니다.
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 300)

        # 마지막 항목은 btn의 너비(60) 보다 여유있게 설정하여 잘리는 것을 방지하고, Table의 길이를 수정할 수 없도록 변경.
        self.table.setColumnWidth(len(self.columns) - 1, 80)
        self.table.EditTrigger(QAbstractItemView.EditTrigger.NoEditTriggers)

    def filter_table(self, text):
        """검색어에 따라 테이블 행 숨기기/보이기"""
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0) # 0번 컬럼이 이름
            if name_item:
                is_match = text.lower() in name_item.text().lower()
                self.table.setRowHidden(row, not is_match)

    def _apply_btn_style(self, btn, bg_color, text_color):
        """버튼 스타일 적용 헬퍼"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                font-weight: bold; border: none; border-radius: 5px;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
    def closeEvent(self, event):
        self.project.set_Persona_editing_windows_geometry(self.x(), self.y(), self.width(), self.height())
        return super().closeEvent(event)
