# -*- coding:utf-8 -*-
# 调用Artemis_Pack_Tool一键封包
# https://github.com/crskycode/Artemis_Pack_Tool

import os
import sys


def pack_artemis(input_path, output_path=None):
    toolkit_path = os.path.join(bundle_dir, 'Dependencies')
    artemis_pack_tool = os.path.join(toolkit_path, 'Artemis_Pack_Tool\\Artemis_Pack_Tool.exe')
    if not output_path:
        output_path = os.path.join(bundle_dir, 'root.pfs')
    count = 1
    while os.path.exists(output_path):
        output_path = 'root.pfs' + '.%03d' % count
        count += 1
    command = f'{artemis_pack_tool} {input_path} {output_path}'
    os.system(command)


if __name__ == '__main__':
    bundle_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(bundle_dir)
    try:
        input_path = sys.argv[1]
    except IndexError:
        input_path = input('\n请将需要打包的文件夹拖到此处后按回车：\n').replace('\\', '\\\\')
    pack_artemis(input_path)
    print('='*50)
    input('打包完成，按回车退出：')
    sys.exit()
