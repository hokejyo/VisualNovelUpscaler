# -*- coding:utf-8 -*-

from .functions import *
from .config import Config
from .texts_utils import TextsUtils
from .image_utils import ImageUtils
from .video_utils import VideoUtils


class Core(Config, TextsUtils, ImageUtils, VideoUtils):
    """核心"""

    uuid_list = []

    def __init__(self):
        Config.__init__(self)

    def set_vn_hd_io_folder(self, game_data, patch_folder):
        self.game_data = Path(game_data)
        self.patch_folder = Path(patch_folder)

    def set_resolution_encoding(self, scwidth, scheight, encoding):
        self.scwidth = scwidth
        self.scheight = scheight
        self.encoding = encoding

    def emit_info(self, info_str):
        print(info_str)
        logging.info(info_str)

    def emit_progress(self, _percent, _left_time):
        print(_percent, _left_time, sep='\t')

    def pool_run(self, target, runs, *args) -> list:
        """
        @brief      使用进程池多进程加速计算

        @param      target  目标执行函数
        @param      runs    执行可变参数迭代器
        @param      args    其它固定参数，按执行函数参数顺序输入

        @return     将执行函数的返回值以列表返回
        """
        pool = Pool(self.cpu_cores)
        processer_ls = []
        for i in runs:
            processer = pool.apply_async(target, args=(i, *args))
            processer_ls.append(processer)
        pool.close()
        pool.join()
        return [processer.get() for processer in processer_ls]

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

    def create_str(self, len_num=8) -> str:
        """
        @brief      生成不重复的指定位数的字符串

        @param      len_num  字符串长度

        @return     字符串
        """
        while True:
            uuid_str = str(uuid.uuid4())[:len_num]
            if uuid_str not in self.uuid_list:
                self.uuid_list.append(uuid_str)
                break
        return uuid_str
