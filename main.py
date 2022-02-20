# -*- coding: utf-8 -*-

from Core import *
from VNEngines import *
from GUI import *
from SettingPageUIConnection import SettingPageUIConnection
from GamePageRunner import GamePageRunner


class VisualNovelClearer(Core, SettingPageUIConnection):

    _version = 'v0.2.0'

    def __init__(self):
        Core.__init__(self)
        self.initUI()

    def initUI(self):
        self.ui = MainUI()
        self.ui.set_version(self._version)
        SettingPageUIConnection.__init__(self)
        self.ui_game_page_connections()

    def ui_game_page_connections(self):
        # self.ui.gamepage.select_input_folder_line_edit.textChanged.connect(self.check_input_game_engine)
        self.ui.gamepage.run_btn.clicked.connect(self.game_page_run)

    def game_page_run(self):
        self.input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip()).resolve()
        self.output_folder = Path(self.ui.gamepage.select_output_folder_line_edit.text().strip()).resolve()

        warn_message = None
        if not self.input_folder.exists():
            warn_message = '输入路径不存在'
        elif not self.input_folder.is_dir():
            warn_message = '输入路径需要是文件夹'
        elif self.input_folder == Path('./').resolve() or self.output_folder == Path('./').resolve():
            warn_message = '输入路径和输出路径不能与工作目录相同'
        elif self.input_folder == self.output_folder:
            warn_message = '输入路径和输出路径不能相同'
        elif (self.image_sr_engine == 'real_cugan' or self.video_sr_engine == 'real_cugan') and self.ui.gamepage.kirikiri.custiom_ratio_spinbox.value() > 4:
            warn_message = 'Real-Cugan仅支持4倍以下放大倍率'
        if warn_message:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', warn_message+'!', QMessageBox.Yes)
        else:
            if not self.output_folder.exists():
                self.output_folder.mkdir(parents=True)
            self.game_page_runner = GamePageRunner(self)
            # 信号绑定
            self.game_page_runner.start_sig.connect(self.start_game_page_runner_and_lock)
            self.game_page_runner.info_sig.connect(self.append_info_text_edit)
            self.game_page_runner.progress_sig.connect(self.update_progress_bar)
            self.game_page_runner.finish_sig.connect(self.finish_game_page_runner_and_open)
            self.game_page_runner.start()

    def start_game_page_runner_and_lock(self):
        # 开始时锁定，防止重复操作
        self.ui.gamepage.run_btn.setDisabled(True)
        # 清空历史信息
        self.ui.gamepage.info_text_edit.clear()
        self.ui.gamepage.run_btn.setText('正在处理')
        print('开始')

    def append_info_text_edit(self, info_str):
        self.ui.gamepage.info_text_edit.append(info_str)

    def update_progress_bar(self, int_value):
        self.ui.gamepage.status_progress_bar.setValue(int_value)

    def finish_game_page_runner_and_open(self, info_str=''):
        self.ui.gamepage.run_btn.setEnabled(True)
        self.ui.gamepage.run_btn.setText('开始处理')
        print('结束')
        finish_info_msg = QMessageBox()
        reply = finish_info_msg.information(self.ui, '处理完成', f'{info_str}\n是否打开输出文件夹?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        os.system(f'start {self.output_folder}') if reply == QMessageBox.Yes else None

    # def check_input_game_engine(self):
    #     pass

    # def lock_upscale_btn(self):
    #     ugp = self.ui.gamepage
    #     if ugp.game_engine_area.currentWidget is ugp.kirikiri:
    #         if ugp.kirikiri.currentWidget is ugp.kirikiri.hd_parts_frame:
    #             ugp.run_btn.setDisabled(True)
    #     else:
    #         ugp.run_btn.setEnabled(True)


if __name__ == '__main__':
    # 防止打包运行后多进程内存泄漏
    freeze_support()
    # 防止打包后拖拽运行工作路径改变
    bundle_dir = Path(sys.argv[0]).resolve().parent
    os.chdir(bundle_dir)
    # 错误日志
    vnc_log_file = bundle_dir/'log.txt'
    logging.basicConfig(filename=vnc_log_file, level=logging.DEBUG, filemode='a+', format='[%(asctime)s] [%(levelname)s] >>>  %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    # 启动
    # try:
    app = QApplication(sys.argv)
    visual_novel_clearer = VisualNovelClearer()
    visual_novel_clearer.ui.show()
    sys.exit(app.exec())
    # except Exception as e:
    #     logging.error(e)
    #     logging.error(traceback.format_exc())
    #     sys.exit()
