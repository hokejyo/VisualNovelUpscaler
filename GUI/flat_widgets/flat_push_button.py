# -*- coding: utf-8 -*-

from ..qt_core import *


class FPushButton(QPushButton):
    """扁平化按钮"""

    def __init__(self,
                 text='',
                 height=40,
                 minimum_width=50,
                 icon_path=None,
                 icon_color="#c3ccdf",
                 text_color="#c3ccdf",
                 btn_color="#44475a",
                 btn_hover="#4f5368",
                 btn_pressed="#282a36",
                 text_padding=0,
                 text_align="left",
                 border_width=5,
                 border_direction="border-right",
                 border_radius=15,
                 is_active=False
                 ):
        QPushButton.__init__(self)
        self.setText(text)
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        self.setMinimumWidth(minimum_width)
        self.setCursor(Qt.PointingHandCursor)
        # 最小宽度
        self.minimum_width = minimum_width
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
        # 左边距
        self.text_padding = text_padding
        # 字体对齐方式
        self.text_align = text_align
        # 激活边界标志宽度
        self.border_width = border_width
        # 激活边界标志方向
        self.border_direction = border_direction
        # 边界圆角半径
        self.border_radius = border_radius
        # 是否激活
        self.is_active = is_active
        self.set_style()

    def set_active(self, is_active):
        self.is_active = is_active
        self.set_style()

    def set_style(self):
        normal_style = f"""
        QPushButton {{
            color: {self.text_color};
            background-color: {self.btn_color};
            padding-left: {self.text_padding}px;
            text-align: {self.text_align};
            border: none;
            border-radius: {self.border_radius}px;
            font: 'Segoe UI';
        }}
        QPushButton:hover {{
            background-color: {self.btn_hover};
        }}
        QPushButton:pressed {{
            background-color: {self.btn_pressed};
        }}
        """
        active_style = f"""
        QPushButton {{
            background-color: {self.btn_hover};
            {self.border_direction}: {self.border_width}px solid {self.btn_pressed};
        }}
        """
        if self.is_active:
            style = normal_style + active_style
        else:
            style = normal_style
        self.setStyleSheet(style)

    def paintEvent(self, event):
        QPushButton.paintEvent(self, event)
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setPen(Qt.NoPen)
        rect = QRect(0, 0, self.minimum_width, self.height())
        if self.icon_path:
            self.draw_icon(qp, rect)
        qp.end()

    def draw_icon(self, qp, rect):
        # 绘制图标
        icon = QPixmap(self.icon_path)
        painter = QPainter(icon)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(icon.rect(), self.icon_color)
        qp.drawPixmap(
            (rect.width() - icon.width()) / 2,
            (rect.height() - icon.height()) / 2,
            icon)
        painter.end()

    def show_shadow(self):
        # 显示阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.border_radius)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)
