# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *
from .left_menu import LeftMenu
from .main_content import MainContent
from .image_page import ImagePage
from .game_page import GamePage
from .info_page import InfoPage
from .setting_page import SettingPage


class MainUI(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

        def moveWindow(event):
            if self.is_maxed:
                x_left = event.globalPosition().toPoint().x()-self.leftmenu.width()
                x_right = self.width()-event.globalPosition().toPoint().x()
                x_left_precent = x_left/self.maincontent.top_bar.width()
                y_top = event.globalPosition().toPoint().y()
                self.maximize_restore()
                if x_left_precent < 0.25:
                    self.move(event.globalPosition().toPoint()-QPoint(self.leftmenu.width()+x_left, y_top))
                elif x_left_precent > 0.75:
                    self.move(event.globalPosition().toPoint()-QPoint(self.width()-x_right, y_top))
                else:
                    # 移动到等比例位置
                    self.move(event.globalPosition().toPoint()-QPoint(self.leftmenu.width()+self.maincontent.top_bar.width()*x_left_precent, y_top))
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()
        # 设置标题栏能用鼠标拖动
        self.maincontent.top_bar.mouseMoveEvent = moveWindow

    def initUI(self):
        # 设置标题
        self.setWindowTitle('Visual Novel Clearer')
        # 移除标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 改变尺寸
        self.resize(1080, 720)
        # 设置最小尺寸
        self.setMinimumSize(950, 680)
        self.setup_layouts()
        self.setup_pages()
        self.setup_connections()
        self.move_to_center()
        self.is_maxed = False
        # 设置圆角
        self.setStyleSheet("QFrame {border-radius: 15px;}")
        # 设置透明度
        self.setWindowOpacity(1)
        # 显示页面2
        self.show_image_page()

    def setup_layouts(self):
        self.central_frame = QFrame()
        self.setCentralWidget(self.central_frame)
        # 主窗口布局
        main_layout = QHBoxLayout(self.central_frame)
        # 设置页边距都为0
        main_layout.setContentsMargins(0, 0, 0, 0)
        # 设置部件间距为0
        main_layout.setSpacing(0)
        # 添加左侧菜单
        self.leftmenu = LeftMenu()
        main_layout.addWidget(self.leftmenu)
        # 添加内容页面
        self.maincontent = MainContent()
        main_layout.addWidget(self.maincontent)

    def set_version(self, version_text):
        self.leftmenu.version_label.setText(version_text)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_to_center(self):
        # 获取屏幕坐标系
        screen_center = QGuiApplication.screens()[0].geometry().center()
        self.move(screen_center-self.frameGeometry().center())

    def setup_connections(self):
        self.leftmenu.image_button.clicked.connect(self.show_image_page)
        self.leftmenu.game_button.clicked.connect(self.show_game_page)
        self.leftmenu.info_btn.clicked.connect(self.show_info_page)
        self.leftmenu.setting_btn.clicked.connect(self.show_setting_page)
        self.maincontent.minimize_btn.clicked.connect(self.showMinimized)
        self.maincontent.maximize_btn.clicked.connect(self.maximize_restore)
        # 退出询问
        self.maincontent.close_btn.clicked.connect(self.quit_question)
        # self.maincontent.close_btn.clicked.connect(self.close)

    def setup_pages(self):
        # 内容页
        self.imagepage = ImagePage()
        self.maincontent.pages.addWidget(self.imagepage)

        self.gamepage = GamePage()
        self.maincontent.pages.addWidget(self.gamepage)

        self.infopage = InfoPage()
        self.maincontent.pages.addWidget(self.infopage)

        self.settingpage = SettingPage()
        self.maincontent.pages.addWidget(self.settingpage)

    def show_image_page(self):
        self.maincontent.pages.setCurrentWidget(self.imagepage)
        if self.leftmenu.image_button.is_active:
            self.leftmenu.fold_menu()
        else:
            self.leftmenu.reset_selection()
            self.leftmenu.image_button.set_active(True)

    def show_game_page(self):
        self.maincontent.pages.setCurrentWidget(self.gamepage)
        if self.leftmenu.game_button.is_active:
            self.leftmenu.fold_menu()
        else:
            self.leftmenu.reset_selection()
            self.leftmenu.game_button.set_active(True)

    def show_info_page(self):
        self.maincontent.pages.setCurrentWidget(self.infopage)
        if self.leftmenu.info_btn.is_active:
            self.leftmenu.fold_menu()
        else:
            self.leftmenu.reset_selection()
            self.leftmenu.info_btn.set_active(True)

    def show_setting_page(self):
        self.maincontent.pages.setCurrentWidget(self.settingpage)
        if self.leftmenu.setting_btn.is_active:
            self.leftmenu.fold_menu()
        else:
            self.leftmenu.reset_selection()
            self.leftmenu.setting_btn.set_active(True)

    def maximize_restore(self):
        # print(self.settingpage.image_setting_frame.height(), self.settingpage.image_setting_stacks.height())
        # print(self.width(), self.height())
        if not self.is_maxed:
            # 放大时取消圆角，填补空隙
            self.setStyleSheet("QFrame {border-radius: 0px;}")
            self.showMaximized()
            self.is_maxed = True
        else:
            self.setStyleSheet("QFrame {border-radius: 15px;}")
            self.showNormal()
            self.is_maxed = False

    def quit_question(self):
        # 退出时询问
        quit_message = QMessageBox()
        reply = quit_message.question(self, '退出程序', '确认退出？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.close() if reply == QMessageBox.Yes else None
