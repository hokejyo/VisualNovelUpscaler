# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class ImagePage(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.initUI()

    def initUI(self):
        self.setup_layouts()
        self.setup_connections()

    def setup_connections(self):
        pass

    def setup_layouts(self):
        self.layout = QVBoxLayout(self)

        self.setup_in_out_folders()

        self.setup_center_layout()

        # self.setup_input_list()

    def setup_in_out_folders(self):
        layout = QHBoxLayout()
        self.input_lb = QLabel('输入图片：')
        self.input_line_edit = FLineEdit(place_holder_text='将图片文件或文件夹拖拽至此处', height=30, radius=12, text_padding=10)
        layout.addWidget(self.input_lb)
        layout.addWidget(self.input_line_edit)
        self.layout.addLayout(layout)

    def add_shadow(self, target_widget):
        shadow = QGraphicsDropShadowEffect(target_widget)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 200))
        target_widget.setGraphicsEffect(shadow)

    def setup_center_layout(self):
        self.center_frame = QFrame()
        self.add_shadow(self.center_frame)
        self.layout.addWidget(self.center_frame)
        self.center_layout = QHBoxLayout(self.center_frame)

        self.filters_lb = QLabel('文件筛选')
        self.center_layout.addWidget(self.filters_lb)

        self.setup_circular_progress()

        self.start_btn = FPushButton('开始')
        # self.add_shadow(self.start_btn)
        self.center_layout.addWidget(self.start_btn)

    def setup_circular_progress(self):
        self.circular_progress = FCircularProgress()
        self.center_layout.addWidget(self.circular_progress)
        self.circular_progress.set_value(10)
        # self.circular_progress.add_shadow()

        # layout = QHBoxLayout(self.circular_progress)
        # layout.addWidget(QLabel('测试'))

    def setup_input_list(self):
        layout = QHBoxLayout()
        self.layout.addLayout(layout)

        self.input_list = QTextEdit()
        layout.addWidget(self.input_list)
