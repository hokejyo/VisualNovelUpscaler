# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class TextPage(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.icon_folder = Path(sys.argv[0]).parent/'Icons'
        self.initUI()
        self.set_file_root_path('./')

    def initUI(self):
        self.setup_layouts()
        self.setup_connections()

    def setup_connections(self):
        self.text_tree_view.selectionModel().currentChanged.connect(self.show_text)
        # self.text_tree_view.clicked.connect(self.show_text)
        self.text_tree_view.doubleClicked.connect(self.changed_root_dir)

    def setup_layouts(self):
        self.main_layout = QVBoxLayout(self)

        self.setup_edit()

        self.setup_text_area()

    def setup_edit(self):
        layout = QHBoxLayout()
        self.main_layout.addLayout(layout)

        self.lb1 = QLabel('正则表达式：')
        kwds_ = '|'.join(['width', 'height', 'left', 'top'])
        self.lnedt = FLineEdit(rf'(?<=(\W|^)({kwds_})\W+((int|float|double)\W+)?)(\d+)(?=\W|$)')
        layout.addWidget(self.lb1)
        layout.addWidget(self.lnedt)

    def setup_text_area(self):
        self.text_layout = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.text_layout)

        self.setup_text_tree_view()

        self.org_text_edit = QTextEdit()
        self.org_text_edit.setStyleSheet('background-color:#456')

        self.edited_text_edit = QTextEdit()
        self.edited_text_edit.setStyleSheet('background-color:#456')

        self.text_layout.addWidget(self.org_text_edit)
        self.text_layout.addWidget(self.edited_text_edit)

    def setup_text_tree_view(self):
        self.text_tree_view = QTreeView()
        self.text_layout.addWidget(self.text_tree_view)

        self.file_model = QFileSystemModel()
        self.text_tree_view.setModel(self.file_model)
        for i in range(1, self.file_model.columnCount()):
            self.text_tree_view.hideColumn(i)
        self.text_tree_view.setSortingEnabled(False)
        # self.text_tree_view.setStyleSheet('background-color:#456')

    def set_file_root_path(self, root_path):
        self.file_model.setRootPath(root_path)
        self.text_tree_view.setRootIndex(self.file_model.index(root_path))

    def show_text(self, current):
        file_path = Path(self.text_tree_view.model().filePath(current))
        if file_path.exists() and file_path.is_file():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.org_text_edit.setPlainText(content)
            except:
                self.org_text_edit.setPlainText('无法打开此文件')

    def changed_root_dir(self, current):
        file_path = Path(self.text_tree_view.model().filePath(current))
        print(file_path)
        if file_path.exists() and file_path.is_dir():
            self.set_file_root_path(str(file_path))
