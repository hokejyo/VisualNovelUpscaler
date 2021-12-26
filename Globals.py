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
from wmi import WMI
from PIL import Image
from pathlib import Path
from math import log2, ceil
from multiprocessing import Pool, cpu_count, Process, freeze_support


def image_zoom(input_path, zoom_factor, output_path=None) -> Path:
    """
    @brief      单张图片缩放

    @param      input_path   输入路径
    @param      zoom_factor  缩放系数
    @param      output_path  输出路径

    @return     输出图片路径对象
    """
    if not output_path:
        output_path = input_path
    image = Image.open(input_path)
    image_resize = image.resize(
        (int(image.width*zoom_factor), int(image.height*zoom_factor)),
        Image.ANTIALIAS)
    image_resize.save(output_path)
    return output_path


def image_convert(input_path, output_extention, del_input=False) -> Path:
    """
    @brief      单张图片格式转换

    @param      input_path        输入路径
    @param      output_extention  输出格式
    @param      del_input         是否删除输入图片

    @return     输出图片路径对象
    """
    input_path = Path(input_path)
    output_path = input_path.with_suffix('.'+output_extention)
    if output_extention.lower() in ['jpg', 'jpeg']:
        Image.open(input_path).convert('RGB').save(output_path, quality=100)
    else:
        Image.open(input_path).save(output_path, quality=100)
    if del_input:
        if output_path != input_path:
            input_path.unlink()
    return output_path


def alpha_image(image_path) -> bool:
    """
    @brief      检查图片是否含有alpha通道

    @param      image_path  图片路径

    @return     bool
    """
    return True if Image.open(image_path).mode in ['RGBA', 'LA'] else False


def get_image_format(image_path) -> str:
    """
    @brief      获取图片真实格式

    @param      image_path  图片路径

    @return     图片格式
    """
    return Image.open(image_path).format.lower()


def get_gpu_list() -> list:
    """
    @brief      获取显卡名称列表

    @return     返回显卡名称列表
    """
    GPUs = WMI().Win32_VideoController()
    GPU_list = [i.name for i in GPUs]
    return GPU_list


def get_gpu_id(GPU_name) -> str:
    """
    @brief      获取显卡ID

    @param      GPU_name  显卡名

    @return     返回显卡ID
    """
    GPU_list = get_gpu_list()
    return str(GPU_list.index(GPU_name))


def fcopy(src, dst):
    """
    @brief      复制文件到文件夹

    @param      src   源文件
    @param      dst   目标文件夹
    """
    src = Path(src)
    dst = Path(dst)
    target_file = dst/(src.name)
    if target_file.exists():
        target_file.unlink()
    if not dst.exists():
        dst.makedir(parents=True)
    shutil.copy(src, dst)


def fmove(src, dst):
    """
    @brief      移动文件到文件夹

    @param      src   源文件
    @param      dst   目标文件夹
    """
    src = Path(src)
    dst = Path(dst)
    target_file = dst/(src.name)
    if target_file.exists():
        target_file.unlink()
    if not dst.exists():
        dst.makedir(parents=True)
    shutil.move(src, dst)


def get_encoding(script_file) -> str:
    """
    @brief      获取文本编码

    @param      script_file  文本文件路径

    @return     文本编码格式
    """
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
    folder = Path(folder)
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
    file_path_ls = [Path(file) for file in file_path_ls]
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
        start_time_dict[image_file] = image_file.stat().st_mtime
    # 时间戳判断图片是否被放大
    now_count = len([image_file for image_file in start_time_dict.keys() if image_file.stat().st_mtime > start_time_dict[image_file]])
    target_count = len(start_time_dict.keys())
    if target_count == 0:
        now_percent = 1
        print(f'未发现需要放大的{image_extension}图片')
    else:
        now_percent = now_count/target_count
    start_time = time.time()
    # 百分比小于100%时循环
    while now_percent < 1:
        now_time = time.time()
        try:
            now_count = len([image_file for image_file in start_time_dict.keys() if image_file.stat().st_mtime > start_time_dict[image_file]])
        except:
            pass
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
