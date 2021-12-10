# -*- coding:utf-8 -*-

import os
import re
import sys
import csv
import png
import json
import time
import shutil
import logging
import traceback
import subprocess
import configparser
from multiprocessing import Pool, cpu_count, Process, freeze_support


def fcopy(src, dst):
    '''
    强制复制，限定文件到目录
    '''
    target_file = os.path.join(dst, os.path.basename(src))
    if os.path.exists(target_file):
        os.remove(target_file)
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.copy(src, dst)


def fmove(src, dst):
    '''
    强制移动，限定文件到目录
    '''
    target_file = os.path.join(dst, os.path.basename(src))
    if os.path.exists(target_file):
        os.remove(target_file)
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.move(src, dst)


def get_encoding(script_file):
    '''
    获取编码
    '''
    encoding_ls = ['shift-jis', 'utf-8', 'gbk', 'utf-16', 'CP932']
    with open(script_file, 'rb') as f:
        content_b = f.read()
        for encoding in encoding_ls:
            try:
                content_b.decode(encoding=encoding)
                return encoding
            except:
                continue
        return 'Unknown_Encoding'


def extension_name(file) -> str:
    '''
    获取文件扩展名
    '''
    try:
        return file.split('.')[-1]
    except:
        return 'Unknown_Extension'


def file_list(folder, extension=None, walk_mode=True, ignored_folders=[], parent_folders=[]) -> list:
    '''
    默认获取目录树中所有文件的路径

    可选：
    指定扩展名(忽略大小写)
    不遍历目录树
    忽略遍历文件夹
    指定上级目录(不包含子目录)
    '''
    file_path_ls = []
    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        for file in files:
            file_path = os.path.join(root, file)
            if not extension:
                file_path_ls.append(file_path)
            else:
                if extension_name(file).lower() == extension.lower():
                    file_path_ls.append(file_path)
        if walk_mode == False:
            break
    if parent_folders:
        file_path_ls = [file_path for file_path in file_path_ls if os.path.basename(os.path.dirname(file_path)) in parent_folders]
    return file_path_ls


def real_digit(str1) -> bool:
    '''
    判断字符串是否为数字
    '''
    try:
        tmp = float(str1)
        return True
    except:
        return False


def pattern_num2x(line, line_c, scale_ratio, test_mode=False) -> str:
    '''
    将正则匹配结果中的行中的数字乘以放大倍数
    '''
    if test_mode == True:
        print(line, end='')
    line_cc = list(line_c.groups())
    for i in range(len(line_cc)):
        if real_digit(line_cc[i]):
            if test_mode == True:
                print(line_cc[i])
            line_cc[i] = str(int(float(line_cc[i])*scale_ratio))
    line_cc = [i for i in line_cc if i != None]
    line = ''.join(line_cc)
    if test_mode == True:
        print(line, end='\n'*2)
    return line


def seconds_format(time_length) -> str:
    '''
    将秒格式化输出
    '''
    m, s = divmod(time_length, 60)
    h, m = divmod(m, 60)
    return "%dh%02dm%02ds" % (h, m, s)


def show_image2x_status(image_folder, image_extension):
    '''
    显示图片处理进度条，根据时间戳判断图片是否被放大
    '''
    start_time_dict = {}
    for image_file in file_list(image_folder, image_extension):
        start_time_dict[image_file] = os.path.getmtime(image_file)
    # 时间戳判断图片是否被放大
    now_count = len([image_file for image_file in file_list(image_folder, image_extension) if os.path.getmtime(image_file) > start_time_dict[image_file]])
    target_count = len(file_list(image_folder, image_extension))
    if target_count == 0:
        now_percent = 1
        print(f'未发现需要放大的{image_extension}图片')
    else:
        now_percent = now_count/target_count
    start_time = time.time()
    # 百分比小于100%时循环
    while now_percent < 1:
        now_time = time.time()
        now_count = len([image_file for image_file in file_list(image_folder, image_extension) if os.path.getmtime(image_file) > start_time_dict[image_file]])
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


