# -*- coding: utf-8 -*-

from ..qt_core import *


class FMessageBox(QMessageBox):
    def __init__(self):
        QMessageBox.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
