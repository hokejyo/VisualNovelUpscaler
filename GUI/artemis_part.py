# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class ArtemisPart(FTabWidget):
    def __init__(self):
        FTabWidget.__init__(self, height=40, position='top')
        self.icon_folder = Path(sys.argv[0]).parent/'Icons'
        self.initUI()
        self.set_ratio_state()
        self.set_resolution_state()
        self.select_all_part()
        self.set_game_resolution_encoding(1280, 720, 'UTF-8')
        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def initUI(self):

        self.setup_hd_parts()
        self.addTab(self.hd_parts_frame, '高清重制')

        self.setup_work_up()
        self.addTab(self.work_up_frame, '重制后处理')

        self.setup_zip()
        self.addTab(self.zip_frame, '存储优化')

        self.setup_connections()

    def setup_zip(self):
        self.zip_frame = QFrame()
        layout = QVBoxLayout(self.zip_frame)
        layout.addWidget(QLabel('正在开发中...'))

    def setup_hd_parts(self):
        self.hd_parts_frame = QFrame()
        layout = QHBoxLayout(self.hd_parts_frame)

        self.setup_choose_resolution()
        layout.addWidget(self.choose_resolution_Frame, 1)

        self.setup_select_run_parts()
        layout.addWidget(self.select_run_parts_frame, 1)

    def setup_choose_resolution(self):
        self.choose_resolution_Frame = QFrame()
        layout1 = QFormLayout(self.choose_resolution_Frame)
        self.choose_resolution_lb = QLabel('分辨率设定：')
        layout2 = QVBoxLayout()
        layout2.setContentsMargins(0, 5, 0, 0)
        layout1.addRow(self.choose_resolution_lb, layout2)

        formlayout1 = QFormLayout()
        self.before_resolution_lb = QLabel('原生分辨率：')
        resolution_hlayout = QHBoxLayout()
        resolution_hlayout.setContentsMargins(0, 0, 0, 0)
        resolution_hlayout.setSpacing(15)
        self.before_resolution = QLabel()
        self.main_encoding = QLabel()
        resolution_hlayout.addWidget(self.before_resolution)
        resolution_hlayout.addWidget(self.main_encoding)
        self.check_resolution_btn = FPushButton(text='检测分辨率', height=20, minimum_width=80, text_padding=0, text_align='center', border_radius=10)
        self.check_resolution_btn.show_shadow()
        resolution_hlayout.addWidget(self.check_resolution_btn)
        _spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        resolution_hlayout.addItem(_spacer)
        formlayout1.addRow(self.before_resolution_lb, resolution_hlayout)

        self.s1080p_btn = QRadioButton('1080P')
        self.s2k_btn = QRadioButton('2K')
        self.s4k_btn = QRadioButton('4K')

        formlayout2 = QFormLayout()

        self.custiom_ratio_btn = QRadioButton('自定义放大倍率：')
        self.custiom_ratio_spinbox = QDoubleSpinBox()
        self.custiom_ratio_spinbox.setDecimals(3)
        self.custiom_ratio_spinbox.setSingleStep(0.5)
        formlayout2.addRow(self.custiom_ratio_btn, self.custiom_ratio_spinbox)

        self.custom_resolution_btn = QRadioButton('自定义分辨率：')
        custom_resolution_hlayout = QHBoxLayout()
        self.width_line_edit = FLineEdit()
        self.x_label = QLabel('x')
        self.x_label.setMaximumWidth(10)
        self.height_line_edit = FLineEdit()
        custom_resolution_hlayout.addWidget(self.width_line_edit)
        custom_resolution_hlayout.addWidget(self.x_label)
        custom_resolution_hlayout.addWidget(self.height_line_edit)
        formlayout2.addRow(self.custom_resolution_btn, custom_resolution_hlayout)

        layout2.addLayout(formlayout1)
        layout2.addWidget(self.s1080p_btn)
        layout2.addWidget(self.s2k_btn)
        layout2.addWidget(self.s4k_btn)
        layout2.addLayout(formlayout2)
        # 分组
        self.sr_group = QButtonGroup()
        self.sr_group.addButton(self.s1080p_btn)
        self.sr_group.addButton(self.s2k_btn)
        self.sr_group.addButton(self.s4k_btn)
        self.sr_group.addButton(self.custiom_ratio_btn)
        self.sr_group.addButton(self.custom_resolution_btn)

    def setup_select_run_parts(self):
        self.select_run_parts_frame = QFrame()
        layout1 = QFormLayout(self.select_run_parts_frame)

        self.game_part_lb = QLabel('处理部分选择：')
        layout2 = QVBoxLayout()
        layout2.setContentsMargins(0, 4, 0, 0)
        layout1.addRow(self.game_part_lb, layout2)

        self.text_part = QCheckBox('文本')
        self.image_part = QCheckBox('图片')
        self.animation_part = QCheckBox('动画')
        self.video_part = QCheckBox('视频')
        self.select_all_btn = FPushButton(text='全选', height=20, minimum_width=50, text_padding=0, text_align='center', border_radius=10)
        self.select_none_btn = FPushButton(text='全不选', height=20, minimum_width=50, text_padding=0, text_align='center', border_radius=10)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.select_all_btn)
        hlayout.addWidget(self.select_none_btn)

        layout2.addWidget(self.text_part)
        layout2.addWidget(self.image_part)
        layout2.addWidget(self.animation_part)
        layout2.addWidget(self.video_part)
        layout2.addLayout(hlayout)

        self.patch_mode_lb = QLabel('高清补丁输出：')
        self.keep_mode_btn = QCheckBox('保持目录结构')
        layout1.addRow(self.patch_mode_lb, self.keep_mode_btn)
        self.keep_mode_btn.setChecked(True)
        self.keep_mode_btn.setDisabled(True)

    def setup_work_up(self):
        self.work_up_frame = QFrame()
        self.work_up_layout = QFormLayout(self.work_up_frame)
        self.work_up_layout.setContentsMargins(15, 25, 15, 0)
        self.work_up_layout.setSpacing(15)

        self.setup_pfs_unpack()

        self.work_up_group = QButtonGroup()
        self.work_up_group.addButton(self.pfs_unpack_btn)

    def setup_pfs_unpack(self):
        self.pfs_unpack_btn = QRadioButton('批量解包：')
        self.pfs_unpack_btn.setChecked(True)
        layout = QHBoxLayout()
        self.work_up_layout.addRow(self.pfs_unpack_btn, layout)
        self.pfs_encoding_label = QLabel('编码格式：')
        self.pfs_encoding_line_edit = FLineEdit('UTF-8')
        layout.addWidget(self.pfs_encoding_label)
        layout.addWidget(self.pfs_encoding_line_edit)

    def check_pfs_unpack_btn(self):
        self.pfs_unpack_btn.setChecked(True)


    def setup_connections(self):
        self.s1080p_btn.toggled.connect(self.s1080p_btn_ratio)
        self.s2k_btn.toggled.connect(self.s2k_btn_ratio)
        self.s4k_btn.toggled.connect(self.s4k_btn_ratio)
        self.custiom_ratio_btn.toggled.connect(self.set_ratio_state)
        self.custiom_ratio_spinbox.textChanged.connect(self.auto_change_width_height)
        self.custom_resolution_btn.toggled.connect(self.set_resolution_state)
        self.width_line_edit.textEdited.connect(self.auto_change_height_ratio)
        self.height_line_edit.textEdited.connect(self.auto_change_width_ratio)
        self.select_all_btn.clicked.connect(self.select_all_part)
        self.select_none_btn.clicked.connect(self.select_none_part)
        self.pfs_encoding_line_edit.textChanged.connect(self.check_pfs_unpack_btn)

    def select_all_part(self):
        for check_box in self.select_run_parts_frame.findChildren(QCheckBox):
            if check_box is self.keep_mode_btn:
                continue
            check_box.setChecked(True)

    def select_none_part(self):
        for check_box in self.select_run_parts_frame.findChildren(QCheckBox):
            if check_box is self.keep_mode_btn:
                continue
            check_box.setChecked(False)

    def set_ratio_state(self):
        if self.custiom_ratio_btn.isChecked():
            self.custiom_ratio_spinbox.setEnabled(True)
        else:
            self.custiom_ratio_spinbox.setDisabled(True)

    def set_resolution_state(self):
        if self.custom_resolution_btn.isChecked():
            self.width_line_edit.setEnabled(True)
            self.height_line_edit.setEnabled(True)
        else:
            self.width_line_edit.setDisabled(True)
            self.height_line_edit.setDisabled(True)

    def auto_change_height_ratio(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        try:
            ratio = int(self.width_line_edit.text())/width
            self.custiom_ratio_spinbox.setValue(ratio)
            self.height_line_edit.setText(str(int(height*ratio)))
        except:
            pass

    def auto_change_width_ratio(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        try:
            pass
            ratio = int(self.height_line_edit.text())/height
            self.custiom_ratio_spinbox.setValue(ratio)
            self.width_line_edit.setText(str(int(width*ratio)))
        except:
            pass

    def auto_change_width_height(self):
        # 避免信号冲突
        if not self.custom_resolution_btn.isChecked():
            width, height = map(int, self.before_resolution.text().split('x'))
            ratio = float(self.custiom_ratio_spinbox.value())
            self.width_line_edit.setText(str(int(width*ratio)))
            self.height_line_edit.setText(str(int(height*ratio)))

    def judge_scaled_resolution_btn(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        if width/height == 16/9:
            self.s1080p_btn.setEnabled(True)
            self.s2k_btn.setEnabled(True)
            self.s4k_btn.setEnabled(True)
            # self.s1080p_btn.setChecked(True)
        else:
            # 非16:9
            self.s1080p_btn.setDisabled(True)
            self.s2k_btn.setDisabled(True)
            self.s4k_btn.setDisabled(True)
        # 默认2倍放大
        self.custiom_ratio_btn.setChecked(True)
        self.custiom_ratio_spinbox.setValue(1)
        self.custiom_ratio_spinbox.setValue(2)

    def set_game_resolution_encoding(self, width, height, encoding):
        self.before_resolution.setText(f'{width}x{height}')
        self.main_encoding.setText(encoding)
        self.judge_scaled_resolution_btn()

    def s1080p_btn_ratio(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        ratio = 1080/height
        self.custiom_ratio_spinbox.setValue(ratio)

    def s2k_btn_ratio(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        ratio = 1440/height
        self.custiom_ratio_spinbox.setValue(ratio)

    def s4k_btn_ratio(self):
        width, height = map(int, self.before_resolution.text().split('x'))
        ratio = 2160/height
        self.custiom_ratio_spinbox.setValue(ratio)
