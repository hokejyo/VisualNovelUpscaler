# -*- coding: utf-8 -*-

from ..qt_core import *


class FIconButton(QPushButton):
    """扁平化启动按钮"""

    def __init__(self,
                 text=None,
                 minimum_width=50,
                 height=40,
                 icon_path=None,
                 icon_color="#c3ccdf",
                 text_color="#c3ccdf",
                 btn_color="#44475a",
                 btn_hover="#4f5368",
                 btn_pressed="#282a36",
                 text_align="center",
                 border_radius=15,
                 ):
        QPushButton.__init__(self)
        if text is not None:
            self.setText(text)
        self.setCursor(Qt.PointingHandCursor)
        # 最小宽度
        self.minimum_width = minimum_width
        # 高度
        self.height = height
        # 图标路径
        self.icon_path = icon_path
        # 图标颜色
        self.icon_color = icon_color
        # 字体颜色
        self.text_color = text_color
        # 背景颜色
        self.btn_color = btn_color
        # 鼠标掠过颜色
        self.btn_hover = btn_hover
        # 鼠标按下颜色
        self.btn_pressed = btn_pressed
        # 字体对齐方式
        self.text_align = text_align
        # 边界圆角半径
        self.border_radius = border_radius
        # 设置样式
        self.set_style()
        # 设置图标
        if self.icon_path is not None:
            self.set_icon(self.icon_path)

    def set_style(self):
        style = f"""
        QPushButton {{
            color: {self.text_color};
            background-color: {self.btn_color};
            text-align: {self.text_align};
            border: none;
            border-radius: {self.border_radius}px;
            font: 'Segoe UI';
            margin-right: 5;
        }}
        QPushButton:hover {{
            background-color: {self.btn_hover};
        }}
        QPushButton:pressed {{
            background-color: {self.btn_pressed};
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumWidth(self.minimum_width)
        self.setMaximumHeight(self.height)
        self.setMinimumHeight(self.height)

    def set_icon(self, icon_path):
        self.icon_pix = QPixmap(icon_path)
        # self.icon_pix.scaledToHeight(self.height)
        self.setIcon(self.icon_pix)
