# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class TextPage(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.icon_folder = Path(sys.argv[0]).parent/'Icons'
        self.initUI()

    def initUI(self):
        self.setup_layouts()
        self.setup_connections()

    def setup_layouts(self):
        self.main_layout = QVBoxLayout(self)

        self.setup_edit()

        self.setup_text_area()


    def setup_edit(self):
        layout = QHBoxLayout()
        self.main_layout.addLayout(layout)

        self.lb1 = QLabel('正则表达式：')
        self.lnedt = FLineEdit(r'\W\d+\W')
        layout.addWidget(self.lb1)
        layout.addWidget(self.lnedt)

    def setup_text_area(self):
        self.text_layout = QHBoxLayout()
        self.main_layout.addLayout(self.text_layout)

        self.org_text_edit = QTextEdit()
        self.org_text_edit.setStyleSheet('background-color:#456')

        self.edited_text_edit = QTextEdit()
        self.edited_text_edit.setStyleSheet('background-color:#456')

        self.text_layout.addWidget(self.org_text_edit)
        self.text_layout.addWidget(self.edited_text_edit)

    def setup_connections(self):
        pass