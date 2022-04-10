# -*- coding: utf-8 -*-

from Core import *
from GUI import *


class ImagePageUIConnection(object):

    def __init__(self):
        self.ui.imagepage.run_btn.clicked.connect(self.image_page_run)

    def image_page_run(self):
        self.input_path = Path(self.ui.imagepage.input_line_edit.text().strip())
        self.output_folder = Path(self.ui.imagepage.output_line_edit.text().strip())
        if self.check_image_in_out_folder(self.input_path, self.output_folder):
            self.image_page_runner = ImagePageRunner(self)
            # 信号绑定
            self.image_page_runner.start_sig.connect(self.start_image_page_runner_and_lock)
            self.image_page_runner.progress_sig.connect(self.update_image_progress_bar)
            self.image_page_runner.finish_sig.connect(self.finish_image_page_runner_and_unlock)
            self.image_page_runner.crash_sig.connect(self.crash_image_page_runner_and_unlock)
            self.image_page_runner.start()

    def check_image_in_out_folder(self, input_path, output_folder) -> bool:
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        warn_message = None
        if not input_path.exists():
            warn_message = '输入路径不存在'
        if input_path == Path('./'):
            warn_message = '输入路径不能与工作目录相同'
        if output_folder == Path('./'):
            warn_message = '输出路径不能与工作目录相同'
        if warn_message is not None:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', warn_message + '!', QMessageBox.Yes)
            return False
        else:
            if not output_folder.exists():
                output_folder.mkdir(parents=True)
            return True

    def start_image_page_runner_and_lock(self):
        # 开始时锁定，防止重复操作
        self.ui.imagepage.set_running_state(1)
        # 清空历史信息
        self.emit_info(format('开始处理', '=^76'))

    def update_image_progress_bar(self, _percent, _left_time):
        self.ui.imagepage.status_progress_bar.setValue(_percent)
        left_time_str = seconds_format(_left_time)
        self.ui.imagepage.run_btn.setText(left_time_str)
        if _percent == 100:
            self.ui.imagepage.set_running_state(1)

    def finish_image_page_runner_and_unlock(self, info_str=''):
        self.ui.imagepage.set_running_state(2)
        self.emit_info(format('结束处理', '=^76'))
        finish_info_msg = QMessageBox()
        reply = finish_info_msg.information(self.ui, '处理完成', f'{info_str}\n是否打开输出文件夹?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        os.system(f'start {self.output_folder}') if reply == QMessageBox.Yes else None

    def crash_image_page_runner_and_unlock(self, info_str):
        self.ui.imagepage.set_running_state(0)
        self.emit_info(format('中断处理', '=^76'))
        raise Exception(info_str)


class ImagePageRunner(QThread):

    # 开始信号
    start_sig = Signal()
    # 进度(0-100)
    progress_sig = Signal(int, int)
    # 结束弹窗信息
    finish_sig = Signal(str)
    # 崩溃错误信息
    crash_sig = Signal(str)

    def __init__(self, vnu):
        QThread.__init__(self)
        self.vnu = vnu

    def run(self):
        self.start_sig.emit()
        try:
            image_upscaler = ImageUpscaler(self)
            input_path = self.vnu.input_path
            output_folder = self.vnu.output_folder
            scale_ratio = float(self.vnu.ui.imagepage.custiom_ratio_spinbox.value())
            output_extention = self.vnu.ui.imagepage.output_extention_line_edit.text().strip().lower()
            filters = [extension.strip().lower() for extension in self.vnu.ui.imagepage.filter_line_edit.text().split(',')]
            walk_mode = True if self.vnu.ui.imagepage.ignr_btn.isChecked() else False
            stem_sfx = self.vnu.ui.imagepage.suffix_line_edit.text().strip()
            rename_sfx = None if stem_sfx == '' else stem_sfx
            image_upscaler.image_upscale(input_path=input_path,
                                         output_folder=output_folder,
                                         scale_ratio=scale_ratio,
                                         output_extention=output_extention,
                                         filters=filters,
                                         walk_mode=walk_mode,
                                         rename_sfx=rename_sfx
                                         )
            self.finish_sig.emit('图片放大完成!')
        except Exception as e:
            self.crash_sig.emit(traceback.format_exc())


class ImageUpscaler(Core):

    def __init__(self, image_ui_runner):
        Core.__init__(self)
        self.load_config()
        self.__class__.image_ui_runner = image_ui_runner

    def emit_progress(self, _percent, _left_time):
        print(_percent, _left_time, sep='\t')
        self.image_ui_runner.progress_sig.emit(_percent, _left_time)
