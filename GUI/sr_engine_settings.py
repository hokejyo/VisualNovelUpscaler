# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class Waifu2xNCNNSettings(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.noise_level_lb = QLabel('降噪等级：')
        self.noise_level_spinbox = QSpinBox()
        self.noise_level_spinbox.setRange(-1, 3)
        layout.addRow(self.noise_level_lb, self.noise_level_spinbox)

        self.tile_size_lb = QLabel('分割尺寸：')
        self.tile_size_line_edit = FLineEdit()
        layout.addRow(self.tile_size_lb, self.tile_size_line_edit)

        self.modle_name_lb = QLabel('超分模型选择：')
        self.modle_name_combobox = QComboBox()
        layout.addRow(self.modle_name_lb, self.modle_name_combobox)
        self.modle_name_combobox.addItems(['models-cunet', 'models-upconv_7_anime_style_art_rgb', 'models-upconv_7_photo'])

        self.load_proc_save_lb = QLabel('显卡线程分配：')
        self.load_proc_save_line_edit = FLineEdit()
        self.load_proc_save_line_edit = FLineEdit(place_holder_text='解码:放大:编码')
        layout.addRow(self.load_proc_save_lb, self.load_proc_save_line_edit)


class RealESRGANSettings(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.tile_size_lb = QLabel('分割尺寸：')
        self.tile_size_line_edit = FLineEdit()
        layout.addRow(self.tile_size_lb, self.tile_size_line_edit)

        self.modle_name_lb = QLabel('超分模型选择：')
        self.modle_name_combobox = QComboBox()
        layout.addRow(self.modle_name_lb, self.modle_name_combobox)
        self.modle_name_combobox.addItems(['realesrgan-x4plus', 'realesrnet-x4plus', 'realesrgan-x4plus-anime', 'RealESRGANv2-animevideo-xsx2', 'RealESRGANv2-animevideo-xsx4'])

        self.load_proc_save_lb = QLabel('显卡线程分配：')
        self.load_proc_save_line_edit = FLineEdit()
        self.load_proc_save_line_edit = FLineEdit(place_holder_text='解码:放大:编码')
        layout.addRow(self.load_proc_save_lb, self.load_proc_save_line_edit)


class SRMDNCNNSettings(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.noise_level_lb = QLabel('降噪等级：')
        self.noise_level_spinbox = QSpinBox()
        self.noise_level_spinbox.setRange(-1, 10)
        layout.addRow(self.noise_level_lb, self.noise_level_spinbox)

        self.tile_size_lb = QLabel('分割尺寸：')
        self.tile_size_line_edit = FLineEdit()
        layout.addRow(self.tile_size_lb, self.tile_size_line_edit)

        self.load_proc_save_lb = QLabel('显卡线程分配：')
        self.load_proc_save_line_edit = FLineEdit()
        self.load_proc_save_line_edit = FLineEdit(place_holder_text='解码:放大:编码')
        layout.addRow(self.load_proc_save_lb, self.load_proc_save_line_edit)


class RealSRNCNNSettings(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.tile_size_lb = QLabel('分割尺寸：')
        self.tile_size_line_edit = FLineEdit()
        layout.addRow(self.tile_size_lb, self.tile_size_line_edit)

        self.modle_name_lb = QLabel('超分模型选择：')
        self.modle_name_combobox = QComboBox()
        layout.addRow(self.modle_name_lb, self.modle_name_combobox)
        self.modle_name_combobox.addItems(['models-DF2K', 'models-DF2K_JPEG'])

        self.load_proc_save_lb = QLabel('显卡线程分配：')
        self.load_proc_save_line_edit = FLineEdit()
        self.load_proc_save_line_edit = FLineEdit(place_holder_text='解码:放大:编码')
        layout.addRow(self.load_proc_save_lb, self.load_proc_save_line_edit)
