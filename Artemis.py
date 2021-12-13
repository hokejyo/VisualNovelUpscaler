# -*- coding:utf-8 -*-

from Globals import *
from GeneralEngine import GeneralEngine


class Artemis(GeneralEngine):
    """Artemis Engine"""

    def __init__(self, game_data):
        super().__init__(game_data)

        self.patch_folder = os.path.join(os.path.dirname(self.game_data), 'root')
        self.encoding, self.scwidth, self.scheight = self.get_encoding_resolution()
        self.scale_ratio = self.get_default_scale_ratio()
        self.run_dict = {'script': False, 'image': False, 'animation': False, 'video': False}

    def upscale(self):

        self.select2run()
        print('\n', format('开始处理', '=^76'), sep='', end='\n'*2)
        timing_start = time.time()
        if not os.path.exists(self.patch_folder):
            os.mkdir(self.patch_folder)
        if os.path.exists(self.tmp_folder):
            shutil.rmtree(self.tmp_folder)
        os.mkdir(self.tmp_folder)

        if self.run_dict['script']:
            self.script2x()
            print('脚本文件处理完成')
        if self.run_dict['image']:
            self.image2x()
            print('图片文件放大完成')
        if self.run_dict['animation']:
            self.animation2x()
            print('动画文件处理完成')
        if self.run_dict['video']:
            self.video2x()
            print('视频文件处理完成')

        shutil.rmtree(self.tmp_folder)
        timing_count = time.time() - timing_start
        tmp = input(f'\n高清重制完成，共耗时{seconds_format(timing_count)}\n请将root文件夹中的文件放到游戏根目录下\n按回车键退出：')
        sys.exit()

    def select2run(self):
        selecting = True
        sep_line = '-'*80
        while selecting:
            os.system('cls')
            self.hd_resolution = self.get_hd_resolution()
            print(f'{sep_line}\n检测到游戏引擎为Artemis，主要文本编码为：{self.encoding}，原生分辨率为：{self.scwidth}*{self.scheight}\n{sep_line}')
            select_num = input(f'[-1]更改高清重制分辨率：{self.hd_resolution}\n{sep_line}\n[0]一键自动执行\n[1]仅处理脚本文件\n[2]仅处理游戏图片\n[3]仅处理游戏动画\n[4]仅处理视频文件\n{sep_line}\n[95]显示配置\n[96]修改配置\n[97]重置配置\n[98]开源与第三方软件\n[99]退出程序\n{sep_line}\n请选择(默认一键自动执行)：')
            if select_num == '0':
                for key in self.run_dict.keys():
                    if key not in []:
                        self.run_dict[key] = True
            elif select_num == '1':
                self.run_dict['script'] = True
            elif select_num == '2':
                self.run_dict['image'] = True
            elif select_num == '3':
                self.run_dict['animation'] = True
            elif select_num == '4':
                self.run_dict['video'] = True

            elif select_num == '-1':
                self.change_scale_ratio()
                continue
            elif select_num == '95':
                self.print_vnc_config()
                continue
            elif select_num == '96':
                self.change_vnc_config()
                continue
            elif select_num == '97':
                self.reset_vnc_config()
                continue
            elif select_num == '98':
                self.print_license()
                continue
            elif select_num == '99':
                sys.exit()
            else:
                for key in self.run_dict.keys():
                    if key not in []:
                        self.run_dict[key] = True
            selecting = False

    def get_encoding_resolution(self):
        '''
        获取文本编码和分辨率
        '''
        for ini_file in file_list(self.game_data, 'ini'):
            if os.path.basename(ini_file) == 'system.ini':
                encoding = get_encoding(ini_file)
                with open(ini_file, newline='', encoding=encoding) as f:
                    lines = f.readlines()
                    pattern = re.compile(r'(WIDTH|HEIGHT|CHARSET)\W+([A-Za-z0-9]+-?[A-Za-z0-9]+).*')
                    for line in lines:
                        if line.startswith('WIDTH'):
                            scwidth = int(re.match(pattern, line).group(2))
                        if line.startswith('HEIGHT'):
                            scheight = int(re.match(pattern, line).group(2))
                        if line.startswith('CHARSET'):
                            encoding = re.match(pattern, line).group(2)
                        if line.startswith('[ANDROID]'):
                            break
                    return encoding, scwidth, scheight

    def a2p(self, file_path):
        '''
        游戏数据文件夹到补丁文件夹，保持目录结构路径
        '''
        target_file = file_path.replace(self.game_data, self.patch_folder)
        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        return target_file

    def a2t(self, file_path):
        '''
        游戏数据文件夹到临时文件夹，保持目录结构路径
        '''
        target_file = file_path.replace(self.game_data, self.tmp_folder)
        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        return target_file

    def t2p(self, file_path):
        '''
        临时文件夹到补丁文件夹，保持目录结构路径
        '''
        target_file = file_path.replace(self.tmp_folder, self.patch_folder)
        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        return target_file

    """
    ==================================================
    Artemis引擎脚本文件：ini, tbl, lua, iet, ipt, ast
    ==================================================
    """

    def script2x(self):
        print('正在处理脚本文件......')
        self.sysini2x()
        self.windows_xx_tbl2x()
        self.windwos_tbl2x()
        self.ipt2x()
        self.ast2x()
        self.lua2x()

    def sysini2x(self):
        '''
        游戏分辨率，存档位置修改
        '''
        for ini_file in file_list(self.game_data, 'ini'):
            if os.path.basename(ini_file) == 'system.ini':
                pattern1 = re.compile(r'(WIDTH|HEIGHT)(\W+)(\d+)(.*)')
                result = []
                lines, current_encoding = self.get_lines_encoding(ini_file)
                for line in lines:
                    line_c = re.match(pattern1, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                    result.append(line)
                with open(self.a2p(ini_file), 'w', newline='', encoding=current_encoding) as f:
                    _save_change = True
                    pattern2 = re.compile(r'^(;?)(SAVEPATH.*)')
                    for line in result:
                        line_c = re.match(pattern2, line)
                        if line_c:
                            if line_c.group(1):
                                if _save_change:
                                    line = 'SAVEPATH = .\\savedataHD\r\n'
                                    _save_change = False
                            else:
                                line = ';'+line
                        f.write(line)

    def windows_xx_tbl2x(self):
        '''
        主要是字体修正
        '''
        keyn_ls = ['size', 'left', 'top', 'width', 'height', 'spacetop', 'spacemiddle', 'spacebottom', 'rubysize']
        windows_xx_ls = [tbl_file for tbl_file in file_list(self.game_data, 'tbl') if os.path.basename(tbl_file).startswith('list_windows_')]
        for tbl_file in windows_xx_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(tbl_file)
            for line in lines:
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*?\W+{keyn}\W+)(\d+)(.*)')
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                result.append(line)
            with open(self.a2p(tbl_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def windwos_tbl2x(self):
        '''
        主要是ui修正，游戏窗口，立绘定位
        '''
        for tbl_file in file_list(self.game_data, 'tbl'):
            if os.path.basename(tbl_file) == 'list_windows.tbl':
                result = []
                lines, current_encoding = self.get_lines_encoding(tbl_file)
                for line in lines:
                    ls1 = ['game_scale', 'game_wasmbar', 'fontsize', 'line_size', 'line_window', 'line_back', 'line_scroll', 'line_name01', 'line_name02']
                    # ls1 = ['game_scale', 'game_wasmbar', 'title_anime', 'fontsize', 'line_size', 'line_window', 'line_back', 'line_scroll', 'line_name01', 'line_name02']
                    for keyn1 in ls1:
                        if line.startswith(keyn1):
                            # pattern_rule1 = rf'({keyn1}\W+?\{)(.*?)(\}.*)'    # 为甚?
                            pattern_rule1 = '('+keyn1+r'\W+?\{'+')'+'(.*?)'+r'(\}.*)'
                            pattern1 = re.compile(pattern_rule1)
                            line_c1 = re.match(pattern1, line)
                            if line_c1:
                                line_ls = list(line_c1.groups())
                                tmp_ls = line_ls[1].split(',')
                                for i in range(len(tmp_ls)):
                                    if real_digit(tmp_ls[i]):
                                        tmp_ls[i] = str(int(int(tmp_ls[i])*self.scale_ratio))
                                line_ls[1] = ','.join(tmp_ls)
                                line = ''.join([i for i in line_ls if i != None])
                    ls2 = ['x', 'y', 'w', 'h', 'r', 'cx', 'cy', 'cw', 'ch', 'fx', 'fy', 'fw', 'fh', 'left', 'top', 'size', 'width', 'height', 'spacetop', 'spacemiddle', 'spacebottom', 'kerning', 'rubysize']
                    for keyn2 in ls2:
                        pattern2 = re.compile(rf'(.*\W+{keyn2}\W+)(\d+)(.*)')
                        line_c2 = re.match(pattern2, line)
                        if line_c2:
                            line = pattern_num2x(line, line_c2, self.scale_ratio)
                    ls3 = ['clip', 'clip_a', 'clip_c', 'clip_d']
                    for keyn3 in ls3:
                        pattern3 = re.compile(rf'(.*\W+{keyn3}\W+?")(.*?)(".*)')
                        line_c3 = re.match(pattern3, line)
                        if line_c3:
                            line_ls = list(line_c3.groups())
                            tmp_ls = line_ls[1].split(',')
                            for i in range(len(tmp_ls)):
                                if real_digit(tmp_ls[i]):
                                    tmp_ls[i] = str(int(int(tmp_ls[i])*self.scale_ratio))
                            line_ls[1] = ','.join(tmp_ls)
                            line = ''.join([i for i in line_ls if i != None])
                    ls4 = ['game_width', 'game_height']
                    for keyn4 in ls4:
                        pattern4 = re.compile(rf'^({keyn4}\W+)(\d+)(.*)')
                        line_c4 = re.match(pattern4, line)
                        if line_c4:
                            line = pattern_num2x(line, line_c4, self.scale_ratio)
                    result.append(line)
                with open(self.a2p(tbl_file), 'w', newline='', encoding=current_encoding) as f:
                    for line in result:
                        f.write(line)
                return

    # def ipt2x(self):
    #     '''
    #     粒子效果显示修正
    #     '''
    #     for ipt_file in file_list(self.game_data, 'ipt'):
    #         result = []
    #         lines, current_encoding = self.get_lines_encoding(ipt_file)
    #         for line in lines:
    #             keyn_ls = ['x', 'y', 'w', 'h', 'ax', 'ay']
    #             for keyn in keyn_ls:
    #                 pattern = re.compile(rf'(.*\W+{keyn}\W+)(\d+)(.*)')
    #                 line_c = re.match(pattern, line)
    #                 if line_c:
    #                     line = pattern_num2x(line, line_c, self.scale_ratio)
    #             result.append(line)
    #         with open(self.a2p(ipt_file), 'w', newline='', encoding=current_encoding) as f:
    #             for line in result:
    #                 f.write(line)

    def ipt2x(self):
        '''
        粒子效果显示修正，部分游戏对话框修正
        '''
        for ipt_file in file_list(self.game_data, 'ipt'):
            result = []
            lines, current_encoding = self.get_lines_encoding(ipt_file)
            for line in lines:
                keyn_ls = ['x', 'y', 'w', 'h', 'ax', 'ay']
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*\W+{keyn}\W+)(\d+)(.*)')
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                pattern2 = re.compile(r'(.*\W+")(\d+.*?)(".*)')
                line_c2 = re.match(pattern2, line)
                if line_c2:
                    line2ls = list(line_c2.groups())
                    num_str_ls = line2ls[1].split(',')
                    for i, num_str in enumerate(num_str_ls):
                        if real_digit(num_str):
                            num_str_ls[i] = str(int(int(num_str)*self.scale_ratio))
                    line2ls[1] = ','.join(num_str_ls)
                    line = ''.join(line2ls)
                result.append(line)
            with open(self.a2p(ipt_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def ast2x(self):
        '''
        人物位置修正，剧本文件
        '''
        for ast_file in file_list(self.game_data, 'ast'):
            result = []
            lines, current_encoding = self.get_lines_encoding(ast_file)
            for line in lines:
                keyn_ls = ['mx', 'my', 'ax', 'ay', 'bx', 'by', 'x', 'y', 'x2', 'y2']
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*\W+{keyn}\W+?)(-?\d+)(.*)')
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                result.append(line)
            with open(self.a2p(ast_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def lua2x(self):
        '''
        部分游戏音量值位置修正
        '''
        for lua_file in file_list(self.game_data, 'lua'):
            lines, current_encoding = self.get_lines_encoding(lua_file)
            result = []
            keyn_ls = ['width', 'height', 'left', 'top', 'x', 'y']
            for line in lines:
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*\W+{keyn}\W+)(\d+)(.*)')
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                result.append(line)
            with open(self.a2p(lua_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    """
    ==================================================
    Artemis引擎图片文件：png(可能包含立绘坐标)
    ==================================================
    """

    def image2x(self):
        self.png2x()

    def png2x(self):
        print('正在复制图片至临时文件夹......')
        for png_file in file_list(self.game_data, 'png'):
            fcopy(png_file, os.path.dirname(self.a2t(png_file)))
        print('图片复制完成，正在放大中......')
        show_image2x_p = Process(target=show_image2x_status, args=(self.tmp_folder, 'png'))
        show_image2x_p.start()
        self.image_scale(self.tmp_folder, output_extention='png')
        show_image2x_p.join()
        print('正在将立绘坐标信息写入到png图片')
        png_text_dict = self.get_all_png_text()
        for png_file, png_text in png_text_dict.items():
            write_png_text(png_file, png_text)
        for png_file in file_list(self.tmp_folder, 'png'):
            fmove(png_file, os.path.dirname(self.t2p(png_file)))
        for folder in os.listdir(self.tmp_folder):
            folder_path = os.path.join(self.tmp_folder, folder)
            shutil.rmtree(folder_path)

    def get_all_png_text(self) -> dict:
        '''
        将含有文本信息的png图片中的坐标放大并保存
        '''
        png_text_dict = {}
        text_png_path_ls = file_list(self.game_data, 'png')
        for png_file in text_png_path_ls:
            # 放大后的png图片在临时文件夹中的路径
            scaled_png_path = self.a2t(png_file)
            # 获取原始图片中的png坐标信息
            png_text = read_png_text(png_file)
            if png_text:
                scaled_png_text = png_text_2x(png_text, self.scale_ratio)
                png_text_dict[scaled_png_path] = scaled_png_text
        return png_text_dict

    """
    ==================================================
    Artemis引擎动画文件：ogv
    ==================================================
    """

    def animation2x(self):
        print('开始处理游戏动画')
        self.ogv2x()

    def ogv2x(self):
        ogv_file_ls = file_list(self.game_data, 'ogv')
        if ogv_file_ls:
            [fcopy(ogv_file, os.path.dirname(self.a2t(ogv_file))) for ogv_file in ogv_file_ls]
            for ogv_file in file_list(self.tmp_folder, 'ogv'):
                tmp_ogv_path = self.video_scale(ogv_file)
                fmove(tmp_ogv_path, os.path.dirname(self.t2p(tmp_ogv_path)))

    """
    ==================================================
    Artemis引擎视频文件：wmv2、dat(wmv3)
    ==================================================
    """

    def video2x(self):
        print('开始处理游戏视频')
        video_extension_ls = ['wmv', 'dat', 'mp4', 'avi', 'mpg']
        for video_extension in video_extension_ls:
            video_file_ls = file_list(self.game_data, video_extension)
            if video_file_ls:
                print(f'{video_extension}视频放大中......')
                for video_file in video_file_ls:
                    if self.get_video_codec(video_file):
                        fcopy(video_file, os.path.dirname(self.a2t(video_file)))
                for video_file in file_list(self.tmp_folder, video_extension):
                    if video_extension == 'dat':
                        os.rename(video_file, video_file.replace('.dat', '.wmv'))
                        video_file = video_file.replace('.dat', '.wmv')
                    output_vcodec = None
                    if self.get_video_codec(video_file) == 'wmv3':
                        output_vcodec = 'wmv2'
                    tmp_video_path = self.video_scale(video_file, output_extension=None, output_vcodec=output_vcodec)
                    if video_extension == 'dat':
                        os.rename(tmp_video_path, tmp_video_path.replace('.wmv', '.dat'))
                        tmp_video_path = tmp_video_path.replace('.wmv', '.dat')
                    fmove(tmp_video_path, os.path.dirname(self.t2p(tmp_video_path)))


def read_png_text(png_file) -> tuple:
    '''
    读取png图片中的立绘坐标信息
    '''
    text_sign = b'tEXt'
    reader = png.Reader(filename=png_file)
    chunks = reader.chunks()
    text_chunk = [chunk for chunk in chunks if chunk[0] == text_sign]
    if text_chunk:
        return text_chunk[0]
    else:
        return None


def png_text_2x(text_chunk, scale_ratio) -> tuple:
    '''
    将png图片中的文本信息中的坐标放大
    '''
    png_text_encoding_ls = ['shift-jis', 'utf-8', 'gbk', 'utf-16', 'CP932']
    text_ls = list(text_chunk)
    text = text_ls[1]
    for png_text_encoding in png_text_encoding_ls:
        try:
            tmp_ls = str(text, png_text_encoding).split(',')
            current_encoding = png_text_encoding
            break
        except:
            continue
    for i in range(len(tmp_ls)):
        if real_digit(tmp_ls[i]):
            tmp_ls[i] = str(int(int(tmp_ls[i])*scale_ratio))
    new_text = ','.join(tmp_ls)
    new_text2bytes = bytes(new_text, current_encoding)
    text_ls[1] = new_text2bytes
    return tuple(text_ls)


def write_png_text(png_file, png_text):
    '''
    将文本信息写入到png图片
    '''
    text_sign = b'tEXt'
    reader = png.Reader(filename=png_file)
    old_chunks = reader.chunks()
    new_chunks = [chunk for chunk in old_chunks if chunk[0] != text_sign]
    new_chunks.insert(1, png_text)
    with open(png_file, 'wb') as f:
        png.write_chunks(f, new_chunks)
