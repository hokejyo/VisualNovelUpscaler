# -*- coding: utf-8 -*-

from ..qt_core import *


class FTabWidget(QTabWidget):
    """扁平化标签页"""

    def __init__(self,
                 width=105,
                 height=35,
                 margin_left=15,
                 text_padding=10,
                 hide_edge=True,
                 position='top',
                 shape='triangle',
                 selection_color='#6272a4'):
        QTabWidget.__init__(self)

        # 标签宽
        self.width = width
        # 标签高
        self.height = height
        # 标签左余白
        self.margin_left = margin_left
        # 文字边距
        self.text_padding = text_padding
        # 是否隐藏边框
        self.hide_edge = hide_edge
        # 标签位置
        self.position = position
        # 标签形状
        self.shape = shape
        # 选中背景颜色
        self.selection_color = selection_color

        self.set_style()

    def set_style(self):
        un_selected_height = int(self.height/1.2)
        height_diff = self.height - un_selected_height
        style = f'''
            QTabBar::tab {{
                width: {self.width}px;
                height: {self.height}px;
                margin-left: {self.margin_left}px;
                padding-left: {self.text_padding}px;
                padding-right: {self.text_padding}px;
            }}
            QTabBar::tab:selected {{
                background: {self.selection_color};
            }}
            QTabBar::tab:!selected {{
                margin-{self.position}: {height_diff}px;
                height: {un_selected_height}px;
            }}
            '''
        # 应用样式
        self.setStyleSheet(style)
        # 去除边框
        if self.hide_edge:
            self.setDocumentMode(True)
        # 标签显示位置
        match self.position:
            case 'top':
                self.setTabPosition(QTabWidget.North)
            case 'bottom':
                self.setTabPosition(QTabWidget.South)
            case 'left':
                self.setTabPosition(QTabWidget.West)
            case 'right':
                self.setTabPosition(QTabWidget.East)
        # 改变标签形状
        match self.shape:
            case 'triangle':
                self.setTabShape(QTabWidget.Triangular)
            case 'round':
                self.setTabShape(QTabWidget.Rounded)

