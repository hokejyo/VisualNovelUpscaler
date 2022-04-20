# -*- coding: utf-8 -*-

from Core import *


class Majiro(Core):
    """Majiro Script Engine"""

    def __init__(self, game_ui_runner=None):
        Core.__init__(self)
        self.load_config()
        self.__class__.game_ui_runner = game_ui_runner
        self.encoding = 'Shift_JIS'
        self.run_dict = {'script': False, 'image': False, 'video': False}

    def emit_info(self, info_str):
        print(info_str)
        logging.info(info_str)
        if self.game_ui_runner is not None:
            self.game_ui_runner.info_sig.emit(info_str)

    def emit_progress(self, _percent, _left_time):
        print(_percent, _left_time, sep='\t')
        if self.game_ui_runner is not None:
            self.game_ui_runner.progress_sig.emit(_percent, _left_time)

    def upscale(self):
        # 计时
        start_time = time.time()
        # 创建补丁文件夹
        if not self.patch_folder.exists():
            self.patch_folder.mkdir(parents=True)
        # 开始放大
        if self.run_dict['script']:
            self._script2x()
            self.emit_info('文本文件处理完成')
        if self.run_dict['image']:
            self._image2x()
            self.emit_info('图片文件放大完成')
        if self.run_dict['video']:
            self._video2x()
            self.emit_info('视频文件处理完成')
        # 结束
        timing_count = time.time() - start_time
        self.emit_info(f'共耗时：{seconds_format(timing_count)}')

    """
    ==================================================
    Majiro引擎脚本文件：mjo, cfg, env, winmerge, csv
    ==================================================
    """

    def _script2x(self):
        pass

    def mjo_de_batch(self, input_path, output_folder) -> list:
        """
        @brief      拆分mjo

        @param      input_path     The input path
        @param      output_folder  The output folder

        @return     拆分出的mjil文件路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        mjo_out_path_dict = {}
        if input_path.is_file():
            out_dir = input_path.reio_path(input_path.parent, output_folder, mk_dir=True).parent
            mjo_out_path_dict[input_path] = out_dir
        else:
            mjo_file_ls = input_path.file_list('mjo')
            for mjo_file in mjo_file_ls:
                out_dir = mjo_file.reio_path(input_path, output_folder, mk_dir=True).parent
                mjo_out_path_dict[mjo_file] = out_dir
        out_mjil_file_ls = self.pool_run(self._mjo_de, mjo_out_path_dict.items())
        return out_mjil_file_ls

    def _mjo_de(self, mjo_out_path) -> Path:
        mjo_file, out_dir = mjo_out_path
        with tempfile.TemporaryDirectory() as mjo_de_tmp_folder:
            mjo_de_tmp_folder = Path(mjo_de_tmp_folder)
            tmp_mjo_file = mjo_file.copy_to(mjo_de_tmp_folder)
            mjo_de_p = subprocess.run([self.mjotool_exe, 'disassemble', tmp_mjo_file], capture_output=True, shell=True)
            tmp_mjil_file = tmp_mjo_file.with_suffix('.mjil')
            tmp_mjres_file = tmp_mjo_file.with_suffix('.mjres')
            mjil_file = tmp_mjil_file.move_to(out_dir)
            if tmp_mjres_file.exists():
                mjres_file = tmp_mjres_file.move_to(out_dir)
            return mjil_file

    def mjo_en_batch(self, input_path, output_folder) -> list:
        """
        @brief      组合mjo，需要有mjres文件

        @param      input_path   The input dir
        @param      output_folder  The output dir

        @return     mjo path list
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        mjil_out_path_dict = {}
        if input_path.is_file():
            out_dir = input_path.reio_path(input_path.parent, output_folder, mk_dir=True).parent
            mjil_out_path_dict[input_path] = out_dir
        else:
            mjil_file_ls = input_path.file_list('mjil')
            for mjil_file in mjil_file_ls:
                out_dir = mjil_file.reio_path(input_path, output_folder, mk_dir=True).parent
                mjil_out_path_dict[mjil_file] = out_dir
        out_mjo_file_ls = self.pool_run(self._mjo_en, mjil_out_path_dict.items())
        return out_mjo_file_ls

    def _mjo_en(self, mjil_out_path) -> Path:
        mjil_file, out_dir = mjil_out_path
        mjres_file = mjil_file.with_suffix('.mjres')
        with tempfile.TemporaryDirectory() as mjo_en_tmp_folder:
            mjo_en_tmp_folder = Path(mjo_en_tmp_folder)
            tmp_mjil_file = mjil_file.copy_to(mjo_en_tmp_folder)
            if mjres_file.exists():
                tmp_mjres_file = mjres_file.copy_to(mjo_en_tmp_folder)
            mjo_en_p = subprocess.run([self.mjotool_exe, 'assemble', tmp_mjil_file], capture_output=True, shell=True)
            tmp_mjo_file = tmp_mjil_file.with_suffix('.mjo')
            mjo_file = tmp_mjo_file.move_to(out_dir)
            return mjo_file

    """
    ==================================================
    Majiro引擎图片文件：png, bmp, jpg, rct, rc8
    ==================================================
    """

    def _image2x(self):
        pass

    """
    ==================================================
    Majiro引擎视频文件：wmv(WMV3), mpg(MPEG1、MPEG2)
    ==================================================
    """

    def _video2x(self):
        pass