class VNCConfig(object):
    """配置设置"""

    def __init__(self):
        # 打包后工作目录变了啊
        self.bundle_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        os.chdir(self.bundle_dir)
        self.vnc_config = configparser.ConfigParser()
        self.vnc_config_file = os.path.join(self.bundle_dir, 'config.ini')
        self.vnc_log_file = os.path.join(self.bundle_dir, 'log_records.txt')
        self.vnc_lic_file = os.path.join(self.bundle_dir, 'LICENSE')
        self.write_vnc_config()
        self.read_vnc_config()

    def write_vnc_config(self, reset_mode=False):
        if not os.path.exists(self.vnc_config_file):
            reset_mode = True
        if reset_mode == True:
            self.vnc_config = configparser.ConfigParser()
            if os.path.exists(self.vnc_config_file):
                os.remove(self.vnc_config_file)
            with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
                self.vnc_config.add_section('General')
                self.vnc_config.set('General', 'image_scale_mode', 'waifu2x')
                self.vnc_config.set('General', 'cpu_cores', str(cpu_count()))
                self.vnc_config.set('General', 'gpu_No', '0')
                # waifu2x配置相关
                self.vnc_config.add_section('waifu2x')
                self.vnc_config.set('waifu2x', 'process_mode', 'cudnn')
                self.vnc_config.set('waifu2x', 'crop_size', '128')
                self.vnc_config.set('waifu2x', 'scale_mode', 'noise_scale')
                self.vnc_config.set('waifu2x', 'noise_level', '3')
                self.vnc_config.set('waifu2x', 'style_mode', 'cunet')
                self.vnc_config.set('waifu2x', 'batch_size', '1')
                self.vnc_config.set('waifu2x', 'tta', '0')
                # ffmpeg配置相关
                self.vnc_config.add_section('ffmpeg')
                self.vnc_config.set('ffmpeg', 'video_quality', '2')
                self.vnc_config.write(vcf)

    def read_vnc_config(self):
        # 依赖工具集执行文件路径
        self.toolkit_path = os.path.join(self.bundle_dir, 'Dependencies')
        # https://github.com/FFmpeg/FFmpeg
        self.ffmpeg = os.path.join(self.toolkit_path, 'ffmpeg\\bin\\ffmpeg.exe')
        self.ffprobe = os.path.join(self.toolkit_path, 'ffmpeg\\bin\\ffprobe.exe')
        # https://github.com/lltcggie/waifu2x-caffe
        self.waifu2x_exe = os.path.join(self.toolkit_path, 'waifu2x-caffe\\waifu2x-caffe-cui.exe')
        # https://github.com/TianZerL/Anime4KCPP
        self.anime4k_exe = os.path.join(self.toolkit_path, 'Anime4KCPP_CLI\\Anime4KCPP_CLI.exe')
        # https://github.com/UlyssesWu/FreeMote
        self.psb_de_exe = os.path.join(self.toolkit_path, 'FreeMoteToolkit\\PsbDecompile.exe')
        self.psb_en_exe = os.path.join(self.toolkit_path, 'FreeMoteToolkit\\PsBuild.exe')
        # https://github.com/vn-toolkit/tlg2png
        self.tlg2png_exe = os.path.join(self.toolkit_path, 'tlg2png\\tlg2png.exe')
        # https://github.com/krkrz/krkr2
        self.krkrtpc_exe = os.path.join(self.toolkit_path, 'krkrtpc\\krkrtpc.exe')
        # https://github.com/zhiyb/png2tlg
        self.png2tlg6_exe = os.path.join(self.toolkit_path, 'png2tlg6\\png2tlg6.exe')
        # https://github.com/xmoeproject/AlphaMovieDecoder
        self.amv_de_exe = os.path.join(self.toolkit_path, 'AlphaMovieDecoder\\AlphaMovieDecoderFake.exe')
        self.amv_de_folder = os.path.join(self.toolkit_path, 'AlphaMovieDecoder\\video')
        # https://github.com/zhiyb/AlphaMovieEncoder
        self.amv_en_exe = os.path.join(self.toolkit_path, 'AlphaMovieEncoder\\amenc.exe')
        # 通用参数
        self.vnc_config.read(self.vnc_config_file)
        self.image_scale_mode = self.vnc_config.get('General', 'image_scale_mode')
        self.cpu_cores = self.vnc_config.getint('General', 'cpu_cores')
        self.gpu_No = self.vnc_config.get('General', 'gpu_No')
        # waifu2x配置相关
        self.process_mode = self.vnc_config.get('waifu2x', 'process_mode')
        self.crop_size = self.vnc_config.get('waifu2x', 'crop_size')
        self.scale_mode = self.vnc_config.get('waifu2x', 'scale_mode')
        self.noise_level = self.vnc_config.get('waifu2x', 'noise_level')
        self.style_mode = self.vnc_config.get('waifu2x', 'style_mode')
        self.batch_size = self.vnc_config.get('waifu2x', 'batch_size')
        self.tta = self.vnc_config.get('waifu2x', 'tta')
        # ffmpeg配置相关
        self.video_quality = self.vnc_config.get('ffmpeg', 'video_quality')


vc = VNCConfig()
