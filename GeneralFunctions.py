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
from math import ceil, log
from multiprocessing import Pool, cpu_count, Process, freeze_support


def get_gpu_list() -> list:
    """
    @brief      获取显卡名称列表

    @return     返回显卡名称列表
    """
    GPUs = WMI().Win32_VideoController()
    GPU_name_list = [i.name for i in GPUs]
    return GPU_name_list


def get_gpu_id(GPU_name) -> str:
    """
    @brief      获取显卡ID

    @param      GPU_name  显卡名

    @return     返回显卡ID
    """
    GPU_name_list = get_gpu_list()
    return str(GPU_name_list.index(GPU_name))


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


def get_parent_names(file_path) -> list:
    """
    @brief      获取文件父目录名的列表

    @param      file_path  文件路径

    @return     父目录名列表
    """
    parent_names = [i.name for i in Path(file_path).resolve().parents]
    parent_names.remove('')
    return parent_names


def file_list(folder, extension=None, walk_mode=True, ignored_folders=[], parent_folder=None) -> list:
    """
    @brief      获取文件夹中文件的路径对象

    @param      folder           指定文件夹
    @param      extension        指定扩展名
    @param      walk_mode        是否递归查找
    @param      ignored_folders  忽略文件夹，不遍历子目录
    @param      parent_folder    父级文件夹，包含子目录

    @return     文件路径对象列表
    """
    folder = Path(folder).resolve()
    file_path_ls = []
    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        for file in files:
            file_path = Path(root)/file
            if not extension:
                file_path_ls.append(file_path)
            else:
                if file_path.suffix.lower() == '.'+extension.lower():
                    file_path_ls.append(file_path)
        if walk_mode == False:
            break
    if parent_folder:
        file_path_ls = [file_path for file_path in file_path_ls if parent_folder in get_parent_names(file_path)]
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


# def show_image2x_status(image_folder, image_extension):
#     '''
#     显示图片处理进度条，根据时间戳判断图片是否被放大
#     '''
#     start_time_dict = {}
#     for image_file in file_list(image_folder, image_extension):
#         start_time_dict[image_file] = image_file.stat().st_mtime
#     # 时间戳判断图片是否被放大
#     now_count = len([image_file for image_file in start_time_dict.keys() if image_file.stat().st_mtime > start_time_dict[image_file]])
#     target_count = len(start_time_dict.keys())
#     if target_count == 0:
#         now_percent = 1
#         print(f'未发现需要放大的{image_extension}图片')
#     else:
#         now_percent = now_count/target_count
#     start_time = time.time()
#     # 百分比小于100%时循环
#     while now_percent < 1:
#         now_time = time.time()
#         try:
#             now_count = len([image_file for image_file in start_time_dict.keys() if image_file.stat().st_mtime > start_time_dict[image_file]])
#         except:
#             pass
#         now_percent = now_count/target_count
#         if now_percent == 0:
#             print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：统计中...', end=' \r')
#             time.sleep(2)
#             continue
#         left_time = int((now_time-start_time)/now_percent - (now_time-start_time))
#         print('处理进度：[%s]' % (format('>'*int(35*now_percent), '<35')), format(now_percent, ' >7.2%'), f'预计剩余时间：{seconds_format(left_time)}', end=' \r')
#         time.sleep(2)
#         if now_percent == 1:
#             print()
