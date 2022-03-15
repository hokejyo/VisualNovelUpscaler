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
        # 错误日志
        logging.basicConfig(filename=self.vnc_log_file, encoding='UTF-8', level=logging.DEBUG, filemode='a+', format='[%(asctime)s] [%(levelname)s] >>>  %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
        try:
            self.ui = MainUI()
            SettingPageUIConnection.__init__(self)
            GamePageUIConnection.__init__(self)
        except Exception as e:
            error_info = traceback.format_exc()
            logging.error(error_info)
            error_msg = QMessageBox()
            reply = error_msg.critical(self.ui, '错误!', error_info, QMessageBox.Yes)

if __name__ == '__main__':
    # _main()
    # 防止打包运行后多进程内存泄漏
    freeze_support()
    # 防止打包后拖拽运行工作路径改变
    bundle_dir = Path(sys.argv[0]).parent
    os.chdir(bundle_dir)
    # 启动
    app = QApplication(sys.argv)
    visual_novel_clearer = VisualNovelClearer()
    visual_novel_clearer.ui.show()
    sys.exit(app.exec())
