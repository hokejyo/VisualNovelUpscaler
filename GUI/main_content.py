# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class MainContent(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.icon_folder = Path('./').resolve()/'Icons'
        self.theme = {'MainContent_background': '#282a36', 'MainContent_font': '#6272a4', 'MainContent_bar': '#21232d', }
        self.setStyleSheet(f"background-color: {self.theme['MainContent_background']};color: {self.theme['MainContent_font']}")
        self.setup_layouts()
        self.setup_connections()

    def setup_connections(self):
        pass

    def setup_layouts(self):
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        # 顶部标题栏
        self.setup_top_bar()
        # 内容页
        self.setup_pages()
        # 底部状态栏
        self.setup_bottom_bar()
        # 添加组件进布局
        self.content_layout.addWidget(self.top_bar)
        self.content_layout.addWidget(self.pages)
        self.content_layout.addWidget(self.bottom_bar)

    def setup_top_bar(self):
        # 顶部标题栏
        self.top_bar = QFrame()
        # 设置高度、背景颜色
        self.top_bar.setMinimumHeight(40)
        self.top_bar.setMaximumHeight(40)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        # 左边距为10
        self.top_bar_layout.setContentsMargins(20, 0, 0, 0)
        self.top_label_left = QLabel("Visual Novel Clearer")
        self.top_label_left.setStyleSheet("font: 700 10pt 'Segoe UI'")
        # 空间
        self.top_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # 字体修改
        # 窗口功能按键
        self.minimize_btn = FPushButton(height=self.top_bar.height(),
                                        minimum_width=self.top_bar.height(),
                                        btn_color=self.theme['MainContent_background'],
                                        icon_path=self.icon_folder/'icon_minimize.svg')
        self.maximize_btn = FPushButton(height=self.top_bar.height(),
                                        minimum_width=self.top_bar.height(),
                                        btn_color=self.theme['MainContent_background'],
                                        icon_path=self.icon_folder/'icon_maximize.svg')
        self.close_btn = FPushButton(height=self.top_bar.height(),
                                     minimum_width=self.top_bar.height(),
                                     btn_color=self.theme['MainContent_background'],
                                     icon_path=self.icon_folder/'icon_close.svg')
        # 添加控件
        self.top_bar_layout.addWidget(self.top_label_left)
        self.top_bar_layout.addItem(self.top_spacer)
        self.top_bar_layout.addWidget(self.minimize_btn)
        self.top_bar_layout.addWidget(self.maximize_btn)
        self.top_bar_layout.addWidget(self.close_btn)

    def setup_pages(self):
        # 内容页
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("font-size: 10pt; color: #f8f8f2;")

    def setup_bottom_bar(self):
        # 底部状态栏
        self.bottom_bar = QFrame()
        self.bottom_bar.setMinimumHeight(30)
        self.bottom_bar.setMaximumHeight(30)
        self.bottom_bar.setStyleSheet(f"background-color: {self.theme['MainContent_bar']};")
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(10, 0, 2.5, 0)
        self.bottom_label_left = QLabel("准备就绪！")
        self.bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # 窗口尺寸控制
        self.setup_resize_botton()
        # 添加组件
        self.bottom_bar_layout.addWidget(self.bottom_label_left)
        self.bottom_bar_layout.addItem(self.bottom_spacer)
        self.bottom_bar_layout.addWidget(self.frame_grip)

    def setup_resize_botton(self):
        self.frame_grip = QFrame()
        self.frame_grip.setObjectName(u"frame_grip")
        self.frame_grip.setMinimumSize(QSize(30, 30))
        self.frame_grip.setMaximumSize(QSize(30, 30))
        self.frame_grip.setStyleSheet(u"padding: 5px;")
        self.frame_grip.setFrameShape(QFrame.StyledPanel)
        self.frame_grip.setFrameShadow(QFrame.Raised)
        self.sizegrip = QSizeGrip(self.frame_grip)
        self.sizegrip.setStyleSheet(f"QSizeGrip {{ width: 10px; height: 10px; margin: 5px;background-color: {self.theme['MainContent_font']}; border-radius: 10px;}} QSizeGrip:hover {{ background-color: yellow}}")
        self.sizegrip.setToolTip('窗口缩放')
