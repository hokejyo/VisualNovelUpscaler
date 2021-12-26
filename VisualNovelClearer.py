# -*- coding:utf-8 -*-

from Globals import *
from VNCConfig import vc
from Kirikiri import Kirikiri
from Artemis import Artemis


def get_engine_type(game_data):
    game_data = os.path.abspath(game_data)
    for file in file_list(game_data):
        if os.path.basename(file) == 'Config.tjs':
            return 'Kirikiri'
        elif os.path.basename(file) == 'list_windows.tbl':
            return 'Artemis'
    input('未识别的游戏引擎，按回车键退出：')
    sys.exit()


if __name__ == '__main__':
    # 防止多进程内存泄漏
    freeze_support()
    # 错误日志
    logging.basicConfig(filename=vc.vnc_log_file, level=logging.DEBUG, filemode='a+', format='[%(asctime)s] [%(levelname)s] >>>  %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    try:
        try:
            game_data = sys.argv[1]
        except IndexError:
            game_data = input('\n请将游戏拆包后放到同一文件夹拖到此处后按回车：\n').replace('\\', '\\\\')
        game_engine = get_engine_type(game_data)
        if game_engine == 'Kirikiri':
            game = Kirikiri(game_data)
        elif game_engine == 'Artemis':
            game = Artemis(game_data)
        game.upscale()
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
