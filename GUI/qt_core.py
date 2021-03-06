# -*- coding: utf-8 -*-

from Core import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

def add_shadow(target_widget):
    """
    @brief      给控件添加阴影

    @param      target_widget  控件
    """
    shadow = QGraphicsDropShadowEffect(target_widget)
    shadow.setBlurRadius(15)
    shadow.setXOffset(0)
    shadow.setYOffset(0)
    shadow.setColor(QColor(0, 0, 0, 200))
    target_widget.setGraphicsEffect(shadow)
