# -*- coding:utf-8 -*-

from Core import *
from .amv_struct import AMVStruct


class Kirikiri(Core):
    """Kirikiri 2/Z Engine"""

    def __init__(self, game_ui_runner=None):
        Core.__init__(self)
        self.encoding = 'Shift_JIS'
        self.load_config()
        self.__class__.game_ui_runner = game_ui_runner
        self.run_dict = {'script': False, 'image': False, 'animation': False, 'video': False}
        self.keep_path_struct_mode = True

    def emit_info(self, info_str):
        print(info_str)
        logging.info(info_str)
        if self.game_ui_runner is not None:
            self.game_ui_runner.info_sig.emit(info_str)

    def emit_progress(self, _percent, _left_time):
        print(_percent, _left_time, sep='\t')
        if self.game_ui_runner is not None:
            self.game_ui_runner.progress_sig.emit(_percent, _left_time)

    def upscale(self):
        # 计时
        start_time = time.time()
        # 创建补丁文件夹
        if not self.patch_folder.exists():
            self.patch_folder.mkdir(parents=True)
        # 开始放大
        if self.run_dict['script']:
            self.script2x()
            self.emit_info('文本文件处理完成')
        if self.run_dict['image']:
            self.image2x()
            self.emit_info('图片文件放大完成')
        if self.run_dict['animation']:
            self.animation2x()
            self.emit_info('动画文件处理完成')
        if self.run_dict['video']:
            self.video2x()
            self.emit_info('视频文件处理完成')
        # 将文件平铺
        if not self.keep_path_struct_mode:
            self.patch_folder.flat_folder_()
        timing_count = time.time() - start_time
        self.emit_info(f'共耗时：{seconds_format(timing_count)}')

    def get_resolution_encoding(self, input_folder):
        '''
        获取文本编码和分辨率
        '''
        input_folder = Path(input_folder)
        tjs_file_ls = patch9_first(input_folder.file_list('tjs'))
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
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        self.emit_info('正在计算文件优先级......')
        patch_file_ls = patch9_first(input_folder.file_list())
        if patch_file_ls:
            for file in patch_file_ls:
                target_file_path = file.copy_to(output_folder)
                self.emit_info(f'{target_file_path} saved!')

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
        self.fg_text2x()
        # self.scn2x()

    def tjs2x(self):
        tjs_file_ls = patch9_first(self.game_data.file_list('tjs'))
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

    def ks2x(self):
        ks_file_ls = patch9_first(self.game_data.file_list('ks'))
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
                pattern1 = re.compile(r'(.*genpos)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)([\D]*)(\d+)(.*)')
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
        uicsv_file_ls = patch9_first(self.game_data.file_list('csv', parent_folder='uipsd'))
        for input_csv in uicsv_file_ls:
            output_csv = self.a2p(input_csv)
            self.csv2x(input_csv, output_csv, self.scale_ratio)

    def asd2x(self):
        '''
        人物表情、sd动画、对话框上的等待点击效果、进度条
        '''
        asd_keyword_list = ['clipleft', 'cliptop', 'clipwidth', 'clipheight', 'left',
                            'top', 'height', 'weight', 'dx', 'dy', 'dw', 'dh', 'sx', 'sy', 'sw', 'sh', 'x', 'y']
        # asd_file_ls = patch9_first(self.game_data.file_list('asd'))
        # 忽略人物表情处理，这东西不需要改，改了反而不正常
        asd_file_ls = patch9_first(self.game_data.file_list('asd', ignored_folders=['emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
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

    def scn2x(self):
        ori_scn_file_ls = patch9_first(self.game_data.file_list('scn'))
        if ori_scn_file_ls:
            with tempfile.TemporaryDirectory() as tmp_folder:
                self.tmp_folder = Path(tmp_folder)

                scn_file_ls = [scn_file.copy_as(self.a2t(scn_file)) for scn_file in ori_scn_file_ls]
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
                scaled_scn_file_ls = self.pool_run(self.scn_en, scn_json_file_ls)

                [scn_file.move_as(self.t2p(scn_file)) for scn_file in scaled_scn_file_ls]

    def scn_de(self, scn_file):
        scn_de_p = subprocess.run([self.psb_de_exe, scn_file], capture_output=True, shell=True)

    def scn_en(self, scn_json_file):
        output_folder = scn_json_file.parent
        scn_en_p = subprocess.run([self.psb_en_exe, scn_json_file], shell=True, cwd=output_folder, capture_output=True)
        # 重命名
        tmp_scn_file = scn_json_file.with_suffix('.pure.scn')
        out_scn_file = scn_json_file.with_suffix('.scn')
        tmp_scn_file.move_as(out_scn_file)
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
        stand_file_ls = patch9_first(self.game_data.file_list('stand'))
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

    def stand_correction(self, input_folder, output_folder, face_zoom, xpos_move):
        '''
        对话框人物立绘后处理
        '''
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        stand_file_ls = input_folder.file_list('stand')
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
            with open(stand_file.reio_path(input_folder, output_folder, mk_dir=True), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    def fg_text2x(self):
        extension_list = ['txt', 'tjs', 'ks', 'pbd']
        for extension in extension_list:
            for file_path in patch9_first(self.game_data.file_list(extension)):
                try:
                    self._fg_text2x(file_path, self.scale_ratio, self.a2p(file_path))
                except:
                    self.emit_info(f'未识别的加密文件{file_path}!')

    def _fg_text2x(self, file_path, scale_ratio, output_path):
        if file_path.readbs(2) == b'\xfe\xfe':
            mode, content = self._decrypt_text(file_path)
            current_encoding = self.encoding
        else:
            try:
                with open(file_path, newline='', encoding=self.encoding) as f:
                    current_encoding = self.encoding
                    content = f.read()
            except:
                current_encoding = self.get_encoding(file_path)
                with open(file_path, newline='', encoding=current_encoding) as f:
                    content = f.read()
        fgimage_text_sign = '#layer_type\tname\tleft\ttop\twidth\theight\ttype\topacity\tvisible\tlayer_id\tgroup_layer_id\tbase\timages\t'
        if not content.startswith(fgimage_text_sign):
            self.emit_info(f'{file_path}不是立绘坐标文件!')
            return None
        with PrivateStringIO(content) as _f:
            reader = csv.DictReader(_f, delimiter='\t')
            content_ls = list(reader)
            for i, j in enumerate(content_ls):
                kwds = ['left', 'top', 'width', 'height']
                for kwd in kwds:
                    _num = j[kwd]
                    if real_digit(_num):
                        j[kwd] = str(int(float(_num)*scale_ratio))
                content_ls[i] = j
        with open(output_path, 'w', newline='', encoding=current_encoding) as f:
            writer = csv.DictWriter(f, delimiter='\t', fieldnames=fgimage_text_sign.split('\t'))
            writer.writeheader()
            writer.writerows(content_ls)
        self.emit_info(f'{file_path}立绘坐标处理完成!')
        return output_path

    def _decrypt_text(self, file_path):
        content = file_path.readbs()
        # if content[:5] == b'\xfe\xfe\x00\xff\xfe':
        #     pass
        if content[:5] == b'\xfe\xfe\x01\xff\xfe':
            mode = 1
            content_p = bytearray(content[5:])
            for i in range(len(content_p)):
                c = content_p[i]
                if c:
                    content_p[i] = (((c & 0x55) << 1) | ((c & 0xaa) >> 1)) & 0xff
            result = content_p.decode('UTF-16LE')
        elif content[:5] == b'\xfe\xfe\x02\xff\xfe':
            mode = 2
            result = zlib.decompress(content[0x15:]).decode('UTF-16')
        return mode, result

    """
    ==================================================
    Kirikiri引擎图片文件：pimg, tlg, png, jpg, jpeg, bmp, webp, eri
    ==================================================
    """

    def image2x(self):
        self.emit_info('开始处理游戏图片......')
        self._general_image2x()
        self.emit_info('常规图片处理完成')
        self._pimg2x()
        self.emit_info('pimg图片处理完成')
        self._tlg2x()
        self.emit_info('tlg图片处理完成')
        # self.eri2x()
        # self.emit_info('eri图片处理完成')

    def _general_image2x(self):
        '''
        对常规格式图片进行放大处理
        '''
        image_extension_ls = ['bmp', 'jpg', 'jpeg', 'png', 'webp']
        for image_extension in image_extension_ls:
            # image_file_list = patch9_first(self.game_data.file_list(image_extension))
            image_file_list = patch9_first(self.game_data.file_list(image_extension, ignored_folders=['sysscn', 'fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
            if image_file_list:
                with tempfile.TemporaryDirectory() as tmp_folder:
                    self.tmp_folder = Path(tmp_folder)
                    [image_file.copy_as(self.a2t(image_file)) for image_file in image_file_list]
                    self.emit_info(f'开始放大{image_extension}图片......')
                    self.image_upscale(self.tmp_folder, self.patch_folder, self.scale_ratio, image_extension)

    def _pimg2x(self):
        org_pimg_file_ls = patch9_first(self.game_data.file_list('pimg'))
        if org_pimg_file_ls:
            with tempfile.TemporaryDirectory() as tmp_folder:
                self.tmp_folder = Path(tmp_folder)
                pimg_file_ls = [pimg_file.copy_as(self.a2t(pimg_file)) for pimg_file in org_pimg_file_ls]

                self.emit_info('正在拆分pimg文件')
                out_pimg_json_file_ls = self.pimg_de_batch(self.tmp_folder, self.tmp_folder)

                self.emit_info('pimg图片放大中......')
                self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png')

                self.emit_info('pimg图片放大完成，正在修正坐标')
                self.pool_run(self._pimg_json2x_, out_pimg_json_file_ls)

                self.emit_info('pimg组装中......')
                scaled_pimg_file_ls = self.pimg_en_batch(self.tmp_folder, self.patch_folder)

    def pimg_de_batch(self, input_path, output_folder) -> list:
        """
        @brief      拆分pimg文件

        @param      input_path     输入文件或文件夹
        @param      output_folder  The output folder

        @return     json文件路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        pimg_out_path_dict = {}
        if input_path.is_file():
            out_dir = input_path.reio_path(input_path.parent, output_folder, mk_dir=True).parent
            pimg_out_path_dict[input_path] = out_dir
        else:
            pimg_file_ls = input_path.file_list('pimg')
            for pimg_file in pimg_file_ls:
                out_dir = pimg_file.reio_path(input_path, output_folder, mk_dir=True).parent
                pimg_out_path_dict[pimg_file] = out_dir
        out_pimg_json_file_ls = self.pool_run(self._pimg_de, pimg_out_path_dict.items())
        return out_pimg_json_file_ls

    def _pimg_de(self, pimg_out_path) -> Path:
        '''
        拆分pimg文件到指定目录
        '''
        pimg_file, output_dir = pimg_out_path
        with tempfile.TemporaryDirectory() as pimg_tmp_folder:
            pimg_tmp_folder = Path(pimg_tmp_folder)
            tmp_pimg = pimg_file.copy_to(pimg_tmp_folder)
            # 拆分pimg文件到pimg文件所在目录
            pimg_de_p = subprocess.run([self.psb_de_exe, tmp_pimg], capture_output=True, shell=True)
            tmp_png_folder = tmp_pimg.with_suffix('')
            tmp_png_folder.move_to(output_dir)
            tmp_json_file1 = tmp_pimg.with_suffix('.json')
            pimg_json = tmp_json_file1.move_to(output_dir)
            tmp_json_file2 = tmp_pimg.with_suffix('.resx.json')
            tmp_json_file2.move_to(output_dir)
            return pimg_json

    def pimg_en_batch(self, input_path, output_folder) -> list:
        """
        @brief      批量合成pimg

        @param      input_path     The input path
        @param      output_folder  The output folder

        @return     pimg路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        json_work_path_dict = {}
        if input_path.is_file():
            json_work_path_dict[input_path] = output_folder
        else:
            json_file_ls = [json_file for json_file in input_path.file_list('json') if (json_file.with_suffix('').exists() and json_file.with_suffix('').is_dir())]
            for json_file in json_file_ls:
                work_dir = json_file.reio_path(input_path, output_folder, mk_dir=True).parent
                json_work_path_dict[json_file] = work_dir
        output_pimg_file_ls = self.pool_run(self._pimg_en, json_work_path_dict.items())
        return output_pimg_file_ls

    def _pimg_en(self, json_work_path) -> Path:
        '''
        组装pimg文件，原程序直接输出到工作路径，所以需要修改输出路径
        '''
        pimg_json_file, output_folder = json_work_path
        pimg_en_p = subprocess.run([self.psb_en_exe, pimg_json_file], shell=True, cwd=output_folder, capture_output=True)
        # 重命名
        tmp_pimg_file = output_folder/pimg_json_file.with_suffix('.pure.pimg').name
        out_pimg_file = output_folder/pimg_json_file.with_suffix('.pimg').name
        tmp_pimg_file.move_as(out_pimg_file)
        return out_pimg_file

    def _pimg_json2x_(self, pimg_json_file):
        '''
        pimg坐标修正，覆盖
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

    def _tlg2x(self):
        '''
        对tlg格式图片进行放大处理
        '''
        # ori_tlg_file_ls = patch9_first(self.game_data.file_list('tlg'))
        ori_tlg_file_ls = patch9_first(self.game_data.file_list('tlg', ignored_folders=['fgimage', 'emotion', 'emotions', 'Emotion', 'Emotions', 'anim']))
        if ori_tlg_file_ls:
            with tempfile.TemporaryDirectory() as tmp_folder:
                self.tmp_folder = Path(tmp_folder)
                [tlg_file.copy_as(self.a2t(tlg_file)) for tlg_file in ori_tlg_file_ls]

                self.emit_info('tlg图片转换中......')
                png_file_ls = self.tlg2png_batch(self.tmp_folder, self.tmp_folder)

                self.emit_info('tlg转换完成，正在放大中......')
                self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png')

                self.emit_info('tlg格式图片放大完成，正在进行格式转换......')
                scaled_tlg_file_ls = self.png2tlg_batch(self.tmp_folder, self.patch_folder)

    def tlg2png_batch(self, input_path, output_folder) -> list:
        """
        @brief      tlg转png

        @param      input_path     输入文件或文件夹
        @param      output_folder  输出文件夹

        @return     输出png图片路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        tlg_png_path_dict = {}
        if input_path.is_file():
            out_png = input_path.reio_path(input_path.parent, output_folder, mk_dir=True).with_suffix('.png')
            tlg_png_path_dict[input_path] = out_png
        else:
            tlg_file_ls = input_path.file_list('tlg')
            for tlg_file in tlg_file_ls:
                out_png = tlg_file.reio_path(input_path, output_folder, mk_dir=True).with_suffix('.png')
                tlg_png_path_dict[tlg_file] = out_png
        output_png_file_ls = self.pool_run(self._tlg2png, tlg_png_path_dict.items())
        return output_png_file_ls

    def _tlg2png(self, tlg_png_path) -> Path:
        '''
        将tlg图片转化为png格式
        '''
        tlg_file, png_file = tlg_png_path
        tlg2png_p = subprocess.run([self.tlg2png_exe, tlg_file, png_file], capture_output=True, shell=True)
        return png_file

    def png2tlg_batch(self, input_path, output_folder, tlg5_mode=False) -> list:
        """
        @brief      png转tlg

        @param      input_path     输入文件或文件夹
        @param      output_folder  输出文件夹
        @param      tlg5_mode      输出为tlg5，适用于krkr2.24以下版本

        @return     输出tlg图片路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        png_tlg_path_dict = {}
        if input_path.is_file():
            out_tlg = input_path.reio_path(input_path.parent, output_folder, mk_dir=True).with_suffix('.tlg')
            png_tlg_path_dict[input_path] = out_tlg
        else:
            png_file_ls = input_path.file_list('png')
            for png_file in png_file_ls:
                out_tlg = png_file.reio_path(input_path, output_folder, mk_dir=True).with_suffix('.tlg')
                png_tlg_path_dict[png_file] = out_tlg
        if tlg5_mode:
            with tempfile.TemporaryDirectory() as tlg_tmp_folder:
                tlg_tmp_folder = Path(tlg_tmp_folder)
                tmp_target_dict = {}
                for png_file, target_tlg in png_tlg_path_dict.items():
                    tmp_png = tlg_tmp_folder/(self.create_str()+'.png')
                    png_file.copy_as(tmp_png)
                    tmp_target_dict[tmp_png] = target_tlg
                self.emit_info('请将弹出文件夹中的png图片拖入吉里吉里图像转换器窗口\n不要修改选项，确认处理完成后关闭吉里吉里图像转换器')
                show_folder(tlg_tmp_folder)
                _p = subprocess.run([self.krkrtpc_exe,], capture_output=True, shell=True)
                # os.system(str(self.krkrtpc_exe))
                output_tlg_file_ls = []
                for tmp_png, target_tlg in tmp_target_dict.items():
                    tmp_tlg = tmp_png.with_suffix('.tlg')
                    tmp_tlg.move_as(target_tlg)
                    output_tlg_file_ls.append(target_tlg)
        else:
            output_tlg_file_ls = self.pool_run(self._png2tlg6, png_tlg_path_dict.items())
        return output_tlg_file_ls

    def _png2tlg6(self, png_tlg_path) -> Path:
        '''
        将png图片转化为tlg6格式，适用于krkr2.24及以上版本
        '''
        png_file, tlg_file = png_tlg_path
        png2tlg6_p = subprocess.run([self.png2tlg6_exe, png_file, tlg_file], capture_output=True, shell=True)
        return tlg_file

    def tlg2tlg_batch(self, input_path, output_folder, tlg5_mode=False) -> list:
        """
        @brief      tlg转tlg6或tlg5

        @param      input_path     输入文件或文件夹
        @param      output_folder  输出文件夹
        @param      tlg5_mode      输出tlg5

        @return     tlg图片路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        with tempfile.TemporaryDirectory() as tmp_folder:
            tmp_folder = Path(tmp_folder)
            tmp_png_ls = self.tlg2png_batch(input_path, tmp_folder)
            target_tlg_file_ls = self.png2tlg_batch(tmp_folder, output_folder, tlg5_mode=tlg5_mode)
        return target_tlg_file_ls

    def eri2x(self):
        eri_file_ls = self.game_data.file_list('eri')
        if eri_file_ls:
            self.emit_info('暂不支持eri图片格式')

    """
    ==================================================
    Kirikiri引擎动画文件：amv, psb, swf
    ==================================================
    """

    def animation2x(self):
        self.emit_info('开始处理游戏动画......')
        self._amv2x()
        # self.psb2x()
        # self.swf2x()

    def psb2x(self):
        psb_file_ls = self.game_data.file_list('psb')
        if psb_file_ls:
            self.emit_info('暂不支持psb文件处理，后续会加进去')
            pass

    def swf2x(self):
        swf_file_ls = self.game_data.file_list('swf')
        if swf_file_ls:
            self.emit_info('swf这东西没见过有游戏用过，有需求再加进去')

    def _amv2x(self):
        ori_amv_file_ls = patch9_first(self.game_data.file_list('amv'))
        if ori_amv_file_ls:
            with tempfile.TemporaryDirectory() as tmp_folder:
                self.tmp_folder = Path(tmp_folder)
                amv_file_ls = [amv_file.copy_as(self.a2t(amv_file)) for amv_file in ori_amv_file_ls]
                self.emit_info('AMV动画拆帧中......')
                png_sequence_folder_ls = self.amv2png(self.tmp_folder, self.tmp_folder)
                [amv_file.unlink() for amv_file in amv_file_ls]
                self.emit_info('AMV动画拆帧完成，正在放大中......')
                self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png', video_mode=True)
                self.emit_info('AMV动画组装中......')
                scaled_amv_file_ls = self.png2amv(self.tmp_folder, self.patch_folder)

    def amv2png(self, input_dir, output_dir) -> list:
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        amv_dict = self._amv2png_pre(input_dir, output_dir)
        target_amv_dirs = self.pool_run(self._amv_de, amv_dict.items())
        return target_amv_dirs

    def _amv2png_pre(self, input_dir, output_dir) -> dict:
        amv_file_ls = input_dir.file_list('amv')
        self.amv_de_folder.sweep()
        amv_dict = {}
        for index_i, amv_file in enumerate(amv_file_ls, start=1):
            target_amv_file = amv_file.reio_path(input_dir, output_dir, mk_dir=True)
            target_amv_dir = target_amv_file.parent/target_amv_file.stem
            tmp_amv = self.amv_de_folder/('%03d' % index_i + '.amv')
            amv_file.copy_as(tmp_amv)
            tmp_amv_dir = tmp_amv.parent/(tmp_amv.stem+'frames')
            amv_dict[tmp_amv] = (tmp_amv_dir, target_amv_dir, target_amv_file)
        return amv_dict

    def _amv_de(self, amv_tuple) -> Path:
        '''
        拆分amv动画为png序列
        '''
        tmp_amv = amv_tuple[0]
        tmp_amv_dir = amv_tuple[1][0]
        target_amv_dir = amv_tuple[1][1]
        amv_de_p = subprocess.run([self.amv_de_exe, '-amvpath='+tmp_amv.to_str], capture_output=True, shell=True)
        amv_file_info = self._get_amv_file_info(tmp_amv)
        result = json.dumps(amv_file_info, sort_keys=False, indent=2, ensure_ascii=False)
        tmp_amv.unlink()
        tmp_amv_dir.move_as(target_amv_dir)
        with open(target_amv_dir.parent/(target_amv_dir.name+'.json'), 'w', newline='', encoding='utf-8') as amv_c:
            amv_c.write(result)
        return target_amv_dir

    @staticmethod
    def _get_amv_file_info(amv_file) -> dict:
        amv_file_info = dict(AMVStruct.parse_file(amv_file).header)
        amv_file_info.pop('_io')
        for i, j in amv_file_info.items():
            amv_file_info[i] = str(j)
        amv_file_info['type'] = 'amv'
        return amv_file_info

    def _amv_en(self, amv_dict_item):
        '''
        将png序列合并为amv动画
        '''
        png_sequence_folder = Path(amv_dict_item[0])
        target_amv = Path(amv_dict_item[1][0])
        frame_rate = str(amv_dict_item[1][1])
        # 防乱码和空格及特殊字符
        with tempfile.TemporaryDirectory() as tmp_folder:
            tmp_folder = Path(tmp_folder)
            png_sequence_folder.copy_as(tmp_folder)
            tmp_amv = tmp_folder.with_suffix('.amv')
            # 运行
            options = [self.amv_en_exe,
                       '--png', '--zlib',
                       '--rate', frame_rate,
                       '--quality', '100',
                       tmp_folder, tmp_amv
                       ]
            amv_en_p = subprocess.run(options, capture_output=True, shell=True)
            # 改名
            tmp_amv.move_as(target_amv)
        return target_amv

    def png2amv(self, input_folder, output_folder):
        input_folder = Path(input_folder)
        output_folder = Path(output_folder)
        amv_json_file_ls = input_folder.file_list('json')
        amv_en_dict = {}
        for amv_json_file in amv_json_file_ls:
            try:
                with open(amv_json_file, newline='', encoding='utf-8') as f:
                    # 读取文件内容
                    content = json.load(f)
                    if content['type'] == 'amv':
                        # png序列
                        png_sequence_folder = amv_json_file.with_suffix('')
                        target_amv = amv_json_file.reio_path(input_folder, output_folder, mk_dir=True).with_suffix('.amv')
                        amv_en_dict[png_sequence_folder] = (target_amv, content['frame_rate'])
            except:
                pass
        target_amv_file_ls = self.pool_run(self._amv_en, amv_en_dict.items())
        return target_amv_file_ls

    """
    ==================================================
    Kirikiri引擎视频文件：mpg, mpeg, wmv, avi, mkv
    ==================================================
    """

    def video2x(self):
        self.emit_info('开始处理游戏视频......')
        video_extension_ls = ['mpg', 'mpeg', 'wmv', 'avi', 'mkv', 'mp4']
        for video_extension in video_extension_ls:
            org_video_ls = patch9_first(self.game_data.file_list(video_extension))
            if org_video_ls:
                for video_file in org_video_ls:
                    with tempfile.TemporaryDirectory() as tmp_folder:
                        self.tmp_folder = Path(tmp_folder)
                        self.emit_info(f'正在处理：{video_file}')
                        output_video = self.a2t(video_file)
                        output_video = self.video_upscale(video_file, output_video, self.scale_ratio)
                        target_video = output_video.move_as(self.t2p(output_video))
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
    for folder_name in file_path.parent_names:
        try:
            if folder_name[:5] == 'patch':
                if len(folder_name) == 5:
                    return 0
                else:
                    return int(folder_name[5:])
        except:
            pass
    return False
