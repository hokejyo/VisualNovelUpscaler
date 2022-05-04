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


class RealCUGNSettings(QFrame):

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

        self.sync_gap_mode_lb = QLabel('同步间隙等级：')
        self.sync_gap_mode_spinbox = QSpinBox()
        self.sync_gap_mode_spinbox.setRange(0, 3)
        layout.addRow(self.sync_gap_mode_lb, self.sync_gap_mode_spinbox)

        self.modle_name_lb = QLabel('超分模型选择：')
        self.modle_name_combobox = QComboBox()
        layout.addRow(self.modle_name_lb, self.modle_name_combobox)
        self.modle_name_combobox.addItems(['models-se', 'models-nose'])

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
        self.modle_name_combobox.addItems(['realesrgan-x4plus', 'realesrgan-x4plus-anime', 'realesr-animevideov3-x2', 'realesr-animevideov3-x3', 'realesr-animevideov3-x4'])

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


class Anime4KSettings(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.acnet_lb = QLabel('ACNet模式：')
        self.acnet_checkbox = QCheckBox()
        layout.addRow(self.acnet_lb, self.acnet_checkbox)

        self.hdn_mode_lb = QLabel('HDN模式：')
        self.hdn_mode_checkbox = QCheckBox()
        layout.addRow(self.hdn_mode_lb, self.hdn_mode_checkbox)

        self.hdn_level_lb = QLabel('降噪去噪等级：')
        self.hdn_level_spinbox = QSpinBox()
        self.hdn_level_spinbox.setRange(1, 3)
        layout.addRow(self.hdn_level_lb, self.hdn_level_spinbox)
