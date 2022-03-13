# -*- coding: utf-8 -*-

from .functions import *


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

    def get_lines_encoding(self, text_file):
        '''
        返回文本内容和编码
        '''
        try:
            with open(text_file, newline='', encoding=self.encoding) as f:
                lines = f.readlines()
                current_encoding = self.encoding
        except:
            current_encoding = self.get_encoding(text_file)
            with open(text_file, newline='', encoding=current_encoding) as f:
                lines = f.readlines()
        return lines, current_encoding

    def csv2x(self, input_csv, output_csv, scale_ratio):
        '''
        将csv文件中的数字乘以放大倍数
        '''
        result = []
        try:
            with open(input_csv, newline='', encoding=self.encoding) as f:
                current_encoding = self.encoding
                content = list(csv.reader(f))
        except:
            current_encoding = self.get_encoding(input_csv)
            with open(input_csv, newline='', encoding=current_encoding) as f:
                content = list(csv.reader(f))
        for content_ls in content:
            for i in range(len(content_ls)):
                if real_digit(content_ls[i]):
                    content_ls[i] = str(int(float(content_ls[i]) * scale_ratio))
            result.append(content_ls)
        with open(output_csv, 'w', newline='', encoding=current_encoding) as f:
            content2x = csv.writer(f)
            content2x.writerows(result)

    def line_pattern_num2x(self, re_result, test_mode=False, line=None) -> str:
        """
        @brief      将正则匹配结果中的数字乘以放大倍数

        @param      re_result  re.match()捕获的正则匹配结果
        @param      test_mode  测试模式
        @param      line       原始行字符串，需要test_mode为True

        @return     放大数字后的行字符串
        """
        return pattern_num2x(re_result, self.scale_ratio, test_mode=test_mode, line=line)
