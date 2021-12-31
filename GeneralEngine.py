# -*- coding:utf-8 -*-

from GeneralFunctions import *
from Config import Config
from TextsUtils import TextsUtils
from ImageUtils import ImageUtils
from VideoUtils import VideoUtils


class GeneralEngine(Config, TextsUtils, ImageUtils, VideoUtils):
    """通用引擎"""

    def __init__(self):
        Config.__init__(self)
        # 默认必要参数
        self.encoding, self.scwidth, self.scheight = 'shift-jis', 1280, 720

    def get_default_scale_ratio(self) -> float:
        if self.scwidth/self.scheight == 16/9:
            scale_ratio = float(1080/self.scheight)
        else:
            scale_ratio = float(2)
        return scale_ratio

    def get_hd_resolution(self):
        if self.scwidth/self.scheight == 16/9:
            if self.scheight*self.scale_ratio == 1080:
                hd_resolution = '1080P'
            elif self.scheight*self.scale_ratio == 1440:
                hd_resolution = '2K'
            elif self.scheight*self.scale_ratio == 2160:
                hd_resolution = '4K'
            else:
                hd_resolution = '%d*%d' % (int(self.scwidth*self.scale_ratio), int(self.scheight*self.scale_ratio))
        else:
            hd_resolution = '%d*%d' % (int(self.scwidth*self.scale_ratio), int(self.scheight*self.scale_ratio))
        return hd_resolution

    def change_scale_ratio(self):
        sep_line = '-'*80
        os.system('cls')
        if self.scwidth/self.scheight == 16/9:
            choice = input(f'{sep_line}\n请选择高清重制后的分辨率：\n{sep_line}\n[1]1080P\n[2]2K\n[3]4K\n[4]自定义\n{sep_line}\n请选择(默认1080P)：')
            if choice == '1':
                scale_ratio = float(1080/self.scheight)
            elif choice == '2':
                scale_ratio = float(1440/self.scheight)
            elif choice == '3':
                scale_ratio = float(2160/self.scheight)
            elif choice == '4':
                scale_ratio = float(input('\n请手动输入放大倍数：'))
            else:
                scale_ratio = float(1080/self.scheight)
        else:
            scale_ratio = float(input('游戏原生分辨率非16:9，请手动输入放大倍数：'))
        self.scale_ratio = scale_ratio

    def get_lines_encoding(self, text_file):
        '''
        返回文本内容和编码
        '''
        try:
            with open(text_file, newline='', encoding=self.encoding) as f:
                lines = f.readlines()
                current_encoding = self.encoding
        except UnicodeDecodeError:
            current_encoding = self.get_encoding(text_file)
            with open(text_file, newline='', encoding=current_encoding) as f:
                lines = f.readlines()
        return lines, current_encoding

    def change_config(self):
        '''
        配置文件修改
        '''
        cpu_cores = input()
        # 写入配置文件
        with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
            self.vnc_config.set('General', 'cpu_cores', cpu_cores)
            self.vnc_config.set('General', 'gpu_id', gpu_id)
            self.vnc_config.set('waifu2x', 'process_mode', process_mode)
            self.vnc_config.set('waifu2x', 'style_mode', style_mode)
            self.vnc_config.set('waifu2x', 'crop_size', crop_size)
            self.vnc_config.write(vcf)
        self.load_config()
        input('配置修改完成，按回车返回：')

    def reset_vnc_config(self):
        os.system('cls')
        self.reset_config()
        input('配置文件重置完成，按回车返回：')

    def print_vnc_config(self):
        os.system('cls')
        with open(self.vnc_config_file, newline='', encoding='utf-8') as vcf:
            print(vcf.read())
        input('按回车返回：')

    def print_license(self):
        os.system('cls')
        print('-'*80)
        with open(self.vnc_lic_file, newline='', encoding='utf-8') as vlicf:
            print(vlicf.read())
        print('-'*80)
        input('按回车返回：')

    def show_image2x_status(self, image_extension):
        '''
        显示图片处理进度条，根据时间戳判断图片是否被放大
        '''
        target_count = len(file_list(self.tmp_folder, image_extension))
        if target_count == 0:
            now_percent = 1
            print(f'未发现需要放大的{image_extension}图片')
        else:
            now_percent = 0
        start_time = time.time()
        # 百分比小于100%时循环
        while now_percent < 1:
            now_time = time.time()
            # 时间戳判断图片是否被放大
            now_count = len([image_file for image_file in file_list(self.tmp_folder, image_extension) if image_file.stat().st_mtime > start_time])
            now_percent = now_count/target_count
            if now_percent == 0:
                print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：统计中...', end=' \r')
                time.sleep(2)
                continue
            left_time = int((now_time-start_time)/now_percent - (now_time-start_time))
            print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：{seconds_format(left_time)}', end=' \r')
            time.sleep(2)
            if now_percent == 1:
                print()


if __name__ == '__main__':
    input_path = Path(r"D:\trail\krkr\sy\test1")
    # input_path = Path(r"D:\trail\krkr\sy\test2\image\logface\logface_花子.png"))
    output_folder = Path(r"D:\trail\krkr\sy\test2")
    a = GeneralEngine()
    a.scale_ratio = 1.5
    # a.super_resolution_engine = 'real_esrgan'
    b = a.image_upscale(input_path, output_folder, 'jpg')
    print(b)
