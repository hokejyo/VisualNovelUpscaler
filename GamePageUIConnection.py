# -*- coding: utf-8 -*-

from Core import *
from GUI import *
from VNEngines import *


class GamePageUIConnection(object):

    def __init__(self):
        self.ui_game_page_connections()

    def ui_game_page_connections(self):
        self.ui.gamepage.kirikiri.check_resolution_btn.clicked.connect(self.kirikiri_check_resolution)
        self.ui.gamepage.artemis.check_resolution_btn.clicked.connect(self.artemis_check_resolution)
        self.ui.gamepage.run_btn.clicked.connect(self.game_page_run)

    def _check_game_page_in_out_folder(self, only_folder=True, check_output=True) -> bool:
        warn_message = None
        if not self.input_folder.exists():
            warn_message = '输入路径不存在!'
        if self.input_folder == Path('./'):
            warn_message = '输入路径不能与工作目录相同!'
        if only_folder:
            if not self.input_folder.is_dir():
                warn_message = '输入路径需要是文件夹!'
        if check_output:
            if self.output_folder == Path('./'):
                warn_message = '输出路径不能与工作目录相同!'
            if self.input_folder == self.output_folder:
                warn_message = '输入路径和输出路径不能相同!'
        if warn_message is not None:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', warn_message, QMessageBox.Yes)
            return False
        else:
            if check_output:
                if not self.output_folder.exists():
                    self.output_folder.mkdir(parents=True)
            return True

    def _check_game_page_path_access(self):
        # Kirikiri
        if self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.kirikiri:
            # 给ui起个别名
            ugk = self.ui.gamepage.kirikiri
            # 高清重制
            if ugk.currentWidget() is ugk.hd_parts_frame:
                return self._check_game_page_in_out_folder()
            # 后处理
            elif ugk.currentWidget() is ugk.work_up_frame:
                if ugk.stand_crt_btn.isChecked():
                    return self._check_game_page_in_out_folder()
                # tlg图片格式转换
                elif ugk.tlg_convert_btn.isChecked():
                    return self._check_game_page_in_out_folder(only_folder=False)
                # pimg格式转换
                elif ugk.pimg_cvt_btn.isChecked():
                    return self._check_game_page_in_out_folder(only_folder=False)
                # amv动画格式转换
                elif ugk.amv_cvt_btn.isChecked():
                    return self._check_game_page_in_out_folder()
                # 补丁文件平铺
                elif ugk.flat_patch_btn.isChecked():
                    return self._check_game_page_in_out_folder()
        # Artemis
        elif self.ui.gamepage.game_engine_area.currentWidget() is self.ui.gamepage.artemis:
            # 给ui起个别名
            uga = self.ui.gamepage.artemis
            # 高清重制
            if uga.currentWidget() is uga.hd_parts_frame:
                return self._check_game_page_in_out_folder()
            # 后处理
            elif uga.currentWidget() is uga.work_up_frame:
                # 拆包
                if uga.pfs_unpack_btn.isChecked():
                    return self._check_game_page_in_out_folder(only_folder=False)

    def game_page_run(self):
        self.input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip())
        self.output_folder = Path(self.ui.gamepage.select_output_folder_line_edit.text().strip())
        if self._check_game_page_path_access():
            self.game_page_runner = GamePageRunner(self)
            # pyside6信号需要通过实例绑定
            self.game_page_runner.start_sig.connect(self.start_game_page_runner_and_lock)
            self.game_page_runner.info_sig.connect(self.append_game_info_text_edit)
            self.game_page_runner.progress_sig.connect(self.update_game_progress_bar)
            self.game_page_runner.finish_sig.connect(self.finish_game_page_runner_and_unlock)
            self.game_page_runner.crash_sig.connect(self.crash_game_page_runner_and_unlock)
            self.game_page_runner.start()

    def start_game_page_runner_and_lock(self):
        # 开始时锁定，防止重复操作
        self.ui.gamepage.set_running_state(1)
        # 清空历史信息
        self.ui.gamepage.info_text_edit.clear()
        self.emit_info(format('开始处理', '=^76'))
        self.ui.gamepage.info_text_edit.append(format('开始处理', '=^76'))

    def append_game_info_text_edit(self, info_str):
        self.ui.gamepage.info_text_edit.append(info_str)

    def update_game_progress_bar(self, _percent, _left_time):
        self.ui.gamepage.set_running_state(2)
        self.ui.gamepage.status_progress_bar.setValue(_percent)
        left_time_str = seconds_format(_left_time)
        self.ui.gamepage.run_btn.setText(left_time_str)
        if _percent == 100:
            self.ui.gamepage.set_running_state(1)

    def finish_game_page_runner_and_unlock(self, info_str=''):
        self.ui.gamepage.set_running_state(3)
        self.emit_info(format('结束处理', '=^76'))
        self.ui.gamepage.info_text_edit.append(format('结束处理', '=^76'))
        finish_info_msg = QMessageBox()
        reply = finish_info_msg.information(self.ui, '处理完成', f'{info_str}\n是否打开输出文件夹?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        show_folder(self.output_folder) if reply == QMessageBox.Yes else None

    def crash_game_page_runner_and_unlock(self, info_str):
        self.ui.gamepage.set_running_state(0)
        self.emit_info(format('中断处理', '=^76'))
        self.ui.gamepage.info_text_edit.append(format('中断处理', '=^76'))
        raise Exception(info_str)

    def kirikiri_check_resolution(self):
        input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip())
        try:
            _kirikiri = Kirikiri()
            scwidth, scheight, encoding = _kirikiri.get_resolution_encoding(input_folder)
            self.ui.gamepage.kirikiri.set_game_resolution_encoding(scwidth, scheight, encoding)
        except:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', '未能找到游戏分辨率和主要编码格式!', QMessageBox.Yes)

    def artemis_check_resolution(self):
        input_folder = Path(self.ui.gamepage.select_input_folder_line_edit.text().strip())
        try:
            _artemis = Artemis()
            scwidth, scheight, encoding = _artemis.get_resolution_encoding(input_folder)
            self.ui.gamepage.artemis.set_game_resolution_encoding(scwidth, scheight, encoding)
        except:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', '未能找到游戏分辨率和主要编码格式!', QMessageBox.Yes)


