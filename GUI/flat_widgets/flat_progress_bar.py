# -*- coding: utf-8 -*-

from ..qt_core import *


class FProgressBar(QProgressBar):
    """扁平化进度条"""

    def __init__(self,
                 width=None,
                 height=None,
                 border_radius=10):
        QProgressBar.__init__(self)

        self.width = width
        self.height = height
        self.border_radius = border_radius
        # 如果指定了宽高，则固定宽高
        if self.height:
            self.setMaximumHeight(self.height)
            self.setMaximumHeight(self.height)
        if self.width:
            self.setMaximumWidth(self.width)
            self.setMaximumWidth(self.width)

        self.change_style()

    def change_style(self):
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgb(98, 114, 164);
                color: rgb(200, 200, 200);
                border-style: none;
                border-radius: {self.border_radius}px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                border-radius: {self.border_radius}px;
                background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(254, 121, 199, 255), stop:1 rgba(170, 85, 255, 255));
            }}
            """)
