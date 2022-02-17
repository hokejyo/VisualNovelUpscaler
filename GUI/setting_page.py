# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *
from .sr_engine_settings import *
from Core import get_gpu_list


class SettingPage(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.theme = {'MainContent_background': '#282a36', 'MainContent_font': '#6272a4', 'MainContent_bar': '#21232d', }
        self.sr_engine_list = ['waifu2x_ncnn',
                               'real_cugan',
                               'real_esrgan',
                               'srmd_ncnn',
                               'realsr_ncnn',
                               'anime4k']
        self.initUI()

    def initUI(self):
        # self.setStyleSheet(f"background-color: {self.theme['MainContent_background']};color: {self.theme['MainContent_font']};font: 700 12pt 'Segoe UI';")
        self.setup_layouts()
        self.setup_connections()

    def setup_layouts(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 20)
        self.setup_general_settings()
        layout.addWidget(self.general_setting_frame)
        self.setup_sr_engine_settings()
        layout.addWidget(self.image_setting_frame)

        self.setup_video_settings()
        layout.addWidget(self.video_setting_frame)

        spacer_mid1 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer_mid2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer_mid3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_mid1)
        layout.addItem(spacer_mid2)
        layout.addItem(spacer_mid3)

        self.setup_bottom_bar()
        layout.addWidget(self.bottom_bar)

    def setup_connections(self):
        self.sr_engine_combobox.currentTextChanged.connect(self.switch_image_sr_engine_settings)
        self.image_sr_engine_combobox.currentTextChanged.connect(self.image_engine_auto_switch)
        self.video_sr_engine_combobox.currentTextChanged.connect(self.video_engine_auto_switch)

    def setup_general_settings(self):
        self.general_setting_frame = QFrame()
        layout = QFormLayout(self.general_setting_frame)
        layout.setSpacing(5)
        self.general_setting_lb = QLabel('通用设置')
        layout.addRow(self.general_setting_lb)
        self.cpu_lb = QLabel('CPU并发核数：')
        self.cpu_spinbox = QSpinBox()
        self.cpu_spinbox.setMinimum(1)
        layout.addRow(self.cpu_lb, self.cpu_spinbox)
        self.gpu_lb = QLabel('GPU型号：')
        self.gpu_combobox = QComboBox()
        self.gpu_combobox.addItems(get_gpu_list())
        layout.addRow(self.gpu_lb, self.gpu_combobox)
        self.text_encoding_lb = QLabel('文本编码列表：')
        self.text_encoding_line_edit = FLineEdit(place_holder_text='使用英文逗号分隔，优先级从左到右')
        layout.addRow(self.text_encoding_lb, self.text_encoding_line_edit)
        self.image_sr_engine_lb = QLabel('图片超分引擎：')
        self.image_sr_engine_combobox = QComboBox()
        image_sr_engine_list = [sr_engine for sr_engine in self.sr_engine_list]
        image_sr_engine_list.remove('anime4k')
        self.image_sr_engine_combobox.addItems(image_sr_engine_list)
        layout.addRow(self.image_sr_engine_lb, self.image_sr_engine_combobox)
        self.video_sr_engine_lb = QLabel('视频超分引擎：')
        self.video_sr_engine_combobox = QComboBox()
        self.video_sr_engine_combobox.addItems(self.sr_engine_list)
        layout.addRow(self.video_sr_engine_lb, self.video_sr_engine_combobox)
        self.tta_lb = QLabel('TTA模式：')
        self.tta_checkbox = QCheckBox()
        layout.addRow(self.tta_lb, self.tta_checkbox)

    def setup_bottom_bar(self):
        width = 60
        height = 30
        self.bottom_bar = QFrame()
        self.bottom_bar.setMinimumHeight(height)
        self.bottom_bar.setMaximumHeight(height)
        layout = QHBoxLayout(self.bottom_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)
        bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(bottom_spacer)
        self.save_btn = FPushButton(text='保存', height=height, minimum_width=width, text_padding=0, text_align='center', border_radius=15)
        self.cancle_btn = FPushButton(text='取消', height=height, minimum_width=width, text_padding=0, text_align='center', border_radius=15)
        self.reset_btn = FPushButton(text='重置', height=height, minimum_width=width, text_padding=0, text_align='center', border_radius=15)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancle_btn)
        layout.addWidget(self.reset_btn)

    def setup_sr_engine_settings(self):
        self.image_setting_frame = QFrame()
        layout = QFormLayout(self.image_setting_frame)
        layout.setSpacing(5)

        self.sr_engine_setting_lb = QLabel('超分引擎设置')
        layout.addRow(self.sr_engine_setting_lb)
        self.sr_engine_lb = QLabel('超分辨率引擎：')
        self.sr_engine_combobox = QComboBox()
        self.sr_engine_combobox.addItems(self.sr_engine_list)
        layout.addRow(self.sr_engine_lb, self.sr_engine_combobox)

        self.image_setting_stacks = QStackedWidget()
        # self.image_setting_frame.setMinimumHeight(188)
        # self.image_setting_frame.setMaximumHeight(188)
        layout.addRow(self.image_setting_stacks)
        self.real_cugan_settings = RealCUGNSettings()
        self.image_setting_stacks.addWidget(self.real_cugan_settings)
        self.waifu2x_ncnn_settings = Waifu2xNCNNSettings()
        self.image_setting_stacks.addWidget(self.waifu2x_ncnn_settings)
        self.real_esrgan_settings = RealESRGANSettings()
        self.image_setting_stacks.addWidget(self.real_esrgan_settings)
        self.srmd_ncnn_settings = SRMDNCNNSettings()
        self.image_setting_stacks.addWidget(self.srmd_ncnn_settings)
        self.realsr_ncnn_settings = RealSRNCNNSettings()
        self.image_setting_stacks.addWidget(self.realsr_ncnn_settings)
        self.anime4k_settings = Anime4KSettings()
        self.image_setting_stacks.addWidget(self.anime4k_settings)

    def switch_image_sr_engine_settings(self):
        sr_engine = self.sr_engine_combobox.currentText()
        match sr_engine:
            case 'waifu2x_ncnn':
                self.image_setting_stacks.setCurrentWidget(self.waifu2x_ncnn_settings)
            case 'real_cugan':
                self.image_setting_stacks.setCurrentWidget(self.real_cugan_settings)
            case 'real_esrgan':
                self.image_setting_stacks.setCurrentWidget(self.real_esrgan_settings)
            case 'srmd_ncnn':
                self.image_setting_stacks.setCurrentWidget(self.srmd_ncnn_settings)
            case 'realsr_ncnn':
                self.image_setting_stacks.setCurrentWidget(self.realsr_ncnn_settings)
            case 'anime4k':
                self.image_setting_stacks.setCurrentWidget(self.anime4k_settings)

    def image_engine_auto_switch(self):
        sr_engine = self.image_sr_engine_combobox.currentText()
        self.sr_engine_combobox.setCurrentText(sr_engine)

    def video_engine_auto_switch(self):
        sr_engine = self.video_sr_engine_combobox.currentText()
        self.sr_engine_combobox.setCurrentText(sr_engine)

    def setup_video_settings(self):
        self.video_setting_frame = QFrame()
        layout = QFormLayout(self.video_setting_frame)
        layout.setSpacing(5)
        self.video_setting_lb = QLabel('视频设置')
        layout.addRow(self.video_setting_lb)
        self.video_quality_lb = QLabel('输出视频质量：')
        self.video_quality_spinbox = QSpinBox()
        self.video_quality_spinbox.setRange(0, 10)
        layout.addRow(self.video_quality_lb, self.video_quality_spinbox)
