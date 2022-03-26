# -*- coding: utf-8 -*-

from .qt_core import *
from .flat_widgets import *
from Core import Path


class ImagePage(QFrame):

    def __init__(self):
        QFrame.__init__(self)
        self.initUI()

    def initUI(self):
        self.setup_layouts()
        self.setup_connections()
        # self.add_shadow(self.list_widget)
        # self.add_shadow(self.image_show_label)

    def setup_connections(self):
        self.input_line_edit.editingFinished.connect(self.get_image_list)
        self.filter_line_edit.editingFinished.connect(self.get_image_list)
        self.list_widget.currentItemChanged.connect(self.show_image)

    def setup_layouts(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        self.setup_in_out_folders()
        self.setup_image_list_view()

        self.hlayout = QHBoxLayout()
        self.layout.addLayout(self.hlayout)

        self.setup_show_image_area()
        self.setup_filters()


    def setup_filters(self):
        formlayout = QFormLayout()
        self.hlayout.addLayout(formlayout)
        self.filter_lab = QLabel('格式筛选：')
        self.filter_line_edit = FLineEdit(place_holder_text='使用英文逗号分隔图片格式')
        self.filter_line_edit.setText('png,jpg,jpeg,bmp,tif,tiff,webp,tga')
        formlayout.addRow(self.filter_lab, self.filter_line_edit)
        # layout.addWidget(self.filter_line_edit)

    def setup_image_list_view(self):
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def setup_show_image_area(self):
        self.image_show_label = QLabel()
        self.image_show_label.setMinimumWidth(540)
        self.image_show_label.setMinimumHeight(360)
        self.hlayout.addWidget(self.image_show_label)

    def get_image_list(self):
        input_path = Path(self.input_line_edit.text().strip())
        try:
            self.list_widget.clear()
            extension_list = [extension.strip().lower() for extension in self.filter_line_edit.text().split(',')]
            extension_list_ = []
            for extension in extension_list:
                if extension not in extension_list_:
                    extension_list_.append(extension)
            image_list = []
            for extension in extension_list_:
                image_list += input_path.file_list(extension)
            for image_file in image_list:
                self.list_widget.addItem(image_file.to_str)
        except:
            self.list_widget.clear()
            raise ValueError('获取列表失败！')

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

        self.input_lb = QLabel('输入路径：')
        self.input_line_edit = FLineEdit(place_holder_text='将图片文件或文件夹拖拽至此处', height=30, radius=12, text_padding=10)
        layout1.addWidget(self.input_lb)
        layout1.addWidget(self.input_line_edit)
        self.input_line_edit.dropEvent = self.drop_get_list

        layout2 = QHBoxLayout()
        self.layout.addLayout(layout2)
        self.output_lb = QLabel('输出目录：')
        self.output_line_edit = FLineEdit(place_holder_text='输出图片至此处', height=30, radius=12, text_padding=10)
        layout2.addWidget(self.output_lb)
        layout2.addWidget(self.output_line_edit)

    def drop_get_list(self, event):
        file_path = Path(event.mimeData().text().replace('file:///', '').strip())
        self.input_line_edit.setText(str(file_path))
        self.get_image_list()
        event.accept()

    def add_shadow(self, target_widget):
        shadow = QGraphicsDropShadowEffect(target_widget)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 200))
        target_widget.setGraphicsEffect(shadow)
