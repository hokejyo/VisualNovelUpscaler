# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class InfoPage(QTreeWidget):

    def __init__(self):

        QTreeWidget.__init__(self)
        self.setup_layouts()

    def setup_layouts(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setup_licenses()

    def setup_licenses(self):
        layout = QVBoxLayout()
        self.layout.addLayout(layout)

        license_lb = QLabel('License')
        layout.addWidget(license_lb)
        license_msg = QTextEdit()
        license_msg.setReadOnly(True)
        with open(Path(sys.argv[0]).parent/'LICENSE', 'r', newline='', encoding='utf-8') as f:
            license_text = f.read()
        license_msg.setText(license_text)
        layout.addWidget(license_msg)
