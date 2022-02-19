# -*- coding:utf-8 -*-

import os
import re
import sys
import csv
import png
import json
import time
import uuid
import shutil
import logging
import traceback
import subprocess
import configparser
from wmi import WMI
from PIL import Image
from pathlib import Path
from math import ceil, log
from functools import lru_cache
from multiprocessing import Pool, cpu_count, Process, freeze_support

import hashlib
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


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
    GPU_ID = str(GPU_name_list.index(GPU_name))
    return GPU_ID


def p2p(input_file, input_folder, output_folder) -> Path:
    """
    @brief      返回相对于输入文件夹目录结构在输出文件夹的路径

    @param      input_file     输入文件
    @param      input_folder   输入文件夹路径
    @param      output_folder  输出文件夹路径

    @return     目标文件路径
    """
    input_file = Path(input_file).resolve()
    input_folder = Path(input_folder).resolve()
    output_folder = Path(output_folder).resolve()
    target_file = output_folder/input_file.relative_to(input_folder)
    if not target_file.parent.exists():
        target_file.parent.mkdir(parents=True, exist_ok=True)
    return target_file


def fcopy(src, dst) -> Path:
    """
    @brief      复制文件到文件夹

    @param      src   源文件
    @param      dst   目标文件夹

    @return     目标文件路径
    """
    src = Path(src).resolve()
    dst = Path(dst).resolve()
    target_file = dst/(src.name)
    if target_file.exists():
        target_file.unlink()
    if not dst.exists():
        dst.mkdir(parents=True)
    shutil.copy(src, dst)
    return target_file


def fmove(src, dst) -> Path:
    """
    @brief      移动文件到文件夹

    @param      src   源文件
    @param      dst   目标文件夹

    @return     目标文件路径
    """
    src = Path(src).resolve()
    dst = Path(dst).resolve()
    target_file = dst/(src.name)
    if target_file.exists():
        target_file.unlink()
    if not dst.exists():
        dst.mkdir(parents=True)
    shutil.move(src, dst)
    return target_file


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
    """
    @brief      判断字符串是否为数字

    @param      str1  字符串

    @return     布尔值
    """
    try:
        tmp = float(str1)
        return True
    except:
        return False


def pattern_num2x(re_result, scale_ratio, test_mode=False, line=None) -> str:
    """
    @brief      将正则匹配结果中的数字乘以放大倍数

    @param      re_result    re.match()捕获的正则匹配结果
    @param      scale_ratio  放大倍数
    @param      test_mode    测试模式
    @param      line         原始行字符串，需要test_mode为True

    @return     放大数字后的行字符串
    """
    if test_mode:
        print(line, end='')
    re_result_ls = list(re_result.groups())
    for i in range(len(re_result_ls)):
        if real_digit(re_result_ls[i]):
            if test_mode:
                print(re_result_ls[i])
            re_result_ls[i] = str(int(float(re_result_ls[i])*scale_ratio))
    re_result_ls = [i for i in re_result_ls if i != None]
    line = ''.join(re_result_ls)
    if test_mode:
        print(line, end='\n'*2)
    return line


def seconds_format(time_length) -> str:
    """
    @brief      将秒格式化输出为时分秒

    @param      time_length  时长

    @return     输出字符串
    """
    m, s = divmod(time_length, 60)
    h, m = divmod(m, 60)
    return "%dh%02dm%02ds" % (h, m, s)


def batch_group_list(inlist, batch_size=10) -> list:
    """
    @brief      将列表以指定大小划分为多个列表

    @param      inlist      输入列表
    @param      batch_size  每个列表元素数量

    @return     划分列表的列表
    """
    group_list = []
    start_index = 0
    while True:
        end_index = start_index+batch_size
        group = inlist[start_index:end_index]
        if group == []:
            break
        else:
            group_list.append(group)
            start_index = end_index
    return group_list
