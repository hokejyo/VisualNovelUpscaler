# -*- coding:utf-8 -*-

import os
import sys


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


def extract_artemis(game_path, output_path=None):
    toolkit_path = os.path.join(bundle_dir, 'Dependencies')
    bms_tool = os.path.join(toolkit_path, 'quickbms\\quickbms_4gb_files.exe')
    bms_file = os.path.join(toolkit_path, 'quickbms\\artemis_engine.bms')
    if not output_path:
        output_path = os.path.join(bundle_dir, 'ArtemisExtract_Output')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if os.path.isfile(game_path):
        pfs_file = game_path
        command = f'{bms_tool} -o {bms_file} {pfs_file} {output_path}'
        os.system(command)
    else:
        pfs_file_ls = [pfs_file for pfs_file in file_list(game_path) if '.pfs' in os.path.basename(pfs_file)]
        pfs_file_ls.sort()
        for pfs_file in pfs_file_ls:
            command = f'{bms_tool} -o {bms_file} {pfs_file} {output_path}'
            os.system(command)


if __name__ == '__main__':
    bundle_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(bundle_dir)
    try:
        game_path = sys.argv[1]
    except IndexError:
        game_path = input('\n请将游戏文件夹或文件拖到此处后按回车：\n').replace('\\', '\\\\')
    extract_artemis(game_path)
    print('='*50)
    input('拆包完成，请把游戏目录中类似script、movie等文件夹也复制到ArtemisExtract_Output中，按回车退出：')
    sys.exit()