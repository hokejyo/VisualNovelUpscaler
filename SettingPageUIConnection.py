# -*- coding: utf-8 -*-

from Core import *
from GUI import *


class SettingPageUIConnection(object):

    def __init__(self):
        self.ui_setting_connections()
        self.ui_config_load()

    def ui_setting_connections(self):
        # 配置页面应用
        self.ui.settingpage.save_btn.clicked.connect(self.ui_config_save)
        # 配置页面取消
        self.ui.settingpage.cancle_btn.clicked.connect(self.ui_config_load)
        # 配置页面重置
        self.ui.settingpage.reset_btn.clicked.connect(self.ui_config_reset)

    def ui_config_load(self):
        # 载入配置文件
        try:
            self.load_config()
        except:
            config_reset_message = QMessageBox()
            reply = config_reset_message.question(self.ui, '配置文件未正确配置', '是否重置配置文件？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            sys.exit() if reply == QMessageBox.No else self.reset_config()
        # cpu核数
        self.ui.settingpage.cpu_spinbox.setValue(self.cpu_cores)
        # 显卡型号
        self.ui.settingpage.gpu_combobox.setCurrentIndex(int(self.gpu_id))
        # 文本编码列表
        self.ui.settingpage.text_encoding_line_edit.setText(','.join(self.encoding_list))
        # 超分引擎
        self.ui.settingpage.image_sr_engine_combobox.setCurrentText(self.image_sr_engine)
        self.ui.settingpage.video_sr_engine_combobox.setCurrentText(self.video_sr_engine)
        tta_bool = False if self.tta == '0' else True
        self.ui.settingpage.tta_checkbox.setChecked(tta_bool)
        # self.ui.settingpage.sr_engine_combobox.setCurrentText('real_cugan')
        # waifu2x_ncnn
        self.ui.settingpage.waifu2x_ncnn_settings.noise_level_spinbox.setValue(int(self.waifu2x_ncnn_noise_level))
        self.ui.settingpage.waifu2x_ncnn_settings.tile_size_line_edit.setText(self.waifu2x_ncnn_tile_size)
        self.ui.settingpage.waifu2x_ncnn_settings.modle_name_combobox.setCurrentText(self.waifu2x_ncnn_model_name)
        self.ui.settingpage.waifu2x_ncnn_settings.load_proc_save_line_edit.setText(self.waifu2x_ncnn_load_proc_save)
        # real_cugan
        self.ui.settingpage.real_cugan_settings.noise_level_spinbox.setValue(int(self.real_cugan_noise_level))
        self.ui.settingpage.real_cugan_settings.tile_size_line_edit.setText(self.real_cugan_tile_size)
        self.ui.settingpage.real_cugan_settings.sync_gap_mode_spinbox.setValue(int(self.real_cugan_sync_gap_mode))
        self.ui.settingpage.real_cugan_settings.modle_name_combobox.setCurrentText(self.real_cugan_model_name)
        self.ui.settingpage.real_cugan_settings.load_proc_save_line_edit.setText(self.real_cugan_load_proc_save)
        # real_esrgan
        self.ui.settingpage.real_esrgan_settings.tile_size_line_edit.setText(self.real_esrgan_tile_size)
        self.ui.settingpage.real_esrgan_settings.modle_name_combobox.setCurrentText(self.real_esrgan_model_name)
        self.ui.settingpage.real_esrgan_settings.load_proc_save_line_edit.setText(self.real_esrgan_load_proc_save)
        # srmd_ncnn
        self.ui.settingpage.srmd_ncnn_settings.noise_level_spinbox.setValue(int(self.srmd_ncnn_noise_level))
        self.ui.settingpage.srmd_ncnn_settings.tile_size_line_edit.setText(self.srmd_ncnn_tile_size)
        self.ui.settingpage.srmd_ncnn_settings.load_proc_save_line_edit.setText(self.srmd_ncnn_load_proc_save)
        # realsr_ncnn
        self.ui.settingpage.realsr_ncnn_settings.tile_size_line_edit.setText(self.realsr_ncnn_tile_size)
        self.ui.settingpage.realsr_ncnn_settings.modle_name_combobox.setCurrentText(self.realsr_ncnn_model_name)
        self.ui.settingpage.realsr_ncnn_settings.load_proc_save_line_edit.setText(self.realsr_ncnn_load_proc_save)
        # anime4kcpp
        acnet_bool = False if self.anime4k_acnet == '0' else True
        self.ui.settingpage.anime4k_settings.acnet_checkbox.setChecked(acnet_bool)
        # 视频设置
        self.ui.settingpage.video_quality_spinbox.setValue(int(self.video_quality))

    def ui_config_save(self):
        with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
            # 通用设置
            self.vnc_config.set('General', 'cpu_cores', str(self.ui.settingpage.cpu_spinbox.value()))
            self.vnc_config.set('General', 'gpu_id', get_gpu_id(self.ui.settingpage.gpu_combobox.currentText()))
            self.vnc_config.set('General', 'encoding_list', self.ui.settingpage.text_encoding_line_edit.text())
            # 超分引擎
            self.vnc_config.set('General', 'image_sr_engine', self.ui.settingpage.image_sr_engine_combobox.currentText())
            self.vnc_config.set('General', 'video_sr_engine', self.ui.settingpage.video_sr_engine_combobox.currentText())
            tta = '1' if self.ui.settingpage.tta_checkbox.isChecked() else '0'
            self.vnc_config.set('General', 'tta', tta)
            # waifu2x_ncnn
            self.vnc_config.set('waifu2x_ncnn', 'noise_level', str(self.ui.settingpage.waifu2x_ncnn_settings.noise_level_spinbox.value()))
            self.vnc_config.set('waifu2x_ncnn', 'tile_size', self.ui.settingpage.waifu2x_ncnn_settings.tile_size_line_edit.text())
            self.vnc_config.set('waifu2x_ncnn', 'model_name', self.ui.settingpage.waifu2x_ncnn_settings.modle_name_combobox.currentText())
            self.vnc_config.set('waifu2x_ncnn', 'load_proc_save', self.ui.settingpage.waifu2x_ncnn_settings.load_proc_save_line_edit.text())
            # Real-CUGAN
            self.vnc_config.set('real_cugan', 'noise_level', str(self.ui.settingpage.real_cugan_settings.noise_level_spinbox.value()))
            self.vnc_config.set('real_cugan', 'tile_size', self.ui.settingpage.real_cugan_settings.tile_size_line_edit.text())
            self.vnc_config.set('real_cugan', 'sync_gap_mode', str(self.ui.settingpage.real_cugan_settings.sync_gap_mode_spinbox.value()))
            self.vnc_config.set('real_cugan', 'model_name', self.ui.settingpage.real_cugan_settings.modle_name_combobox.currentText())
            self.vnc_config.set('real_cugan', 'load_proc_save', self.ui.settingpage.real_cugan_settings.load_proc_save_line_edit.text())
            # real_esrgan
            self.vnc_config.set('real_esrgan', 'tile_size', self.ui.settingpage.real_esrgan_settings.tile_size_line_edit.text())
            self.vnc_config.set('real_esrgan', 'model_name', self.ui.settingpage.real_esrgan_settings.modle_name_combobox.currentText())
            self.vnc_config.set('real_esrgan', 'load_proc_save', self.ui.settingpage.real_esrgan_settings.load_proc_save_line_edit.text())
            # srmd_ncnn
            self.vnc_config.set('srmd_ncnn', 'noise_level', str(self.ui.settingpage.srmd_ncnn_settings.noise_level_spinbox.value()))
            self.vnc_config.set('srmd_ncnn', 'tile_size', self.ui.settingpage.srmd_ncnn_settings.tile_size_line_edit.text())
            self.vnc_config.set('srmd_ncnn', 'load_proc_save', self.ui.settingpage.srmd_ncnn_settings.load_proc_save_line_edit.text())
            # realsr_ncnn
            self.vnc_config.set('realsr_ncnn', 'tile_size', self.ui.settingpage.realsr_ncnn_settings.tile_size_line_edit.text())
            self.vnc_config.set('realsr_ncnn', 'model_name', self.ui.settingpage.realsr_ncnn_settings.modle_name_combobox.currentText())
            self.vnc_config.set('realsr_ncnn', 'load_proc_save', self.ui.settingpage.realsr_ncnn_settings.load_proc_save_line_edit.text())
            # anime4kcpp
            acnet = '1' if self.ui.settingpage.anime4k_settings.acnet_checkbox.isChecked() else '0'
            self.vnc_config.set('anime4k', 'acnet', acnet)
            # 视频设置
            self.vnc_config.set('ffmpeg', 'video_quality', str(self.ui.settingpage.video_quality_spinbox.value()))
            self.vnc_config.write(vcf)
        self.ui_config_load()

    def ui_config_reset(self):
        config_reset_message = QMessageBox()
        reply = config_reset_message.question(self.ui, '重置配置文件', '是否重置配置文件？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.reset_config()
            self.ui_config_load()
