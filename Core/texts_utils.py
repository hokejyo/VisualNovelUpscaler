# -*- coding: utf-8 -*-

from .functions import *


class TextsUtils(object):
    """
    @brief      专用于处理文本文件
    """

    def get_encoding(self, text_file) -> str:
        """
        @brief      获取文本编码，获取不到返回None，优先从自定义编码列表中识别

        @param      text_file  文本文件路径

        @return     文本编码格式
        """
        encoding = None
        with open(text_file, 'rb') as f:
            content_b = f.read()
            for _encoding in self.encoding_list:
                try:
                    content_b.decode(encoding=_encoding)
                    encoding = _encoding
                    break
                except:
                    pass
            if encoding is None:
                encoding = chardet.detect(content_b)
            return encoding

    def get_lines_encoding(self, text_file, split=True):
        '''
        返回文本内容和编码
        '''
        try:
            with open(text_file, newline='', encoding=self.encoding) as f:
                lines = f.readlines() if split else f.read()
                current_encoding = self.encoding
        except:
            current_encoding = self.get_encoding(text_file)
            assert current_encoding != None, f'未能正确识别{text_file}的文本编码'
            with open(text_file, newline='', encoding=current_encoding) as f:
                lines = f.readlines() if split else f.read()
        return lines, current_encoding

    def csv2x(self, input_csv, output_csv, scale_ratio):
        '''
        将csv文件中的数字乘以放大倍数
        '''
        result = []
        lines, current_encoding = self.get_lines_encoding(input_csv, split=False)
        with PrivateStringIO(lines) as _f:
            content = list(csv.reader(_f))
        # try:
        #     with open(input_csv, newline='', encoding=self.encoding) as f:
        #         current_encoding = self.encoding
        #         content = list(csv.reader(f))
        # except:
        #     current_encoding = self.get_encoding(input_csv)
        #     with open(input_csv, newline='', encoding=current_encoding) as f:
        #         content = list(csv.reader(f))
        for content_ls in content:
            for i in range(len(content_ls)):
                if real_digit(content_ls[i]):
                    content_ls[i] = str(int(float(content_ls[i]) * scale_ratio))
            result.append(content_ls)
        with open(output_csv, 'w', newline='', encoding=current_encoding) as f:
            csvwtr = csv.writer(f)
            csvwtr.writerows(result)

    def line_pattern_num2x(self, re_result, test_mode=False, line=None) -> str:
        """
        @brief      将正则匹配结果中的数字乘以放大倍数

        @param      re_result  re.match()捕获的正则匹配结果
        @param      test_mode  测试模式
        @param      line       原始行字符串，需要test_mode为True

        @return     放大数字后的行字符串
        """
        return pattern_num2x(re_result, self.scale_ratio, test_mode=test_mode, line=line)

    def _sub_scale_num(self, match):
        """
        @brief      用于放大正则替换匹配到的数字pattern.sub(self.sub_scale_num), line)，放大倍数为self.scale_ratio

        @param      match        The match

        @return     放大后的数字
        """
        num_ = match.group()
        scaled_num_ = str(int(float(num_) * self.scale_ratio))
        return scaled_num_
