# -*- coding: utf-8 -*-

from Core import *
from VNEngines import *
from GUI import *
from GamePageUIConnection import GamePageUIConnection
from SettingPageUIConnection import SettingPageUIConnection


class VisualNovelClearer(Core, SettingPageUIConnection, GamePageUIConnection):

    _version = 'v0.2.0'

    def __init__(self):
        Core.__init__(self)
        self.initUI()
        self.ui.set_version(self._version)

    def initUI(self):
        self.ui = MainUI()
        SettingPageUIConnection.__init__(self)
        GamePageUIConnection.__init__(self)


if __name__ == '__main__':
    # 防止打包运行后多进程内存泄漏
    freeze_support()
    # 防止打包后拖拽运行工作路径改变
    bundle_dir = Path(sys.argv[0]).parent
    os.chdir(bundle_dir)
    # 错误日志
    vnc_log_file = bundle_dir/'log.txt'
    logging.basicConfig(filename=vnc_log_file, level=logging.DEBUG, filemode='a+', format='[%(asctime)s] [%(levelname)s] >>>  %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    # 启动
    try:
        app = QApplication(sys.argv)
        visual_novel_clearer = VisualNovelClearer()
        visual_novel_clearer.ui.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
        sys.exit()

