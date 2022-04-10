# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *


class ImagePage(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.icon_folder = Path(sys.argv[0]).parent/'Icons'
        self.initUI()

    def initUI(self):
        self.setup_layouts()
        self.setup_connections()
        add_shadow(self.list_widget)
        add_shadow(self.image_show_label)
        add_shadow(self.setting_frame)

    def setup_connections(self):
        self.input_line_edit.editingFinished.connect(self.get_image_list)
        self.input_line_edit.editingFinished.connect(self.auto_fill_output_folder)
        self.filter_line_edit.editingFinished.connect(self.get_image_list)
        self.list_widget.currentItemChanged.connect(self.show_image)
        self.input_btn.clicked.connect(self.choose_input_folder)
        self.output_btn.clicked.connect(self.choose_output_folder)
        self.ignr_btn.toggled.connect(self.get_image_list)

    def setup_layouts(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        self.setup_show_image_area()

        self.hlayout = QHBoxLayout()
        self.layout.addLayout(self.hlayout)

        self.setup_image_list_view()

        self.setup_settings()

        self.setup_in_out_folders()

        self.setup_run_part()


    def setup_settings(self):
        self.setting_frame = QFrame()
        self.hlayout.addWidget(self.setting_frame)
        self.set_formlayout = QFormLayout(self.setting_frame)

        self.custiom_ratio_lb = QLabel('图片放大倍率：')
        self.custiom_ratio_spinbox = QDoubleSpinBox()
        self.custiom_ratio_spinbox.setDecimals(3)
        self.custiom_ratio_spinbox.setSingleStep(0.5)
        self.custiom_ratio_spinbox.setValue(2)
        self.set_formlayout.addRow(self.custiom_ratio_lb, self.custiom_ratio_spinbox)

        self.output_extention_lab = QLabel('输出图片格式：')
        self.output_extention_line_edit = FLineEdit()
        self.output_extention_line_edit.setText('png')
        self.set_formlayout.addRow(self.output_extention_lab, self.output_extention_line_edit)

        self.filter_lab = QLabel('图片格式筛选：')
        self.filter_line_edit = FLineEdit(place_holder_text='使用英文逗号分隔图片格式')
        self.filter_line_edit.setText('png,jpg,jpeg,bmp,tif,tiff,webp,tga')
        self.set_formlayout.addRow(self.filter_lab, self.filter_line_edit)

        self.ignr_lb = QLabel('处理子文件夹：')
        self.ignr_btn = QCheckBox()
        self.ignr_btn.setChecked(True)
        self.set_formlayout.addRow(self.ignr_lb, self.ignr_btn)

        self.suffix_lab = QLabel('输出图片后缀：')
        self.suffix_line_edit = FLineEdit()
        self.set_formlayout.addRow(self.suffix_lab, self.suffix_line_edit)

    def setup_image_list_view(self):
        self.list_widget = QListWidget()
        self.hlayout.addWidget(self.list_widget)

    def setup_show_image_area(self):
        self.image_show_label = QLabel()
        self.image_show_label.setMinimumWidth(540)
        self.image_show_label.setMinimumHeight(360)
        self.layout.addWidget(self.image_show_label)

    def get_image_list(self):
        input_path = Path(self.input_line_edit.text().strip())
        try:
            self.list_widget.clear()
            extension_list = [('.' + extension.strip().lower()) for extension in self.filter_line_edit.text().split(',')]
            walk_mode = True if self.ignr_btn.isChecked() else False
            image_list = [file_path for file_path in input_path.file_list(walk_mode=walk_mode) if file_path.suffix.lower() in extension_list]
            for image_file in image_list:
                self.list_widget.addItem(image_file.to_str)
        except:
            self.list_widget.clear()

    def show_image(self):
        try:
            image_path = Path(self.list_widget.currentItem().text().strip())
            image_show_pix = QPixmap(image_path).scaledToHeight(self.image_show_label.height(), Qt.SmoothTransformation)
            self.image_show_label.setPixmap(image_show_pix)
        except:
            pass

    def setup_in_out_folders(self):
        layout1 = QHBoxLayout()
        self.layout.addLayout(layout1)

        self.input_btn = FIconButton('选择输入路径', minimum_width=100, height=30)
        self.input_line_edit = FLineEdit(place_holder_text='将图片文件或文件夹拖拽至此处', height=30, radius=12, text_padding=10)
        layout1.addWidget(self.input_line_edit)
        layout1.addWidget(self.input_btn)
        self.input_line_edit.dropEvent = self.drop_get_list

        layout2 = QHBoxLayout()
        self.layout.addLayout(layout2)
        self.output_btn = FIconButton('选择输出目录', minimum_width=100, height=30)
        self.output_line_edit = FLineEdit(place_holder_text='输出图片至此处', height=30, radius=12, text_padding=10)
        layout2.addWidget(self.output_line_edit)
        layout2.addWidget(self.output_btn)

    def choose_input_folder(self):
        path_text = QFileDialog.getExistingDirectory()
        if path_text:
            # 转换为操作系统支持的路径格式
            format_path_text = Path(path_text).to_str
            self.input_line_edit.setText(format_path_text)
            self.get_image_list()
            self.auto_fill_output_folder()

    def choose_output_folder(self):
        path_text = QFileDialog.getExistingDirectory()
        if path_text:
            # 转换为操作系统支持的路径格式
            format_path_text = Path(path_text).to_str
            self.output_line_edit.setText(format_path_text)

    def drop_get_list(self, event):
        file_path = Path(event.mimeData().text().replace('file:///', '').strip())
        self.input_line_edit.setText(str(file_path))
        self.get_image_list()
        self.auto_fill_output_folder()
        event.accept()

    def auto_fill_output_folder(self):
        output_folder_path = Path(self.input_line_edit.text().strip()).parent/'VNU_OUTPUT'
        self.output_line_edit.setText(str(output_folder_path))

    def setup_run_part(self):
        run_part_layout = QHBoxLayout()
        self.layout.addLayout(run_part_layout)

        self.status_progress_bar = FProgressBar(height=30, border_radius=12.5)
        run_part_layout.addWidget(self.status_progress_bar)

        self.run_btn = FIconButton(text="开始处理", minimum_width=150, height=30, icon_path=self.icon_folder/'icon_send.svg')
        run_part_layout.addWidget(self.run_btn)

    def set_running_state(self, state):
        if state == 0:
            self.run_btn.setEnabled(True)
            self.run_btn.setText('开始处理')
            self.run_btn.set_icon(self.icon_folder/'icon_send.svg')
            self.status_progress_bar.setRange(0, 100)
            self.status_progress_bar.setValue(0)
        elif state == 1:
            self.run_btn.setDisabled(True)
            self.run_btn.setText('正在统计')
            self.run_btn.set_icon(self.icon_folder/'clock.svg')
        elif state == 2:
            self.run_btn.setEnabled(True)
            self.run_btn.setText('开始处理')
            self.run_btn.set_icon(self.icon_folder/'icon_send.svg')
            self.status_progress_bar.setValue(100)
