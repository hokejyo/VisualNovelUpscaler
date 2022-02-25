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

    def check_in_out_folder(self, input_folder, output_folder='', check_output=True, only_folder=True) -> bool:
        input_folder = Path(input_folder).resolve()
        output_folder = Path(output_folder).resolve()
        warn_message = None
        if not input_folder.exists():
            warn_message = '输入路径不存在'
        if not input_folder.is_dir() and only_folder:
            warn_message = '输入路径需要是文件夹'
        if input_folder == Path('./').resolve():
            warn_message = '输入路径不能与工作目录相同'
        if check_output:
            if output_folder == Path('./').resolve():
                warn_message = '输出路径不能与工作目录相同'
            if input_folder == output_folder:
                warn_message = '输入路径和输出路径不能相同'
        if warn_message is not None:
            warn_msg = QMessageBox()
            reply = warn_msg.warning(self.ui, '提示', warn_message+'!', QMessageBox.Yes)
            return False
        else:
            if check_output:
                if not output_folder.exists():
                    output_folder.mkdir(parents=True)
            return True


if __name__ == '__main__':
    # 防止打包运行后多进程内存泄漏
    freeze_support()
    # 防止打包后拖拽运行工作路径改变
    bundle_dir = Path(sys.argv[0]).resolve().parent
    os.chdir(bundle_dir)
    # 错误日志
    vnc_log_file = bundle_dir/'log.txt'
    logging.basicConfig(filename=vnc_log_file, level=logging.DEBUG, filemode='a+', format='[%(asctime)s] [%(levelname)s] >>>  %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    # 启动
    # try:
    if True:
        app = QApplication(sys.argv)
        visual_novel_clearer = VisualNovelClearer()
        visual_novel_clearer.ui.show()
        sys.exit(app.exec())
    # except Exception as e:
    #     logging.error(e)
    #     logging.error(traceback.format_exc())
    #     sys.exit()
