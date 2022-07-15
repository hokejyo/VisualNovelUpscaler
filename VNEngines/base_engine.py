# -*- coding: utf-8 -*-

from Core import *


class BaseEngine(Core):
    """
    @brief      其它游戏引擎的放大处理器需继承此类
    """

    def __init__(self, game_ui_runner=None):
        Core.__init__(self)
        self.load_config()
        self.__class__.game_ui_runner = game_ui_runner
        self.encoding = 'Shift_JIS'
        self.run_dict = {'script': False, 'image': False, 'animation': False, 'video': False}

    def emit_info(self, info_str):
        """
        @brief      输出信息到窗口

        @param      info_str  字符串信息
        """
        print(info_str)
        logging.info(info_str)
        if self.game_ui_runner is not None:
            self.game_ui_runner.info_sig.emit(info_str)

    def emit_progress(self, _percent, _left_time):
        """
        @brief      输出进度和剩余时间到进度条

        @param      _percent    进度(范围：0-100)
        @param      _left_time  剩余时间(单位：s)
        """
        print(_percent, _left_time, sep='\t')
        if self.game_ui_runner is not None:
            self.game_ui_runner.progress_sig.emit(_percent, _left_time)

    def a2p(self, file_path) -> Path:
        """
        @brief      游戏数据文件夹到补丁文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        return file_path.reio_path(self.game_data, self.patch_folder, mk_dir=True)

    def a2t(self, file_path) -> Path:
        """
        @brief      游戏数据文件夹到临时文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        return file_path.reio_path(self.game_data, self.tmp_folder, mk_dir=True)

    def t2p(self, file_path) -> Path:
        """
        @brief      临时文件夹到补丁文件夹，保持目录结构路径

        @param      file_path  文件路径对象

        @return     目标文件路径对象
        """
        return file_path.reio_path(self.tmp_folder, self.patch_folder, mk_dir=True)

    def upscale(self, game_data, patch_folder, scale_ratio, run_dict=None, encoding=None, resolution=None, **advanced_option):
        """
        @brief      对游戏进行放大处理

        @param      game_data        输入游戏数据文件夹
        @param      patch_folder     输出游戏补丁文件夹
        @param      scale_ratio      放大倍率
        @param      run_dict         可选放大部分字典
        @param      encoding         默认文本编码
        @param      resolution       游戏原生分辨率
        @param      advanced_option  高级处理选项
        """
        # 参数处理
        self.game_data = Path(game_data)
        self.patch_folder = Path(patch_folder)
        self.scale_ratio = scale_ratio
        if run_dict is not None:
            for _key, _value in run_dict.items():
                self.run_dict[_key] = _value
        if encoding is not None:
            self.encoding = encoding
        if resolution is not None:
            self.scwidth, self.scheight = resolution
        # 高级选项
        self.advanced_option = advanced_option
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
        if self.run_dict['animation']:
            self._animation2x()
            self.emit_info('动画文件处理完成')
        if self.run_dict['video']:
            self._video2x()
            self.emit_info('视频文件处理完成')
        timing_count = time.time() - start_time
        self.emit_info(f'共耗时：{seconds_format(timing_count)}')

    def _script2x(self):
        """
        @brief      对脚本进行处理，需复写
        """
        pass

    def _image2x(self):
        """
        @brief      对图像进行处理，需复写
        """
        pass

    def _animation2x(self):
        """
        @brief      对动画进行处理，需复写
        """
        pass

    def _video2x(self):
        """
        @brief      对视频进行处理，需复写
        """
        pass
