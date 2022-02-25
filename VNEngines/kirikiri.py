# -*- coding:utf-8 -*-

from Core import *


class Kirikiri(Core):
    """Kirikiri 2/Z Engine"""

    def __init__(self):
        Core.__init__(self)
        self.load_config()
        # 连接ui并统计进度
        self.has_connected_ui = False
        self.count_class = None
        self._count_process = 0
        self.run_dict = {'script': False, 'image': False, 'animation': False, 'video': False}
        self.keep_path_struct_mode = True

    def set_game_data(self, game_data, patch_folder):
        self.game_data = Path(game_data).resolve()
        self.patch_folder = Path(patch_folder).resolve()
        self.tmp_folder = self.game_data.parent/'vnc_tmp'
        self.tmp_clear()

    def set_resolution_encoding(self, scwidth, scheight, encoding):
        self.scwidth = scwidth
        self.scheight = scheight
        self.encoding = encoding

    def connect_ui_runner(self, ui_runner):
        global _ui_runner_
        _ui_runner_ = ui_runner
        self.has_connected_ui = True
        self.count_class = self

    def emit_info(self, info_str):
        if self.has_connected_ui:
            _ui_runner_.info_sig.emit(info_str)
        else:
            print(info_str)

    def generate_upscale_file_count(self):
        self.emit_info('正在生成处理列表......')
        self._upscale_file_count = 0
        if self.run_dict['script']:
            tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
            self._upscale_file_count += len(tjs_file_ls)

            ks_file_ls = patch9_first(file_list(self.game_data, 'ks'))
            self._upscale_file_count += len(ks_file_ls)
            uicsv_file_ls = patch9_first(file_list(self.game_data, 'csv', parent_folder='uipsd'))
            self._upscale_file_count += len(uicsv_file_ls)
            asd_file_ls = patch9_first(file_list(self.game_data, 'asd', ignored_folders=['emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
            self._upscale_file_count += len(asd_file_ls)
            stand_file_ls = patch9_first(file_list(self.game_data, 'stand'))
            self._upscale_file_count += len(stand_file_ls)
            ori_scn_file_ls = patch9_first(file_list(self.game_data, 'scn'))
            self._upscale_file_count += len(ori_scn_file_ls)

        if self.run_dict['image']:
            image_extension_ls = ['bmp', 'jpg', 'jpeg', 'png', 'webp']
            for image_extension in image_extension_ls:
                image_file_list = patch9_first(file_list(self.game_data, image_extension, ignored_folders=['sysscn', 'fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
                self._upscale_file_count += len(image_file_list)

            org_pimg_file_ls = patch9_first(file_list(self.game_data, 'pimg'))
            self._upscale_file_count += len(org_pimg_file_ls)

            ori_tlg_file_ls = patch9_first(file_list(self.game_data, 'tlg', ignored_folders=['fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
            self._upscale_file_count += len(ori_tlg_file_ls)

        if self.run_dict['animation']:
            ori_amv_file_ls = patch9_first(file_list(self.game_data, 'amv'))
            self._upscale_file_count += len(ori_amv_file_ls)

        if self.run_dict['video']:
            video_extension_ls = ['mpg', 'mpeg', 'wmv', 'avi', 'mkv']
            for video_extension in video_extension_ls:
                org_video_ls = patch9_first(file_list(self.game_data, video_extension))
                self._upscale_file_count += len(org_video_ls)

    def upscale(self):
        # 计时
        start_time = time.time()
        # 创建补丁文件夹和临时文件夹
        if not self.patch_folder.exists():
            self.patch_folder.mkdir(parents=True)
        self.tmp_clear()
        # 进度统计
        self.generate_upscale_file_count()
        self._count_process = 0
        # 更新进度
        update_process_thread = Thread(target=self.update_vn_upscale_process)
        update_process_thread.start()
        # 开始放大
        self._upscale()
        update_process_thread.join()
        # 删除临时文件夹
        if self.tmp_folder.exists():
            shutil.rmtree(self.tmp_folder)
        # 将文件平铺
        if not self.keep_path_struct_mode:
            flat_folder_(self.patch_folder, del_folder=True)
        timing_count = time.time() - start_time
        self.emit_info(f'共耗时：{seconds_format(timing_count)}')

    def update_vn_upscale_process(self):
        """
        @brief      更新进度，需在子线程内启动
        """
        if self._upscale_file_count == 0:
            now_percent = 1
            print(f'未发现需要处理的文件')
        else:
            now_percent = 0
        while now_percent < 100:
            now_percent = int(self._count_process/self._upscale_file_count*100)
            # 发送信号到ui
            if self.has_connected_ui:
                _ui_runner_.progress_sig.emit(now_percent)
            else:
                print(f'进度：->{now_percent}%<-')
            time.sleep(2)

    def _upscale(self):
        if self.run_dict['script']:
            self.script2x()
            self.emit_info('脚本文件处理完成')
        if self.run_dict['image']:
            self.image2x()
            self.emit_info('图片文件放大完成')
        if self.run_dict['animation']:
            self.animation2x()
            self.emit_info('动画文件处理完成')
        if self.run_dict['video']:
            self.video2x()
            self.emit_info('视频文件处理完成')

    def get_resolution_encoding(self, input_folder):
        '''
        获取文本编码和分辨率
        '''
        input_folder = Path(input_folder).resolve()
        tjs_file_ls = patch9_first(file_list(input_folder, 'tjs'))
        for tjs_file in tjs_file_ls:
            if tjs_file.name == 'Config.tjs':
                encoding = self.get_encoding(tjs_file)
                with open(tjs_file, newline='', encoding=encoding) as f:
                    lines = f.readlines()
                    pattern = re.compile(r'(;scWidth|;scHeight)\W+(\d+).*')
                    for line in lines:
                        if line.startswith(';scWidth'):
                            scwidth = int(re.match(pattern, line).group(2))
                        if line.startswith(';scHeight'):
                            scheight = int(re.match(pattern, line).group(2))
                break
        return scwidth, scheight, encoding

    def flat_kirikiri_patch_folder(self, input_folder, output_folder):
        input_folder = Path(input_folder).resolve()
        output_folder = Path(output_folder).resolve()
        self.emit_info('正在计算文件优先级......')
        patch_file_ls = patch9_first(file_list(input_folder))
        if patch_file_ls:
            patch_ls_len = len(patch_file_ls)
            for count, file in enumerate(patch_file_ls, start=1):
                target_file_path = fcopy(file, output_folder)
                self.emit_info(f'{target_file_path} saved!')
                if self.has_connected_ui:
                    progress_percentage = int(count/patch_ls_len*100)
                    _ui_runner_.progress_sig.emit(progress_percentage)
        else:
            if self.has_connected_ui:
                _ui_runner_.progress_sig.emit(100)

    """
    ==================================================
    Kirikiri引擎脚本文件：tjs, ks, csv, asd, stand, scn
    ==================================================
    """

    def script2x(self):
        self.emit_info('开始处理游戏脚本......')
        self.tjs2x()
        self.ks2x()
        self.uicsv2x()
        self.asd2x()
        self.stand2x()
        self.scn2x()

    def tjs2x(self):
        tjs_file_ls = patch9_first(file_list(self.game_data, 'tjs'))
        for tjs_file in tjs_file_ls:
            if tjs_file.name == 'Config.tjs':
                self.Configtjs2x(tjs_file)
            elif tjs_file.name == 'envinit.tjs':
                self.envinit2x(tjs_file)
            elif tjs_file.name == 'custom.tjs':
                self.customtjs2x(tjs_file)
            elif tjs_file.name == 'default.tjs':
                self.default2x(tjs_file)
            elif 'particle' in tjs_file.name:
                self.particle2x(tjs_file)
            else:
                try:
                    pass
                except:
                    pass
            self._count_process += 1

    def ks2x(self):
        ks_file_ls = patch9_first(file_list(self.game_data, 'ks'))
        for ks_file in ks_file_ls:
            if ks_file.name == 'custom.ks':
                self.customks2x(ks_file)
            elif ks_file.name in ['macro.ks', 'macro_old.ks']:
                self.macro2x(ks_file)
            else:
                try:
                    pass
                except:
                    pass
            self._count_process += 1

    def Configtjs2x(self, tjs_file):
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
        result = []
        lines, current_encoding = self.get_lines_encoding(tjs_file)
        for line in lines:
            for config_c in config_dict.values():
                pattern1 = re.compile(rf'(^{config_c}\W+)(\d+)(\W+)(\d*)(.*)')
                re_result = re.match(pattern1, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            pattern2 = re.compile(r'(^;mt.*?)(\d+)(.*)')
            re_result = re.match(pattern2, line)
            if re_result:
                line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(tjs_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                if line.startswith(';saveDataLocation'):
                    continue
                f.write(line)
                # 独立存档位置
                if line.startswith(';freeSaveDataMode'):
                    f.write(';saveDataLocation = "savedataHD";\r\n')

    def envinit2x(self, tjs_file):
        '''
        envinit.tjs文件处理，图层修改，开启对话框头像修正模式
        '''
        pattern_dict = {'amv动画和粒子效果显示层': r'(.*width:)(\d+)(.*height:)(\d+)(.*)(amovie|particle)(.*)',
                        '纯色层1': r'(.*"width", )(\d+)(, "height", )(\d+)(.*color.*)',
                        '纯色层2和motion': r'(^\t*)("width"\D*|"height"\D*)(\d+)(\D*)'}
        result = []
        lines, current_encoding = self.get_lines_encoding(tjs_file)
        for line in lines:
            for i in pattern_dict.values():
                pattern = re.compile(i)
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(tjs_file), 'w', newline='', encoding=current_encoding) as f:
            tmp_count = 0
            for line in result:
                # 开启对话框头像位置修正模式，使对stand文件的修改生效
                if 'autoFaceShow' in line and tmp_count == 0:
                    f.write('\t"facePosMode", 1,\r\n')
                    tmp_count = 1
                if line.startswith('\t"facePosMode'):
                    continue
                f.write(line)

    def customtjs2x(self, tjs_file):
        '''
        custom.tjs文件处理，字体大小，间距修改
        '''
        result = []
        pattern_rule_keywords = ['fontheight', 'fontsize', 'linestep', 'linespace', 'linespacing']
        lines, current_encoding = self.get_lines_encoding(tjs_file)
        for line in lines:
            for rule_keyword in pattern_rule_keywords:
                pattern = re.compile(rf'(.*?\W+)({rule_keyword})(\W+)(\d+)(.*)', re.IGNORECASE)
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(tjs_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def default2x(self, tjs_file):
        '''
        default.tjs文件处理，backlog头像，字体，跳过游戏验证
        '''
        result = []
        pattern1 = re.compile(r'(.*FaceThumbRect\W+)(\d+)(\W+)(\d+)(.*)')
        pattern2_rule_keywords = ['ox', 'oy', 'fontheight', 'fontsize', 'linestep', 'marginL', 'marginR', 'marginB', 'marginT', 'linespace', 'linespacing']
        lines, current_encoding = self.get_lines_encoding(tjs_file)
        for line in lines:
            # backlog头像裁剪
            re_result1 = re.match(pattern1, line)
            if re_result1:
                line = self.line_pattern_num2x(re_result1)
            # 字体等
            for rule_keyword in pattern2_rule_keywords:
                pattern2 = re.compile(rf'(.*?\W+)({rule_keyword})(\W+)(\d+)(.*)', re.IGNORECASE)
                re_result2 = re.match(pattern2, line)
                if re_result2:
                    line = self.line_pattern_num2x(re_result2)
            # 跳过验证
            if ('CHECK_PRODUCTKEY' and 'FORCE_PRODUCTKEY') in line:
                break
            result.append(line)
        with open(self.a2p(tjs_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def particle2x(self, tjs_file):
        '''
        粒子效果修正
        '''
        result = []
        lines, current_encoding = self.get_lines_encoding(tjs_file)
        for line in lines:
            # 生成位置
            if 'genpos' in line:
                pattern1 = re.compile(
                    r'(.*genpos)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)(.*)')
                re_result = re.match(pattern1, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            # 死亡判定
            if 'term' in line:
                pattern2 = re.compile(
                    r'(.*return)([\D]*)(\d+)([\D]*)([\d]*)([\D]*)')
                re_result = re.match(pattern2, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(tjs_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def customks2x(self, ks_file):
        '''
        custom.ks文件处理，选择肢修正
        '''
        result = []
        lines, current_encoding = self.get_lines_encoding(ks_file)
        for line in lines:
            # 选择肢位置、大小修正
            if 'select_normal' in line:
                pattern = re.compile(
                    r'(.*left\W+)(\d+)(.*top\W+)(\d+)(.*width\W+)(\d+)(.*height\W+)(\d+)(.*)')
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(ks_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def macro2x(self, ks_file):
        '''
        macro.ks文件处理，自定义宏
        '''
        keyn_ls = ['xpos', 'width', 'height', 'ypos', 'movex', 'movey', 'zoom', 'movx', 'movy', 'shiftx', 'shifty', 'camerazoom']
        result = []
        lines, current_encoding = self.get_lines_encoding(ks_file)
        for line in lines:
            for keyn in keyn_ls:
                pattern_rule = rf'(.*?)({keyn})(\W+)(\d+)(\W+)(\d*)(.*)'
                pattern = re.compile(pattern_rule, re.IGNORECASE)
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(ks_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def uicsv2x(self):
        '''
        ui相关csv文件中的坐标处理
        '''
        uicsv_file_ls = patch9_first(file_list(self.game_data, 'csv', parent_folder='uipsd'))
        for input_csv in uicsv_file_ls:
            output_csv = self.a2p(input_csv)
            self.csv2x(input_csv, output_csv, self.scale_ratio)
            self._count_process += 1

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
            with open(self.a2p(asd_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)
            self._count_process += 1

    def scn2x(self):
        ori_scn_file_ls = patch9_first(file_list(self.game_data, 'scn'))
        if ori_scn_file_ls:
            scn_file_ls = [fcopy(scn_file, self.a2t(scn_file).parent) for scn_file in ori_scn_file_ls]
            self.emit_info('开始拆分scn')
            self.pool_run(self.scn_de, scn_file_ls)
            # 获得json文件列表并删除原scn
            scn_json_file_ls = []
            for scn_file in scn_file_ls:
                scn_json_file_ls.append(scn_file.with_suffix('.json'))
                scn_file.unlink()
            self.emit_info('开始处理scn坐标')
            self.pool_run(self.scn_json2x_, scn_json_file_ls)
            self.emit_info('开始合并scn')
            scn_json_files_and_output_folders = [(scn_json_file, scn_json_file.parent) for scn_json_file in scn_json_file_ls]
            scaled_scn_file_ls = self.pool_run(self.scn_en, scn_json_files_and_output_folders)
            [fmove(scn_file, self.t2p(scn_file).parent) for scn_file in scaled_scn_file_ls]
            self.tmp_clear()
            self._count_process += len(scaled_scn_file_ls)

    def scn_de(self, scn_file):
        scn_de_p = subprocess.run([self.psb_de_exe, scn_file], capture_output=True)

    def scn_en(self, scn_json_file_and_output_folder: tuple):
        scn_json_file = scn_json_file_and_output_folder[0]
        output_folder = scn_json_file_and_output_folder[1]
        scn_en_p = subprocess.run([self.psb_en_exe, scn_json_file], shell=True, cwd=output_folder, capture_output=True)
        # 重命名
        tmp_scn_file = (output_folder/scn_json_file.name).with_suffix('.pure.scn')
        out_scn_file = (output_folder/scn_json_file.name).with_suffix('.scn')
        tmp_scn_file.replace(out_scn_file)
        return out_scn_file

    def scn_json2x_(self, scn_json_file):
        with open(scn_json_file, newline='', encoding='utf-8') as f:
            lines = f.readlines()
            result = []
            for line in lines:
                keyn_ls = ['originx', 'originy', 'xpos', 'ypos', 'zpos', 'zoomx', 'zoomy']
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*\W+{keyn}\W+?)(-?\d+)(.*)')
                    re_result = re.match(pattern, line)
                    if re_result:
                        line = self.line_pattern_num2x(re_result)
                result.append(line)
        with open(scn_json_file, 'w', newline='', encoding='utf-8') as f:
            f.writelines(result)

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
                    re_result = re.match(pattern, line)
                    if re_result:
                        re_result_ls = list(re_result.groups())
                        re_result_ls[1] = str(int(re_result_ls[1]) - int((self.scwidth*self.scale_ratio-self.scwidth)/2))
                        re_result_ls = [i for i in re_result_ls if i != None]
                        line = ''.join(re_result_ls)
                # 大小修正
                if 'facezoom' in line:
                    re_result = re.match(pattern, line)
                    if re_result:
                        line = self.line_pattern_num2x(re_result)
                result.append(line)
            with open(self.a2p(stand_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)
            self._count_process += 1

    def stand_correction(self, input_folder, output_folder, face_zoom, xpos_move):
        '''
        对话框人物立绘后处理
        '''
        input_folder = Path(input_folder).resolve()
        output_folder = Path(output_folder).resolve()
        stand_file_ls = file_list(input_folder, 'stand')
        pattern = re.compile(r'(.*?)(-?\d+)(.*)')
        for stand_file in stand_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(stand_file)
            for line in lines:
                # 水平方向位置修正
                if 'facexoff' in line:
                    re_result = re.match(pattern, line)
                    if re_result:
                        re_result_ls = list(re_result.groups())
                        re_result_ls[1] = str(int(re_result_ls[1]) + xpos_move)
                        re_result_ls = [i for i in re_result_ls if i != None]
                        line = ''.join(re_result_ls)
                # 大小修正
                if 'facezoom' in line:
                    re_result = re.match(pattern, line)
                    if re_result:
                        line = pattern_num2x(re_result, face_zoom)
                result.append(line)
            with open(p2p(stand_file, input_folder, output_folder), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    """
    ==================================================
    Kirikiri引擎图片文件：pimg, tlg, png, jpg, jpeg, bmp, webp, eri
    ==================================================
    """

    def image2x(self):
        self.emit_info('开始处理游戏图片......')
        self.general_image2x()
        self.emit_info('常规图片处理完成')
        self.pimg2x()
        self.emit_info('pimg图片处理完成')
        self.tlg2x()
        self.emit_info('tlg图片处理完成')
        # self.eri2x()
        # self.emit_info('eri图片处理完成')

    def general_image2x(self):
        '''
        对常规格式图片进行放大处理
        '''
        image_extension_ls = ['bmp', 'jpg', 'jpeg', 'png', 'webp']
        for image_extension in image_extension_ls:
            image_file_list = patch9_first(file_list(self.game_data, image_extension, ignored_folders=['sysscn', 'fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
            if image_file_list:
                [fcopy(image_file, self.a2t(image_file).parent) for image_file in image_file_list]
                self.emit_info(f'开始放大{image_extension}图片......')
                # show_image2x_p = Process(target=self.show_image2x_status, args=(image_extension,))
                # show_image2x_p.start()
                self.image_upscale(self.tmp_folder, self.patch_folder, self.scale_ratio, image_extension, count_class=self.count_class)
                # show_image2x_p.join()
                self.tmp_clear()

    def pimg2x(self):
        org_pimg_file_ls = patch9_first(file_list(self.game_data, 'pimg'))
        if org_pimg_file_ls:
            pimg_file_ls = [fcopy(pimg_file, self.a2t(pimg_file).parent) for pimg_file in org_pimg_file_ls]
            self.emit_info('正在拆分pimg文件')
            self.pool_run(self.pimg_de, pimg_file_ls)
            self.emit_info('pimg图片放大中......')
            self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png')
            # 获得json文件列表并删除原pimg
            pimg_json_file_ls = []
            for pimg_file in pimg_file_ls:
                pimg_json_file_ls.append(pimg_file.with_suffix('.json'))
                pimg_file.unlink()
            self.emit_info('pimg图片放大完成，正在修正坐标')
            self.pool_run(self.pimg_json2x_, pimg_json_file_ls)
            self.emit_info('pimg组装中......')
            pimg_json_files_and_output_folders = [(pimg_json_file, pimg_json_file.parent) for pimg_json_file in pimg_json_file_ls]
            scaled_pimg_file_ls = self.pool_run(self.pimg_en, pimg_json_files_and_output_folders)
            [fmove(scaled_pimg_file, self.t2p(scaled_pimg_file).parent) for scaled_pimg_file in scaled_pimg_file_ls]
            self.tmp_clear()
            self._count_process += len(scaled_pimg_file_ls)

    def pimg_de(self, pimg_file):
        '''
        拆分pimg文件
        '''
        pimg_de_p = subprocess.run([self.psb_de_exe, pimg_file], capture_output=True)

    def pimg_en(self, pimg_json_file_and_output_folder: tuple):
        '''
        组装pimg文件，原程序直接输出到工作路径，所以需要修改输出路径
        '''
        pimg_json_file = pimg_json_file_and_output_folder[0]
        output_folder = pimg_json_file_and_output_folder[1]
        pimg_en_p = subprocess.run([self.psb_en_exe, pimg_json_file, ], shell=True, cwd=output_folder, capture_output=True)
        # 重命名
        tmp_pimg_file = (output_folder/pimg_json_file.name).with_suffix('.pure.pimg')
        out_pimg_file = (output_folder/pimg_json_file.name).with_suffix('.pimg')
        tmp_pimg_file.replace(out_pimg_file)
        return out_pimg_file

    def pimg_json2x_(self, pimg_json_file):
        '''
        pimg坐标修正
        '''
        keyn_ls = ['height', 'width', 'left', 'top']
        with open(pimg_json_file, newline='', encoding='utf-8') as f:
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
        with open(pimg_json_file, 'w', newline='', encoding='utf-8') as f:
            f.write(result)

    def tlg2x(self):
        '''
        对tlg格式图片进行放大处理
        '''
        ori_tlg_file_ls = patch9_first(file_list(self.game_data, 'tlg', ignored_folders=['fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
        if ori_tlg_file_ls:
            [fcopy(tlg_file, self.a2t(tlg_file).parent) for tlg_file in ori_tlg_file_ls]
            tlg_file_ls = file_list(self.tmp_folder)
            self.emit_info('tlg图片转换中......')
            png_file_ls = self.pool_run(self.tlg2png, tlg_file_ls)
            [tlg_file.unlink() for tlg_file in tlg_file_ls]
            self.emit_info('tlg转换完成，正在放大中......')
            # show_tlg2x_p = Process(target=self.show_image2x_status, args=('png',))
            # show_tlg2x_p.start()
            self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png')
            # show_tlg2x_p.join()
            self.emit_info('tlg格式图片放大完成，正在进行格式转换......')
            scaled_tlg_file_ls = self.pool_run(self.png2tlg6, png_file_ls)
            [fmove(tlg_file, self.t2p(tlg_file).parent) for tlg_file in scaled_tlg_file_ls]
            self.tmp_clear()
            self._count_process += len(scaled_tlg_file_ls)
        else:
            self.emit_info('未发现需要处理的tlg图片')

    def tlg2png_batch(self, input_folder, output_folder) -> list:
        """
        @brief      tlg转png

        @param      input_folder   输入文件夹
        @param      output_folder  输出文件夹

        @return     输出png图片路径列表
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        tlg_file_ls = file_list(input_folder, 'tlg')
        output_png_file_ls = self.pool_run(self.tlg2png, tlg_file_ls)
        target_png_file_ls = []
        for output_png_file in output_png_file_ls:
            target_png_file = p2p(output_png_file, input_folder, output_folder)
            fmove(output_png_file, target_png_file.parent)
            target_png_file_ls.append(target_png_file)
        return target_png_file_ls

    def png2tlg_batch(self, input_folder, output_folder, tlg5_mode=False) -> list:
        """
        @brief      png转tlg

        @param      input_folder   输入文件夹
        @param      output_folder  输出文件夹
        @param      tlg5_mode      输出为tlg5，适用于krkr2.24以下版本

        @return     输出tlg图片路径列表
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        png_file_ls = file_list(input_folder, 'png')
        if tlg5_mode:
            self.emit_info('请将弹出文件夹及其子文件中的png图片拖入吉里吉里图像转换器窗口\n不要修改选项，确认处理完成后关闭吉里吉里图像转换器')
            os.system(f'start {input_folder}')
            os.system(str(self.krkrtpc_exe))
            tmp_tlg_file_ls = [png_file.with_suffix('.tlg') for png_file in png_file_ls]
        else:
            tmp_tlg_file_ls = self.pool_run(self.png2tlg6, png_file_ls)
        target_tlg_file_ls = []
        for tlg_file in tmp_tlg_file_ls:
            target_tlg_file = p2p(tlg_file, input_folder, output_folder)
            fmove(tlg_file, target_tlg_file.parent)
            target_tlg_file_ls.append(target_tlg_file)
        return target_tlg_file_ls

    def tlg2tlg_batch(self, input_folder, output_folder, tlg5_mode=False) -> list:
        """
        @brief      tlg转tlg6或tlg5

        @param      input_folder   输入文件夹
        @param      output_folder  输出文件夹
        @param      tlg5_mode      输出tlg5

        @return     tlg图片路径列表
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        tmp_folder = output_folder.parent/('tmp_'+self.create_str())
        if not tmp_folder.exists():
            tmp_folder.mkdir(parents=True)
        tmp_png_ls = self.tlg2png_batch(input_folder, tmp_folder)
        target_tlg_file_ls = self.png2tlg_batch(tmp_folder, output_folder, tlg5_mode=tlg5_mode)
        shutil.rmtree(tmp_folder)
        return target_tlg_file_ls

    def tlg2png(self, tlg_file) -> Path:
        '''
        将tlg图片转化为png格式
        '''
        output_png_file = tlg_file.with_suffix('.png')
        tlg2png_p = subprocess.run([self.tlg2png_exe, tlg_file, output_png_file], capture_output=True)
        return output_png_file

    def png2tlg6(self, png_file) -> Path:
        '''
        将png图片转化为tlg6格式，适用于krkr2.24及以上版本
        '''
        output_tlg_file = png_file.with_suffix('.tlg')
        png2tlg6_p = subprocess.run([self.png2tlg6_exe, png_file, output_tlg_file], capture_output=True)
        return output_tlg_file

    def eri2x(self):
        eri_file_ls = file_list(self.game_data, 'eri')
        if eri_file_ls:
            self.emit_info('暂不支持eri图片格式')

    """
    ==================================================
    Kirikiri引擎动画文件：amv, psb, swf
    ==================================================
    """

    def animation2x(self):
        self.emit_info('开始处理游戏动画......')
        self.amv2x()
        # self.psb2x()
        # self.swf2x()

    def psb2x(self):
        psb_file_ls = file_list(self.game_data, 'psb')
        if psb_file_ls:
            self.emit_info('暂不支持psb文件处理，后续会加进去')
            pass

    def swf2x(self):
        swf_file_ls = file_list(self.game_data, 'swf')
        if swf_file_ls:
            self.emit_info('swf这东西没见过有游戏用过，有需求再加进去')

    def amv2x(self):
        ori_amv_file_ls = patch9_first(file_list(self.game_data, 'amv'))
        if ori_amv_file_ls:
            amv_file_ls = [fcopy(amv_file, self.a2t(amv_file).parent) for amv_file in ori_amv_file_ls]
            self.emit_info('AMV动画拆帧中......')
            png_sequence_folder_ls = self.amv2png(self.tmp_folder, self.tmp_folder)
            [amv_file.unlink() for amv_file in amv_file_ls]
            self.emit_info('AMV动画拆帧完成，正在放大中......')
            self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png', video_mode=True)
            self.emit_info('AMV动画组装中......')
            scaled_amv_file_ls = self.pool_run(self.amv_en, png_sequence_folder_ls)
            [fmove(scaled_amv_file, self.t2p(scaled_amv_file).parent) for scaled_amv_file in scaled_amv_file_ls]
            self.tmp_clear()
            self._count_process += len(scaled_amv_file_ls)

    def amv2png(self, input_folder, output_folder) -> list:
        """
        @brief      将amv文件拆分为png图片

        @param      input_folder   输入文件夹
        @param      output_folder  输出文件夹

        @return     输出文件夹路径列表
        """
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        # 复制并重命名
        amv_file_ls = file_list(input_folder, 'amv')
        newamv_orgamv_dict = self.format_copy_amvfile(amv_file_ls)
        # 拆帧
        self.pool_run(self.amv_de, newamv_orgamv_dict.keys())
        # 将图片改名并移动到目标文件夹
        png_sequence_folder_ls = []
        for new_amv_file, org_amv_file in newamv_orgamv_dict.items():
            png_sequence_folder = output_folder/org_amv_file.with_name(org_amv_file.stem).relative_to(input_folder)
            png_sequence_folder.mkdir(parents=True, exist_ok=True)
            png_sequence_folder_ls.append(png_sequence_folder)
            # 重命名图片并移动
            for png_file in file_list(self.amv_de_folder, 'png'):
                name_part_ls = png_file.stem.split('_')
                if name_part_ls[0] == new_amv_file.stem:
                    name_part_ls[1] = '%05d' % int(name_part_ls[1])
                    name_fmt = ''.join(name_part_ls)+'.png'
                    tmp_path = self.amv_de_folder/name_fmt
                    png_file.replace(tmp_path)
                    fmove(tmp_path, png_sequence_folder)
        return png_sequence_folder_ls

    def format_copy_amvfile(self, amv_file_ls):
        """
        @brief      复制列表中的amv文件并改名

        @param      amv_file_ls  amv文件路径列表

        @return     返回键为新amv文件路径，对应值为原amv文件路径的字典
        """
        # 清空文件夹
        if self.amv_de_folder.exists():
            shutil.rmtree(self.amv_de_folder)
        self.amv_de_folder.mkdir(parents=True)
        newamv_orgamv_dict = {}
        for new_amv_name_index, amv_file in enumerate(amv_file_ls, start=1):
            tmp_amv_file = fcopy(amv_file, self.amv_de_folder)
            new_amv_file = tmp_amv_file.with_name('%03d.amv' % new_amv_name_index)
            newamv_orgamv_dict[new_amv_file] = amv_file
            tmp_amv_file.replace(new_amv_file)
        return newamv_orgamv_dict

    def amv_de(self, amv_file):
        '''
        拆分amv动画为png序列
        '''
        amv_de_p = subprocess.run([self.amv_de_exe, '-amvpath='+str(amv_file)], capture_output=True)
        amv_file.unlink()

    def amv_en(self, png_sequence_folder):
        '''
        将png序列合并为amv动画
        '''
        # 目标amv文件
        target_amv = png_sequence_folder.with_suffix('.amv')
        # 临时名称防乱码和空格及特殊字符
        tmp_stem = self.create_str()
        tmp_folder = png_sequence_folder.with_name(tmp_stem)
        png_sequence_folder.replace(tmp_folder)
        tmp_amv = tmp_folder.with_suffix('.amv')
        # 运行
        options = [self.amv_en_exe,
                   '--png', '--zlib',
                   '--quality', '100',
                   tmp_folder, tmp_amv
                   ]
        amv_en_p = subprocess.run(options, capture_output=True)
        # 改名
        tmp_folder.replace(png_sequence_folder)
        tmp_amv.replace(target_amv)
        return target_amv

    def png2amv(self, png_sequence_folder, output_folder):
        """
        @brief      将png序列合成为amv动画

        @param      png_sequence_folder  The png sequence folder
        @param      output_folder        The output folder

        @return     输出amv文件路径
        """
        png_sequence_folder = Path(png_sequence_folder).resolve()
        output_folder = Path(output_folder).resolve()
        amv_file = self.amv_en(png_sequence_folder)
        target_amv_path = fmove(amv_file, output_folder)
        return target_amv_path

    """
    ==================================================
    Kirikiri引擎视频文件：mpg, mpeg, wmv, avi, mkv
    ==================================================
    """

    def video2x(self):
        self.emit_info('开始处理游戏视频......')
        video_extension_ls = ['mpg', 'mpeg', 'wmv', 'avi', 'mkv']
        for video_extension in video_extension_ls:
            org_video_ls = patch9_first(file_list(self.game_data, video_extension))
            if org_video_ls:
                for video_file in org_video_ls:
                    self.emit_info(f'{video_file} 处理中......')
                    output_video = self.a2t(video_file)
                    output_vcodec = None
                    if self.video_info(video_file)['vcodec'] == 'wmv3':
                        output_vcodec = 'wmv2'
                    output_video = self.video_upscale(video_file, output_video, self.scale_ratio, output_vcodec=output_vcodec)
                    self.tmp_clear()
                    target_video = fmove(output_video, self.t2p(output_video).parent)
                    self._count_process += 1
                    self.emit_info(f'{target_video} saved!')


def patch9_first(file_ls) -> list:
    """
    @brief      对于重名文件，含有patch后缀数字大的文件夹及其子目录中的文件优先

    @param      file_ls  文件列表

    @return     筛选后的文件列表
    """
    path_name_dict = {}
    for file in file_ls:
        path_name_dict[file] = file.name
    new_file_ls = []
    for i, i_name in path_name_dict.items():
        still_alive = True
        for j, j_name in path_name_dict.items():
            if j_name == i_name:
                a = patch_num(i)
                b = patch_num(j)
                if b is not False:
                    if a is not False:
                        if b > a:
                            still_alive = False
                    else:
                        still_alive = False
        if still_alive == True:
            new_file_ls.append(i)
    return new_file_ls


def patch_num(file_path):
    """
    @brief      如果是patch文件夹，返回patch文件夹后缀数字，否则False

    @param      file_path  文件路径

    @return     数字或False
    """
    for folder_name in get_parent_names(file_path):
        try:
            if folder_name[:5] == 'patch':
                if len(folder_name) == 5:
                    return 0
                else:
                    return int(folder_name[5:])
        except:
            pass
    return False
