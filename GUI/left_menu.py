# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class LeftMenu(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.icon_folder = Path(sys.argv[0]).parent/'Icons'
        # self.setStyleSheet("background-color: #44475a; border-radius: 15px;")
        self.setStyleSheet("background-color: #44475a")
        self.setup_layouts()
        self.setup_connections()

    def setup_connections(self):
        self.menu_button.clicked.connect(self.fold_menu)
        # self.page1_button.clicked.connect(lambda: self.fold_menu() if self.page1_button.is_active else None)

    def setup_layouts(self):
        # 设置最大、最小宽度
        self.setMaximumWidth(50)
        self.setMinimumWidth(50)
        # 左侧菜单布局
        self.left_menu_layout = QVBoxLayout(self)
        self.left_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_layout.setSpacing(0)
        # 顶部区域
        self.setup_left_menu_top()
        # 中部空间
        self.left_menu_spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # 底部区域
        self.setup_left_menu_bottom()
        # 底部文字
        self.setup_left_menu_label()
        # 添加组件进布局
        self.left_menu_layout.addWidget(self.left_menu_top_frame)
        self.left_menu_layout.addItem(self.left_menu_spacer)
        self.left_menu_layout.addWidget(self.left_menu_bottom_frame)
        self.left_menu_layout.addWidget(self.version_label)

    def setup_left_menu_top(self):
        # 左侧菜单顶部区域
        self.left_menu_top_frame = QFrame()
        self.left_menu_top_frame.setMinimumHeight(40)
        self.left_menu_top_layout = QVBoxLayout(self.left_menu_top_frame)
        self.left_menu_top_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_top_layout.setSpacing(0)
        # 按钮
        self.menu_button = FPushButton(text="折叠菜单", text_padding=60, icon_path=self.icon_folder/'columns.svg')
        self.image_button = FPushButton(text="图像增强", text_padding=60, icon_path=self.icon_folder/'slack.svg')
        self.game_button = FPushButton(text="视觉小说", text_padding=60, icon_path=self.icon_folder/'book-open.svg')
        self.text_button = FPushButton(text="文本处理", text_padding=60, icon_path=self.icon_folder/'edit.svg')
        # self.page3_button = FPushButton(text="批量处理", text_padding=60, icon_path=self.icon_folder/'trello.svg')
        self.left_menu_top_layout.addWidget(self.menu_button)
        self.left_menu_top_layout.addWidget(self.image_button)
        self.left_menu_top_layout.addWidget(self.game_button)
        self.left_menu_top_layout.addWidget(self.text_button)
        # self.left_menu_top_layout.addWidget(self.page3_button)

    def setup_left_menu_bottom(self):
        # 菜单底部布局
        self.left_menu_bottom_frame = QFrame()
        self.left_menu_bottom_frame.setMinimumHeight(40)
        self.left_menu_bottom_layout = QVBoxLayout(self.left_menu_bottom_frame)
        self.left_menu_bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_bottom_layout.setSpacing(0)
        self.info_btn = FPushButton(text='关于', text_padding=60, icon_path=self.icon_folder/'info.svg')
        self.setting_btn = FPushButton(text='设置', text_padding=60, icon_path=self.icon_folder/'settings.svg')
        self.left_menu_bottom_layout.addWidget(self.info_btn)
        self.left_menu_bottom_layout.addWidget(self.setting_btn)

    def setup_left_menu_label(self):
        # 版本号
        self.version_label = QLabel('version')
        # 设置对齐和字体高度、颜色
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setMinimumHeight(30)
        self.version_label.setMaximumHeight(30)
        self.version_label.setStyleSheet("color: #c3ccdf")

    def fold_menu(self):
        # 折叠菜单
        menu_width = self.width()
        width = 50
        if menu_width == 50:
            width = 240
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setStartValue(menu_width)
        self.animation.setEndValue(width)
        self.animation.setDuration(200)
        self.animation.start()

    def reset_selection(self):
        # 重置为非活动状态
        for btn in self.findChildren(QPushButton):
            try:
                btn.set_active(False)
            except:
                pass
