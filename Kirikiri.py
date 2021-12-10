# -*- coding:utf-8 -*-

from Globals import *
from GeneralEngine import GeneralEngine


class Kirikiri(GeneralEngine):
    """Kirikiri 2/Z Engine"""

    def __init__(self, game_data):
        super().__init__(game_data)

        self.patch_folder = os.path.join(os.path.dirname(self.game_data), 'patch')
        self.encoding, self.scwidth, self.scheight = self.get_encoding_resolution()
        self.scale_ratio = self.get_default_scale_ratio()
        self.run_dict = {'script': False, 'ui': False, 'image': False, 'animation': False, 'video': False, 'stand': False, 'tlg5': False}

    def upscale(self):

        self.select2run()
        print('\n', format('开始处理', '=^76'), sep='', end='\n'*2)
        timing_start = time.time()
        if not os.path.exists(self.patch_folder):
            os.mkdir(self.patch_folder)
        if os.path.exists(self.tmp_folder):
            os.rmtree(self.tmp_folder)
        os.mkdir(self.tmp_folder)

        if self.run_dict['script']:
            self.script2x()
            print('脚本文件处理完成')
        if self.run_dict['ui']:
            self.ui2x()
            print('UI文件处理完成')
        if self.run_dict['image']:
            self.image2x()
            print('图片文件放大完成')
        if self.run_dict['animation']:
            self.animation2x()
            print('动画文件处理完成')
        if self.run_dict['video']:
            self.video2x()
            print('视频文件处理完成')
        if self.run_dict['stand']:
            self.stand_correction()
            print('对话框人物立绘手动调整完成')
        if self.run_dict['tlg5']:
            self.tlg6totlg5()
            print('tlg6转换tlg5完成')

        shutil.rmtree(self.tmp_folder)
        timing_count = time.time() - timing_start
        tmp = input(f'\n高清重制完成，共耗时{seconds_format(timing_count)}\n请将patch文件夹打包，放到游戏根目录下(或使用Universal Patch方法)\n按回车键退出：')
        sys.exit()

    def select2run(self):
        selecting = True
        sep_line = '-'*80
        while selecting:
            os.system('cls')
            self.hd_resolution = self.get_hd_resolution()
            print(f'{sep_line}\n检测到游戏引擎为Kirikiri，主要文本编码为：{self.encoding}，原生分辨率为：{self.scwidth}*{self.scheight}\n{sep_line}')
            select_num = input(f'[-1]更改高清重制分辨率：{self.hd_resolution}\n{sep_line}\n[0]一键自动执行\n[1]仅处理脚本文件\n[2]仅处理ui文件\n[3]仅处理游戏图片\n[4]仅处理游戏动画\n[5]仅处理视频文件\n{sep_line}\n高清重制后处理(需要先高清处理获得patch文件夹后再使用)：\n[11]手动调整对话框人物立绘(立绘错位时使用)\n[12]将tlg图片转化为tlg5格式(tlg6不兼容时使用)\n{sep_line}\n[95]显示配置\n[96]修改配置\n[97]重置配置\n[98]开源与第三方软件\n[99]退出程序\n{sep_line}\n请选择(默认一键自动执行)：')
            if select_num == '0':
                for key in self.run_dict.keys():
                    if key not in ['stand', 'tlg5']:
                        self.run_dict[key] = True
            elif select_num == '1':
                self.run_dict['script'] = True
            elif select_num == '2':
                self.run_dict['ui'] = True
            elif select_num == '3':
                self.run_dict['image'] = True
            elif select_num == '4':
                self.run_dict['animation'] = True
            elif select_num == '5':
                self.run_dict['video'] = True
            elif select_num == '11':
                self.run_dict['stand'] = True
            elif select_num == '12':
                self.run_dict['tlg5'] = True

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
                    if key not in ['stand', 'tlg5']:
                        self.run_dict[key] = True
            selecting = False

    def get_encoding_resolution(self):
        '''
        获取文本编码和分辨率
        '''
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
        for tjs_file in tjs_file_ls:
            if os.path.basename(tjs_file) == 'Config.tjs':
                encoding = get_encoding(tjs_file)
                with open(tjs_file, newline='', encoding=encoding) as f:
                    lines = f.readlines()
                    pattern = re.compile(r'(;scWidth|;scHeight)\W+(\d+).*')
                    for line in lines:
                        if line.startswith(';scWidth'):
                            scwidth = int(re.match(pattern, line).group(2))
                        if line.startswith(';scHeight'):
                            scheight = int(re.match(pattern, line).group(2))
                    return encoding, scwidth, scheight

    """
    ==================================================
    Kirikiri引擎脚本文件：tjs, ks, asd, stand
    ==================================================
    """

    def script2x(self):
        self.Config2x()
        self.envinit2x()
        self.customtjs2x()
        self.default2x()
        self.particle2x()
        self.customks2x()
        self.macro2x()
        self.asd2x()
        self.stand2x()

    def Config2x(self):
        '''
        Config.tjs文件处理，游戏分辨率，默认字体等
        '''
        config_dict = {'窗口宽': ';scWidth', '窗口高': ';scHeight', '存档缩略图宽': ';thumbnailWidth',
                       '字体大小1': 'defaultFontSize', '行间距1': 'defaultLineSpacing', '扩展高': ';exHeight',
                       '字体大小2': ';defaultFontSize', '行间距2': ';defaultLineSpacing',
                       '细字大小': ';defaultRubySize', '前景图层位置左': ';scPositionX.left',
                       '前景图层位置中': ';scPositionX.center', '前景图层位置左中': ';scPositionX.left_center',
                       '前景图层位置右': ';scPositionX.right', '前景图层位置右中': ';scPositionX.right_center',
                       '左余白1': ';marginL', '上余白1': ';marginT', '右余白1': ';marginR', '下余白1': ';marginB',
                       '左余白2': 'marginL', '上余白2': 'marginT', '右余白2': 'marginR', '下余白2': 'marginB',
                       '字体高度': ';fontHeight', '行高': ';lineHeight', '标签宽': ';mw', '标签高': ';mh',
                       '点击等待位置左': ';glyphFixedLeft', '点击等待位置上': ';glyphFixedTop', '垂直书写余白': ';marginRCh'}
        # 读取文件，处理数值
        for tjs_file in patch9_first(file_list(self.game_data, 'tjs')):
            if os.path.basename(tjs_file) == 'Config.tjs':
                Config_file = tjs_file
                break
        result = []
        lines, current_encoding = self.get_lines_encoding(Config_file)
        for line in lines:
            for config_c in config_dict.values():
                pattern1 = re.compile(rf'(^{config_c}\W+)(\d+)(\W+)(\d*)(.*)')
                line_c = re.match(pattern1, line)
                if line_c:
                    line = pattern_num2x(line, line_c, self.scale_ratio)
            pattern2 = re.compile(r'(^;mt.*?)(\d+)(.*)')
            line_c = re.match(pattern2, line)
            if line_c:
                line = pattern_num2x(line, line_c, self.scale_ratio)
            result.append(line)
        with open(os.path.join(self.patch_folder, 'Config.tjs'), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                if line.startswith(';saveDataLocation'):
                    continue
                f.write(line)
                # 独立存档位置，避免冲突
                if line.startswith(';freeSaveDataMode'):
                    f.write(';saveDataLocation = "savedataHD";\r\n')

    def envinit2x(self):
        '''
        envinit.tjs文件处理，图层修改，开启对话框头像修正模式
        '''
        pattern_dict = {'amv动画和粒子效果显示层': r'(.*width:)(\d+)(.*height:)(\d+)(.*)(amovie|particle)(.*)',
                        '纯色层1': r'(.*"width", )(\d+)(, "height", )(\d+)(.*color.*)',
                        '纯色层2和motion': r'(^\t*)("width"\D*|"height"\D*)(\d+)(\D*)'}
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
        for tjs_file in tjs_file_ls:
            if os.path.basename(tjs_file) == 'envinit.tjs':
                envinit_file = tjs_file
                break
        result = []
        lines, current_encoding = self.get_lines_encoding(envinit_file)
        for line in lines:
            for i in pattern_dict.values():
                pattern = re.compile(i)
                line_c = re.match(pattern, line)
                if line_c:
                    line = pattern_num2x(line, line_c, self.scale_ratio)
            result.append(line)
        with open(os.path.join(self.patch_folder, 'envinit.tjs'), 'w', newline='', encoding=current_encoding) as f:
            tmp_count = 0
            for line in result:
                # 开启对话框头像位置修正模式
                if 'autoFaceShow' in line and tmp_count == 0:
                    f.write('\t"facePosMode", 1,\r\n')
                    tmp_count = 1
                if line.startswith('\t"facePosMode'):
                    continue
                f.write(line)

    def customtjs2x(self):
        '''
        custom.tjs文件处理，字体大小，间距修改
        '''
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
        for tjs_file in tjs_file_ls:
            if os.path.basename(tjs_file) == 'custom.tjs':
                customtjs_file = tjs_file
                break
        result = []
        pattern_rule_keywords = ['fontheight', 'fontsize', 'linestep', 'linespace', 'linespacing']
        lines, current_encoding = self.get_lines_encoding(customtjs_file)
        for line in lines:
            for rule_keyword in pattern_rule_keywords:
                pattern = re.compile(rf'(.*?\W+)({rule_keyword})(\W+)(\d+)(.*)', re.IGNORECASE)
                line_c = re.match(pattern, line)
                if line_c:
                    line = pattern_num2x(line, line_c, self.scale_ratio)
            result.append(line)
        with open(os.path.join(self.patch_folder, 'custom.tjs'), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def default2x(self):
        '''
        default.tjs文件处理，backlog头像，字体，跳过游戏验证
        '''
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
        for tjs_file in tjs_file_ls:
            if os.path.basename(tjs_file) == 'default.tjs':
                default_file = tjs_file
                break
        result = []
        pattern1 = re.compile(r'(.*FaceThumbRect\W+)(\d+)(\W+)(\d+)(.*)')
        pattern2_rule_keywords = ['ox', 'oy', 'fontheight', 'fontsize', 'linestep', 'marginL', 'marginR', 'marginB', 'marginT', 'linespace', 'linespacing']
        lines, current_encoding = self.get_lines_encoding(default_file)
        for line in lines:
            # backlog头像裁剪
            line_c1 = re.match(pattern1, line)
            if line_c1:
                line = pattern_num2x(line, line_c1, self.scale_ratio)
            # 字体等
            for rule_keyword in pattern2_rule_keywords:
                pattern2 = re.compile(rf'(.*?\W+)({rule_keyword})(\W+)(\d+)(.*)', re.IGNORECASE)
                line_c2 = re.match(pattern2, line)
                if line_c2:
                    line = pattern_num2x(line, line_c2, self.scale_ratio)
            # 跳过验证
            if ('CHECK_PRODUCTKEY' and 'FORCE_PRODUCTKEY') in line:
                break
            result.append(line)
        with open(os.path.join(self.patch_folder, 'default.tjs'), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def particle2x(self):
        '''
        粒子效果修正
        '''
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs', ignored_folders=['sysscn']))
        particle_file_ls = [tjs_file for tjs_file in tjs_file_ls if 'particle' in tjs_file]
        for particle_file in particle_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(particle_file)
            for line in lines:
                # 生成位置
                if 'genpos' in line:
                    pattern1 = re.compile(
                        r'(.*genpos)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)(.*)')
                    line_c = re.match(pattern1, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                # 死亡判定
                if 'term' in line:
                    pattern2 = re.compile(
                        r'(.*return)([\D]*)(\d+)([\D]*)([\d]*)([\D]*)')
                    line_c = re.match(pattern2, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                result.append(line)
            with open(os.path.join(self.patch_folder, os.path.basename(particle_file)), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def customks2x(self):
        '''
        custom.ks文件处理，选择肢修正
        '''
        ks_file_ls = patch9_first(file_list(self.game_data, 'ks'))
        for ks_file in ks_file_ls:
            if os.path.basename(ks_file) == 'custom.ks':
                customks_file = ks_file
                break
        result = []
        lines, current_encoding = self.get_lines_encoding(customks_file)
        for line in lines:
            # 选择肢位置、大小修正
            if 'select_normal' in line:
                pattern = re.compile(
                    r'(.*left\W+)(\d+)(.*top\W+)(\d+)(.*width\W+)(\d+)(.*height\W+)(\d+)(.*)')
                line_c = re.match(pattern, line)
                if line_c:
                    line = pattern_num2x(line, line_c, self.scale_ratio)
            result.append(line)
        with open(os.path.join(self.patch_folder, 'custom.ks'), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def macro2x(self):
        '''
        macro.ks文件处理，自定义宏
        '''
        macro_ls = ['macro.ks', 'macro_old.ks']
        ks_file_ls = patch9_first(file_list(self.game_data, 'ks'))
        for ks_file in ks_file_ls:
            if os.path.basename(ks_file) in macro_ls:
                macro_file = ks_file
                keyn_ls = ['xpos', 'width', 'height', 'ypos', 'movex', 'movey', 'zoom', 'movx', 'movy', 'shiftx', 'shifty', 'camerazoom']
                result = []
                lines, current_encoding = self.get_lines_encoding(macro_file)
                for line in lines:
                    for keyn in keyn_ls:
                        pattern_rule = rf'(.*?)({keyn})(\W+)(\d+)(\W+)(\d*)(.*)'
                        pattern = re.compile(pattern_rule, re.IGNORECASE)
                        line_c = re.match(pattern, line)
                        if line_c:
                            line = pattern_num2x(line, line_c, self.scale_ratio)
                    result.append(line)
                with open(os.path.join(self.patch_folder, os.path.basename(ks_file)), 'w', newline='', encoding=current_encoding) as f:
                    for line in result:
                        f.write(line)

    def asd2x(self):
        '''
        人物表情、sd动画、对话框上的等待点击效果、进度条
        '''
        asd_keyword_list = ['clipleft', 'cliptop', 'clipwidth', 'clipheight', 'left',
                            'top', 'height', 'weight', 'dx', 'dy', 'dw', 'dh', 'sx', 'sy', 'sw', 'sh', 'x', 'y']
        # 忽略人物表情处理，这东西不需要改，改了反而不正常
        asd_file_ls = patch9_first(file_list(self.game_data, 'asd', ignored_folders=['emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
        for asd_file in asd_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(asd_file)
            for line in lines:
                line = line.replace('\r\n', '')
                tmp_ls = line.split(' ')
                for i in range(len(tmp_ls)):
                    for asd_keyword in asd_keyword_list:
                        if tmp_ls[i].startswith(asd_keyword + '='):
                            tmp = tmp_ls[i].split('=')
                            if real_digit(tmp[-1]):
                                tmp[-1] = str(int(float(tmp[-1]) * self.scale_ratio))
                            tmp_ls[i] = '='.join(tmp)
                line = ' '.join(tmp_ls) + '\r\n'
                result.append(line)
            with open(os.path.join(self.patch_folder, os.path.basename(asd_file)), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def stand2x(self):
        '''
        对话框头像大小、位置修正
        '''
        stand_file_ls = patch9_first(file_list(self.game_data, 'stand'))
        for stand_file in stand_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(stand_file)
            pattern = re.compile(r'(.*?)(-?\d+)(.*)')
            for line in lines:
                # 水平方向位置修正
                if 'facexoff' in line:
                    line_c = re.match(pattern, line)
                    if line_c:
                        line_cc = list(line_c.groups())
                        line_cc[1] = str(int(line_cc[1]) - int((self.scwidth*self.scale_ratio-self.scwidth)/2))
                        line_cc = [i for i in line_cc if i != None]
                        line = ''.join(line_cc)
                # 大小修正
                if 'facezoom' in line:
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, self.scale_ratio)
                result.append(line)
            with open(os.path.join(self.patch_folder, os.path.basename(stand_file)), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def stand_correction(self):
        '''
        对话框人物立绘后处理
        '''
        xpos_move = int(input('请输入向右移动像素距离：'))
        face_zoom = float(input('请输入人物头像缩放系数：'))
        stand_file_ls = file_list(self.patch_folder, 'stand')
        pattern = re.compile(r'(.*?)(-?\d+)(.*)')
        for stand_file in stand_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(stand_file)
            for line in lines:
                # 水平方向位置修正
                if 'facexoff' in line:
                    line_c = re.match(pattern, line)
                    if line_c:
                        line_cc = list(line_c.groups())
                        line_cc[1] = str(int(line_cc[1]) + xpos_move)
                        line_cc = [i for i in line_cc if i != None]
                        line = ''.join(line_cc)
                # 大小修正
                if 'facezoom' in line:
                    line_c = re.match(pattern, line)
                    if line_c:
                        line = pattern_num2x(line, line_c, face_zoom)
                result.append(line)
            with open(os.path.join(self.patch_folder, os.path.basename(stand_file)), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    """
    ==================================================
    Kirikiri引擎游戏UI文件：pimg, png, csv
    ==================================================
    """

    def ui2x(self):
        print('开始处理UI文件')
        self.uipsd_folder = os.path.join(self.tmp_folder, 'uipsd')
        os.mkdir(self.uipsd_folder)
        # 重复uipsd文件夹合并
        uipsd_file_ls = []
        for root, folders, files in os.walk(self.game_data):
            if os.path.basename(root) == 'uipsd':
                for folder in folders:
                    uipsd_file_ls += file_list(os.path.join(root, folder))
                for file in files:
                    uipsd_file_ls.append(os.path.join(root, file))
        [fcopy(uipsd_file, self.uipsd_folder) for uipsd_file in patch9_first(uipsd_file_ls)]
        # 额外pimg文件
        extra_pimg_file_ls = patch9_first(file_list(self.game_data, 'pimg', ignored_folders=['uipsd']))
        [fcopy(pimg_file, self.uipsd_folder) for pimg_file in extra_pimg_file_ls]
        self.csv2x()
        self.pimg_folder = self.uipsd_folder
        self.pimg2x()
        for uipng_file in file_list(self.uipsd_folder, 'png', walk_mode=False):
            fmove(uipng_file, self.patch_folder)
        shutil.rmtree(self.uipsd_folder)

    def csv2x(self):
        '''
        csv文件处理：将csv文件中的数字项乘以n
        '''
        for csv_file in file_list(self.uipsd_folder, 'csv'):
            result = []
            try:
                with open(csv_file, newline='', encoding=self.encoding) as f:
                    content = csv.reader(f)
                    current_encoding = self.encoding
                    for content_ls in content:
                        for i in range(len(content_ls)):
                            if real_digit(content_ls[i]):
                                content_ls[i] = str(int(float(content_ls[i]) * self.scale_ratio))
                        result.append(content_ls)
            except UnicodeDecodeError:
                current_encoding = get_encoding(csv_file)
                with open(csv_file, newline='', encoding=current_encoding) as f:
                    content = csv.reader(f)
                    for content_ls in content:
                        for i in range(len(content_ls)):
                            if real_digit(content_ls[i]):
                                content_ls[i] = str(int(float(content_ls[i]) * self.scale_ratio))
                        result.append(content_ls)
            with open(os.path.join(self.patch_folder, os.path.basename(csv_file)), 'w', newline='', encoding=current_encoding) as f:
                content2x = csv.writer(f)
                content2x.writerows(result)

    def pimg2x(self):
        pimg_file_ls = file_list(self.pimg_folder, 'pimg')
        print('正在拆分pimg文件')
        pimg_de_pool = Pool(self.cpu_cores)
        for pimg_file in pimg_file_ls:
            pimg_de_pool.apply_async(self.pimg_de, args=(pimg_file,))
        pimg_de_pool.close()
        pimg_de_pool.join()
        print('pimg文件拆分完成')
        self.json2x()
        print('pimg坐标修正完成')
        print('pimg图片放大中......')
        show_ui2x_p = Process(target=show_image2x_status, args=(self.pimg_folder, 'png'))
        show_ui2x_p.start()
        self.image_scale(self.pimg_folder, output_extention='png')
        show_ui2x_p.join()
        print('pimg图片放大完成，正在组装中......')
        pimg_en_pool = Pool(self.cpu_cores)
        for json_file in [pimg_file.replace('.pimg', '.json') for pimg_file in pimg_file_ls]:
            pimg_en_pool.apply_async(self.pimg_en, args=(json_file,))
        pimg_en_pool.close()
        pimg_en_pool.join()
        [os.rename(pimg_file, pimg_file.replace('.pure', '')) for pimg_file in file_list('.\\', 'pimg', walk_mode=False)]
        print('pimg文件组装完成')
        [fmove(pimg_file, self.patch_folder) for pimg_file in file_list('.\\', 'pimg', walk_mode=False)]

    def pimg_de(self, pimg_file):
        '''
        拆分pimg文件
        '''
        pimg_de_p = subprocess.run([self.psb_de_exe, pimg_file], capture_output=True)

    def pimg_en(self, json_file):
        '''
        组装pimg文件
        '''
        pimg_en_p = subprocess.run([self.psb_en_exe, json_file], capture_output=True)

    def json2x(self):
        '''
        pimg坐标修正
        '''
        keyn_ls = ['height', 'width', 'left', 'top']
        for json_file in file_list(self.pimg_folder, 'json'):
            with open(json_file, encoding='utf-8') as f:
                # 读取文件内容
                content = json.load(f)
                # layer项外的替换
                for keyn in keyn_ls:
                    if keyn in content.keys():
                        content[keyn] = int(content[keyn] * self.scale_ratio)
                # layer项内的替换
                if 'layers' in content.keys():
                    layer_ls = content['layers']
                    for dict1 in layer_ls:
                        for keyn in keyn_ls:
                            if keyn in dict1.keys():
                                dict1[keyn] = int(dict1[keyn] * self.scale_ratio)
            # 美化输出
            result = json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False)
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(result)

    """
    ==================================================
    Kirikiri引擎图片文件：tlg, png, jpg, jpeg, bmp, eri
    ==================================================
    """

    def image2x(self):
        print('开始放大图片，处理时间较长，请耐心等待......')
        self.general_image2x()
        print('常规图片处理完成，开始处理tlg图片......')
        self.tlg_folder = os.path.join(self.tmp_folder, 'tlg')
        os.mkdir(self.tlg_folder)
        [fcopy(tlg_file, self.tlg_folder) for tlg_file in patch9_first(file_list(self.game_data, 'tlg', ignored_folders=['fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))]
        self.tlg2x()
        shutil.rmtree(self.tlg_folder)

    def general_image2x(self):
        '''
        对常规格式图片进行放大处理
        '''
        image_extension_ls = ['bmp', 'jpg', 'jpeg', 'png']
        for image_extension in image_extension_ls:
            image_file_list = patch9_first(file_list(self.game_data, image_extension, ignored_folders=['uipsd', 'sysscn', 'fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
            if image_file_list:
                image_folder = os.path.join(self.tmp_folder, image_extension)
                os.mkdir(image_folder)
                [fcopy(image_file, image_folder) for image_file in image_file_list]
                print(f'开始放大{image_extension}图片......')
                show_image2x_p = Process(target=show_image2x_status, args=(image_folder, image_extension))
                show_image2x_p.start()
                self.image_scale(image_folder, output_extention=image_extension)
                show_image2x_p.join()
                [fmove(image_file, self.patch_folder) for image_file in file_list(image_folder, image_extension)]
                shutil.rmtree(image_folder)

    def tlg2x(self):
        '''
        对tlg格式图片进行放大处理
        '''
        tlg_file_ls = file_list(self.tlg_folder, 'tlg')
        if tlg_file_ls:
            print('tlg图片转换中......')
            tlg2png_pool = Pool(self.cpu_cores)
            for tlg_file in tlg_file_ls:
                tlg2png_pool.apply_async(self.tlg2png, args=(tlg_file,))
            tlg2png_pool.close()
            tlg2png_pool.join()
            [os.remove(tlg_file) for tlg_file in tlg_file_ls]
            print('tlg转换完成，正在放大中......')
            show_tlg2x_p = Process(target=show_image2x_status, args=(self.tlg_folder, 'png'))
            show_tlg2x_p.start()
            self.image_scale(self.tlg_folder, output_extention='png')
            show_tlg2x_p.join()
            print('tlg格式图片放大完成，正在进行格式转换......')
            png2tlg6_pool = Pool(self.cpu_cores)
            for png_file in file_list(self.tlg_folder, 'png'):
                png2tlg6_pool.apply_async(self.png2tlg6, args=(png_file,))
            png2tlg6_pool.close()
            png2tlg6_pool.join()
            [fmove(tlg_file, self.patch_folder) for tlg_file in tlg_file_ls]
        else:
            print('未发现需要处理的tlg图片')

    def tlg2png(self, tlg_file):
        '''
        将tlg图片转化为png格式
        '''
        tlg2png_p = subprocess.run([self.tlg2png_exe, tlg_file, tlg_file.replace('.tlg', '.png')], capture_output=True)

    def png2tlg6(self, png_file):
        '''
        将png图片转化为tlg6格式，适用于krkr2.24及以上版本
        '''
        png2tlg6_p = subprocess.run([self.png2tlg6_exe, png_file, png_file.replace('.png', '.tlg')], capture_output=True)

    def png2tlg5(self):
        '''
        将png图片转换回tlg5格式，手动处理，兼容性好
        '''
        print('请将弹出文件夹中的png图片拖入吉里吉里图像转换器窗口\n不要修改选项，确认处理完成后关闭吉里吉里图像转换器')
        os.system(f'start {self.tlg5_folder}')
        os.system(self.krkrtpc_exe)

    def tlg6totlg5(self):
        '''
        tlg6不兼容时后处理
        '''
        tlg_file_ls = file_list(self.patch_folder, 'tlg')
        if tlg_file_ls:
            self.tlg5_folder = os.path.join(self.patch_folder, 'tlg5')
            os.mkdir(self.tlg5_folder)
            print('tlg图片转换中......')
            tlg2png_pool = Pool(self.cpu_cores)
            for tlg_file in tlg_file_ls:
                tlg2png_pool.apply_async(self.tlg2png, args=(tlg_file,))
            tlg2png_pool.close()
            tlg2png_pool.join()
            [os.remove(tlg_file) for tlg_file in tlg_file_ls]
            [fmove(tlg2png_file.replace('.tlg', '.png'), self.tlg5_folder) for tlg2png_file in tlg_file_ls]
            self.png2tlg5()
            [fmove(tlg_file, self.patch_folder) for tlg_file in file_list(self.tlg5_folder, 'tlg')]
            shutil.rmtree(self.tlg5_folder)
        else:
            print('未发现需要处理的tlg图片')

    def eri2x(self):
        print('暂不支持eri图片格式')

    """
    ==================================================
    Kirikiri引擎动画文件：amv, psb, swf
    ==================================================
    """

    def animation2x(self):
        print('开始处理游戏动画......')
        self.amv2x()
        self.psb2x()
        self.swf2x()

    def psb2x(self):
        psb_file_ls = file_list(self.game_data, 'psb')
        if psb_file_ls:
            print('暂不支持psb文件处理，后续会加进去')
            pass

    def swf2x(self):
        swf_file_ls = file_list(self.game_data, 'swf')
        if swf_file_ls:
            print('swf这东西没见过有游戏用过，有需求再加进去')

    def amv2x(self):
        '''
        放大amv视频
        '''
        # 改名并储存，防止非转区运行时报错
        old_amv_name_ls = []
        new_amv_name_ls = []
        tmp_count = 1
        for amv_file in patch9_first(file_list(self.game_data, 'amv', ignored_folders=['emotion', 'emotions', 'Emotion', 'Emotions', 'anim'])):
            old_amv_name_ls.append(os.path.basename(amv_file))
            new_amv_name = '%03d.amv' % tmp_count
            new_amv_name_ls.append(new_amv_name)
            shutil.copyfile(amv_file, os.path.join(self.amv_de_folder, new_amv_name))
            tmp_count += 1
        old_new_amv_name_zip = zip(old_amv_name_ls, new_amv_name_ls)
        print('AMV动画拆帧中......')
        amv_file_ls = file_list(self.amv_de_folder, 'amv')
        amv_de_pool = Pool(self.cpu_cores)
        for amv_file in amv_file_ls:
            amv_de_pool.apply_async(self.amv_de, args=(amv_file,))
        amv_de_pool.close()
        amv_de_pool.join()
        [os.remove(amv_file) for amv_file in amv_file_ls]
        # 将拆帧得到的图片移动到临时文件夹
        amv_folder = os.path.join(self.tmp_folder, 'amv')
        os.mkdir(amv_folder)
        input_output_zip = self.format_amv_io(old_new_amv_name_zip, amv_folder)
        print('AMV动画拆帧完成，正在放大中......')
        show_amv2x_p = Process(target=show_image2x_status, args=(amv_folder, 'png'))
        show_amv2x_p.start()
        self.image_scale(amv_folder, output_extention='png')
        show_amv2x_p.join()
        print('AMV图片放大完成，正在组装中......')
        amv_en_pool = Pool(self.cpu_cores)
        for png_sequence, output_amv in input_output_zip:
            amv_en_pool.apply_async(self.amv_en, args=(png_sequence, output_amv))
        amv_en_pool.close()
        amv_en_pool.join()
        shutil.rmtree(amv_folder)
        print('AMV动画组装完成')

    def amv_de(self, amv_file):
        '''
        拆分amv动画为png序列
        '''
        amv_de_p = subprocess.run([self.amv_de_exe, '-amvpath='+amv_file], capture_output=True)

    def amv_en(self, png_sequence, output_amv):
        '''
        将png序列合并为amv动画
        '''
        amv_en_p = subprocess.run([self.amv_en_exe, '--quality', '100', png_sequence, output_amv], capture_output=True)

    def format_amv_io(self, old_new_amv_name_zip, amv_folder) -> zip:
        '''
        返回png序列和输出amv动画的路径
        '''
        png_sequence_ls = []
        output_amv_ls = []
        for old_amv_name, new_amv_name in old_new_amv_name_zip:
            png_sequence = os.path.join(amv_folder, old_amv_name.replace('.amv', ''))
            output_amv = os.path.join(self.patch_folder, old_amv_name)
            if not os.path.exists(png_sequence):
                os.mkdir(png_sequence)
            for png_file in file_list(self.amv_de_folder, 'png'):
                name_ori = os.path.basename(png_file).replace('.png', '')
                name_part_ls = name_ori.split('_')
                if name_part_ls[0]+'.amv' == new_amv_name:
                    name_part_ls[1] = '%04d' % int(name_part_ls[1])
                    name_fmt = ''.join(name_part_ls)+'.png'
                    tmp_path = os.path.join(self.amv_de_folder, name_fmt)
                    os.rename(png_file, tmp_path)
                    fmove(tmp_path, png_sequence)
            png_sequence_ls.append(png_sequence)
            output_amv_ls.append(output_amv)
        return zip(png_sequence_ls, output_amv_ls)

    """
    ==================================================
    Kirikiri引擎视频文件：mpg, mpeg, wmv, avi
    ==================================================
    """

    def video2x(self):
        print('开始处理游戏视频......')
        video_extension_ls = ['mpg', 'mpeg', 'wmv', 'avi']
        for video_extension in video_extension_ls:
            video_folder = os.path.join(self.tmp_folder, video_extension)
            video_ls = file_list(self.game_data, video_extension)
            if video_ls:
                print(f'{video_extension}视频放大中......')
                os.mkdir(video_folder)
                [fcopy(video_file, video_folder) for video_file in video_ls]
                for video_file in file_list(video_folder, video_extension):
                    output_vcodec = None
                    if self.get_video_codec(video_file) == 'wmv3':
                        output_vcodec = 'wmv2'
                    tmp_video_path = self.video_scale(video_file, output_extension=None, output_vcodec=output_vcodec)
                    fmove(tmp_video_path, self.patch_folder)
                shutil.rmtree(video_folder)


def patch9_first(file_ls) -> list:
    '''
    适用于Kirikiri 2/Z Engine引擎：如果存在重复文件，文件优先级依次从patch9文件夹到patch文件夹
    '''
    new_file_ls = []
    for i in file_ls:
        still_alive = True
        for j in file_ls:
            if os.path.basename(j) == os.path.basename(i):
                if 'patch' in os.path.dirname(j):
                    if 'patch' in os.path.dirname(i):
                        if os.path.dirname(j) > os.path.dirname(i):
                            still_alive = False
                    else:
                        still_alive = False
        if still_alive == True:
            new_file_ls.append(i)
    return new_file_ls
