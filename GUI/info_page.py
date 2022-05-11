# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class InfoPage(QFrame):

    def __init__(self):

        QFrame.__init__(self)
        self.setup_layouts()

    def setup_layouts(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.tab_view = FTabWidget(height=80, position='bottom')
        self.layout.addWidget(self.tab_view)
        self.setup_help_info()
        self.setup_licenses()
        self.setup_update_bug()

    def setup_help_info(self):
        self.help_info_frame = QFrame()
        self.tab_view.addTab(self.help_info_frame, '教程&&帮助')

    def setup_licenses(self):
        license_msg = QTextEdit()
        license_msg.setReadOnly(True)
        self.tab_view.addTab(license_msg, 'License')

        with open(Path(sys.argv[0]).parent/'LICENSE', 'r', newline='', encoding='utf-8') as f:
            license_text = f.read()
            license_msg.setPlainText(license_text)
        # license_msg.append(license_text)
        # license_msg.moveCursor(QTextCursor.Start)

    def setup_update_bug(self):
        self.update_bug_frame = QFrame()
        self.tab_view.addTab(self.update_bug_frame, '更新&&反馈')

        layout = QVBoxLayout(self.update_bug_frame)
        self.check_update_btn = FIconButton('检查更新')
        layout.addWidget(self.check_update_btn)