class GamePageRunner(QThread):
    """用于处理高清重制等耗时任务"""

    # 开始信号
    start_sig = Signal()
    # 信息文本框
    info_sig = Signal(str)
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
            # Kirikiri
            if self.vnu.ui.gamepage.game_engine_area.currentWidget() is self.vnu.ui.gamepage.kirikiri:
                self.kirikiri_run()
            # Artemis
            elif self.vnu.ui.gamepage.game_engine_area.currentWidget() is self.vnu.ui.gamepage.artemis:
                self.artemis_run()
        except Exception as e:
            self.crash_sig.emit(traceback.format_exc())

    def kirikiri_run(self):
        kirikiri = Kirikiri(self)
        # 给ui起个别名
        ugk = self.vnu.ui.gamepage.kirikiri
        if ugk.currentWidget() is ugk.hd_parts_frame:
            # 设置输入、输出路径
            kirikiri.set_vn_hd_io_folder(self.vnu.input_folder, self.vnu.output_folder)
            # 设置原生分辨率和主要编码
            scwidth, scheight = map(int, ugk.before_resolution.text().split('x'))
            encoding = ugk.main_encoding.text()
            kirikiri.set_resolution_encoding(scwidth, scheight, encoding)
            # 设置放大倍率
            kirikiri.scale_ratio = ugk.custiom_ratio_spinbox.value()
            # 设置放大部分
            kirikiri.run_dict['script'] = ugk.text_part.isChecked()
            kirikiri.run_dict['image'] = ugk.image_part.isChecked()
            kirikiri.run_dict['animation'] = ugk.animation_part.isChecked()
            kirikiri.run_dict['video'] = ugk.video_part.isChecked()
            # 设置是否保存目录结构
            kirikiri.keep_path_struct_mode = ugk.keep_mode_btn.isChecked()
            # 开始放大
            kirikiri.upscale()
            self.finish_sig.emit('高清重制完成!')
        elif ugk.currentWidget() is ugk.work_up_frame:
            # 对话框头像坐标调整
            if ugk.stand_crt_btn.isChecked():
                face_zoom = ugk.crt_ratio.value()
                xpos_move = ugk.crt_movex.value()
                kirikiri.stand_correction(self.vnu.input_folder, self.vnu.output_folder, face_zoom, xpos_move)
                self.finish_sig.emit('对话框头像坐标调整完成!')
            # tlg图片格式转换
            elif ugk.tlg_convert_btn.isChecked():
                input_format = ugk.tlg_in.currentText()
                output_format = ugk.tlg_out.currentText()
                if input_format == 'tlg':
                    if output_format == 'png':
                        kirikiri.tlg2png_batch(self.vnu.input_folder, self.vnu.output_folder)
                    else:
                        tlg5_mode = False if output_format == 'tlg6' else True
                        kirikiri.tlg2tlg_batch(self.vnu.input_folder, self.vnu.output_folder, tlg5_mode)
                elif input_format == 'png':
                    tlg5_mode = False if output_format == 'tlg6' else True
                    kirikiri.png2tlg_batch(self.vnu.input_folder, self.vnu.output_folder, tlg5_mode)
                self.finish_sig.emit('tlg图片转换完成!')
            # pimg格式转换
            elif ugk.pimg_cvt_btn.isChecked():
                input_format = ugk.pimg_in.currentText()
                output_format = ugk.pimg_out.currentText()
                if input_format == 'pimg':
                    kirikiri.pimg_de_batch(self.vnu.input_folder, self.vnu.output_folder)
                elif input_format == 'json&png':
                    kirikiri.pimg_en_batch(self.vnu.input_folder, self.vnu.output_folder)
                self.finish_sig.emit('pimg转换完成!')
            # amv动画格式转换
            elif ugk.amv_cvt_btn.isChecked():
                input_format = ugk.amv_in.currentText()
                output_format = ugk.amv_out.currentText()
                if input_format == 'amv' and output_format == 'json&png':
                    kirikiri.amv2png(self.vnu.input_folder, self.vnu.output_folder)
                elif input_format == 'json&png' and output_format == 'amv':
                    kirikiri.png2amv(self.vnu.input_folder, self.vnu.output_folder)
                self.finish_sig.emit('amv转换完成!')
            elif ugk.flat_patch_btn.isChecked():
                kirikiri.flat_kirikiri_patch_folder(self.vnu.input_folder, self.vnu.output_folder)
                self.finish_sig.emit('补丁文件平铺完成!')

    def artemis_run(self):
        artemis = Artemis(self)
        # 给ui起个别名
        uga = self.vnu.ui.gamepage.artemis
        if uga.currentWidget() is uga.hd_parts_frame:
            # 设置输入、输出路径
            artemis.set_vn_hd_io_folder(self.vnu.input_folder, self.vnu.output_folder)
            # 设置原生分辨率和主要编码
            scwidth, scheight = map(int, uga.before_resolution.text().split('x'))
            encoding = uga.main_encoding.text()
            artemis.set_resolution_encoding(scwidth, scheight, encoding)
            # 设置放大倍率
            artemis.scale_ratio = uga.custiom_ratio_spinbox.value()
            # 设置放大部分
            artemis.run_dict['script'] = uga.text_part.isChecked()
            artemis.run_dict['image'] = uga.image_part.isChecked()
            artemis.run_dict['animation'] = uga.animation_part.isChecked()
            artemis.run_dict['video'] = uga.video_part.isChecked()
            artemis.upscale()
            self.finish_sig.emit('高清重制完成!')
        elif uga.currentWidget() is uga.work_up_frame:
            if uga.pfs_unpack_btn.isChecked():
                pfs_encoding = uga.pfs_encoding_line_edit.text().strip()
                artemis.batch_extract_pfs(self.vnu.input_folder, self.vnu.output_folder, pfs_encoding)
                self.finish_sig.emit(f'拆包完成!\n请把游戏目录中类似script、movie等文件夹及*.ini文件也复制到：\n{self.vnu.output_folder}中')
