# -*- coding: utf-8 -*-

from ..qt_core import *


class FLineEdit(QLineEdit):
    """扁平化输入框"""

    def __init__(self,
                 text="",
                 place_holder_text="",
                 text_padding=0,
                 height=None,
                 radius=0,
                 border_size=2,
                 color="#FFF",
                 selection_color="#FFF",
                 bg_color="#333",
                 bg_color_active="#222",
                 context_color="#00ABE8"
                 ):
        QLineEdit.__init__(self)
        self.setAcceptDrops(True)
        # 参数设置
        if text:
            self.setText(text)
        if place_holder_text:
            self.setPlaceholderText(place_holder_text)
        if height:
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)
        self.text_padding = text_padding
        self.radius = radius
        self.border_size = border_size
        self.color = color
        self.selection_color = selection_color
        self.bg_color = bg_color
        self.bg_color_active = bg_color_active
        self.context_color = context_color
        self.set_style()

    def set_style(self):
        style = f'''
            QLineEdit {{
                background-color: {self.bg_color};
                border-radius: {self.radius}px;
                border: {self.border_size}px solid transparent;
                padding-left: {self.text_padding}px;
                padding-right: {self.text_padding}px;
                selection-color: {self.selection_color};
                selection-background-color: {self.context_color};
                color: {self.color};
            }}
            QLineEdit:focus {{
                border: {self.border_size}px solid {self.context_color};
                background-color: {self.bg_color_active};
            }}
            '''
        self.setStyleSheet(style)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # 拖拽选择文件
        file_path = Path(event.mimeData().text().replace('file:///', '').strip())
        # if file_path.is_dir():
        self.setText(str(file_path))
        event.accept()
