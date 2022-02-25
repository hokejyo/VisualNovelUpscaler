# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *
from functools import partial


class InfoPage(QFrame):

    def __init__(self):

        QFrame.__init__(self)
        self.setup_page_btns(10)

    def setup_page_btns(self, page_nums):
        self.layout = QHBoxLayout(self)
        self.get_page_btns_dict(page_nums)
        self.setup_page_btns_connections()

    def get_page_btns_dict(self, page_nums):
        self.page_dict = {}
        for i in range(page_nums):
            page_num = i+1
            self.page_dict[QPushButton(f'第{page_num}页')] = page_num

    def setup_page_btns_connections(self):
        for btn, page_num in self.page_dict.items():
            self.layout.addWidget(btn)
            # print(btn, page_num)
            btn.clicked.connect(partial(self.switch_page, page_num))

    def switch_page(self, page_num):
        print(page_num)
