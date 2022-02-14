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
        self.ui.gamepage.run_btn.clicked.connect(self.game_page_run)

    def game_page_run(self):
        self.input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip()).resolve()
        self.output_folder = Path(self.ui.gamepage.select_output_folder_line_edit.text().strip()).resolve()
        if self.input_folder.exists() and self.input_folder.is_dir() and self.input_folder != Path('./').resolve():
            if not self.output_folder.exists():
                self.output_folder.mkdir(parents=True)
            # # Kirikiri
            # if self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.kirikiri:
            #     self.kirikiri_run()
            # # Artemis
            # elif self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.artemis:
            #     self.artemis_run()

            self.game_page_runner = GamePageRunner(self)
            # 开始时锁定，防止重复操作
            self.game_page_runner.start_sig.connect(self.start_game_page_runner)
            self.game_page_runner.start()
        else:
            path_warn_msg = QMessageBox()
            reply = path_warn_msg.warning(self.ui, '输入路径错误', '输入路径必须是文件夹！', QMessageBox.Yes)

    def start_game_page_runner(self):
        start_info_msg = QMessageBox()
        reply = start_info_msg.information(self.ui, '开始处理中', '请耐心等待，切勿重复操作！', QMessageBox.Yes)

    # def game_page_run_behaviour(self):
    #     self.input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip()).resolve()
    #     self.output_folder = Path(self.ui.gamepage.select_output_folder_line_edit.text().strip()).resolve()
    #     if self.input_folder.exists() and self.input_folder.is_dir() and self.input_folder != Path('./').resolve():
    #         # Kirikiri
    #         if self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.kirikiri:
    #             self.kirikiri_run()
    #         # Artemis
    #         elif self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.artemis:
    #             self.artemis_run()
    #     else:
    #         tip_msg = QMessageBox()
    #         reply = tip_msg.warning(self.ui, '输入路径错误', '输入路径必须是文件夹！', QMessageBox.Yes)

    # def kirikiri_run(self):
    #     # 给ui起个别名
    #     ugk = self.ui.gamepage.kirikiri
    #     if ugk.currentWidget() is ugk.hd_parts_frame:
    #         # 设置放大部分
    #         run_dict = {}
    #         run_dict['script'] = ugk.text_part.isChecked()
    #         run_dict['ui'] = ugk.ui_part.isChecked()
    #         run_dict['image'] = ugk.image_part.isChecked()
    #         run_dict['animation'] = ugk.animation_part.isChecked()
    #         run_dict['video'] = ugk.video_part.isChecked()

    #         kirikiri_upscaler = KirikiriUpscaler(self.input_folder,self.output_folder,run_dict)
    #         kirikiri_upscaler.strat()

        # # 设置输入、输出路径及放大倍率
        # kirikiri.set_game_data(self.input_folder)
        # kirikiri.patch_folder = self.output_folder
        # kirikiri.scale_ratio = ugk.custiom_ratio_spinbox.value()
        # # 设置放大部分
        # kirikiri.run_dict['script'] = ugk.text_part.isChecked()
        # kirikiri.run_dict['ui'] = ugk.ui_part.isChecked()
        # kirikiri.run_dict['image'] = ugk.image_part.isChecked()
        # kirikiri.run_dict['animation'] = ugk.animation_part.isChecked()
        # kirikiri.run_dict['video'] = ugk.video_part.isChecked()
        # kirikiri.upscale()
        # elif ugk.currentWidget() is ugk.work_up_frame:
        #     pass
    # def artemis_run(self):
    #     artemis = Artemis()
    #     # 给ui起个别名
    #     uga = self.ui.gamepage.artemis
    #     if uga.currentWidget() is uga.hd_parts_frame:
    #         # 设置输入、输出路径及放大倍率
    #         artemis.set_game_data(self.input_folder)
    #         artemis.patch_folder = self.output_folder
    #         artemis.scale_ratio = uga.custiom_ratio_spinbox.value()
    #         # 设置放大部分
    #         artemis.run_dict['script'] = uga.text_part.isChecked()
    #         artemis.run_dict['image'] = uga.image_part.isChecked()
    #         artemis.run_dict['animation'] = uga.animation_part.isChecked()
    #         artemis.run_dict['video'] = uga.video_part.isChecked()
    #         artemis.upscale()
    #     elif uga.currentWidget() is uga.work_up_frame:
    #         pass


if __name__ == '__main__':
    # 防止打包运行后多进程内存泄漏
    freeze_support()
    # 防止打包运行后工作路径改变，pyinstaller坑真多
    bundle_dir = Path(sys.argv[0]).resolve().parent
    os.chdir(bundle_dir)
    vnc_log_file = bundle_dir/'log.txt'
    # 启动
    app = QApplication(sys.argv)
    visual_novel_clearer = VisualNovelClearer()
    visual_novel_clearer.ui.show()
    sys.exit(app.exec())
