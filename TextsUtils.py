# -*- coding: utf-8 -*-

from GeneralFunctions import *


class TextsUtils(object):
    """
    @brief      专用于处理文本文件
    """

    def get_encoding(self, text_file) -> str:
        """
        @brief      获取文本编码

        @param      text_file  文本文件路径

        @return     文本编码格式
        """
        with open(text_file, 'rb') as f:
            content_b = f.read()
            for encoding in self.encoding_list:
                try:
                    content_b.decode(encoding=encoding)
                    return encoding
                except:
                    continue
            return 'Unknown_Encoding'
