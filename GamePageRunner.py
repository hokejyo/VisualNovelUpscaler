# -*- coding: utf-8 -*-

from Core import *
from VNEngines import *
from GUI import *


class GamePageRunner(QThread):
    """用于处理高清重制等耗时任务"""

    start_sig = Signal()
    # (进度名称，进度0-100)
    working_sig = Signal(str, int)
    # 结束弹窗信息
    finish_sig = Signal(str)

    def __init__(self, vnc):
        QThread.__init__(self)
        self.vnc = vnc
        print('开始')

    def run(self):
        self.start_sig.emit()
        # Kirikiri
        if self.vnc.ui.gamepage.game_engine_area.currentWidget() is self.vnc.ui.gamepage.kirikiri:
            self.kirikiri_run()
        # Artemis
        elif self.vnc.ui.gamepage.game_engine_area.currentWidget() is self.vnc.ui.gamepage.artemis:
            self.artemis_run()
            self.finish_sig.emit()

    def kirikiri_run(self):
        kirikiri = Kirikiri()
        # 给ui起个别名
        ugk = self.vnc.ui.gamepage.kirikiri
        if ugk.currentWidget() is ugk.hd_parts_frame:
            # 设置输入、输出路径及放大倍率
            kirikiri.set_game_data(self.vnc.input_folder)
            kirikiri.patch_folder = self.vnc.output_folder
            kirikiri.scale_ratio = ugk.custiom_ratio_spinbox.value()
            # 设置放大部分
            kirikiri.run_dict['script'] = ugk.text_part.isChecked()
            kirikiri.run_dict['image'] = ugk.image_part.isChecked()
            kirikiri.run_dict['animation'] = ugk.animation_part.isChecked()
            kirikiri.run_dict['video'] = ugk.video_part.isChecked()
            kirikiri.upscale()
        elif ugk.currentWidget() is ugk.work_up_frame:
            if ugk.stand_crt_btn.isChecked():
                face_zoom = self.crt_ratio.value()
                xpos_move = self.crt_movex.value()
                kirikiri.stand_correction(self.vnc.input_folder, self.vnc.output_folder, face_zoom, xpos_move)
            elif ugk.amv_cvt_btn.isChecked():
                input_format = ugk.amv_in.currentText()
                output_format = ugk.amv_out.currentText()
                if input_format == 'amv' and output_format == 'png':
                    kirikiri.amv2png(self.vnc.input_folder, self.vnc.output_folder)
                    self.finish_sig.emit('amv转换完成!')
            elif ugk.tlg_convert_btn.isChecked():
                input_format = ugk.tlg_in.currentText()
                output_format = ugk.tlg_out.currentText()

    def artemis_run(self):
        artemis = Artemis()
        # 给ui起个别名
        uga = self.vnc.ui.gamepage.artemis
        if uga.currentWidget() is uga.hd_parts_frame:
            # 设置输入、输出路径及放大倍率
            artemis.set_game_data(self.input_folder)
            artemis.patch_folder = self.output_folder
            artemis.scale_ratio = uga.custiom_ratio_spinbox.value()
            # 设置放大部分
            artemis.run_dict['script'] = uga.text_part.isChecked()
            artemis.run_dict['image'] = uga.image_part.isChecked()
            artemis.run_dict['animation'] = uga.animation_part.isChecked()
            artemis.run_dict['video'] = uga.video_part.isChecked()
            artemis.upscale()
        elif uga.currentWidget() is uga.work_up_frame:
            pass
