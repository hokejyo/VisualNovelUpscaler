# -*- coding:utf-8 -*-

from Core import *


class Artemis(Core):
    """Artemis Engine"""

    def __init__(self):
        Core.__init__(self)
        self.load_config()
        self.has_connected_ui = False
        self.count_class = None
        self._count_process = 0
        self.run_dict = {'script': False, 'image': False, 'animation': False, 'video': False}

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
            sys_ini_file_ls = [ini_file for ini_file in file_list(self.game_data, 'ini') if ini_file.name == 'system.ini']
            self._upscale_file_count += len(sys_ini_file_ls)

            tbl_file_ls = file_list(self.game_data, 'tbl')
            self._upscale_file_count += len(tbl_file_ls)

            ipt_file_ls = file_list(self.game_data, 'ipt')
            self._upscale_file_count += len(ipt_file_ls)

            ast_file_ls = file_list(self.game_data, 'ast')
            self._upscale_file_count += len(ast_file_ls)

            lua_file_ls = file_list(self.game_data, 'lua')
            self._upscale_file_count += len(lua_file_ls)

        if self.run_dict['image']:
            png_file_ls = file_list(self.game_data, 'png')
            self._upscale_file_count += len(png_file_ls)

        if self.run_dict['animation']:
            ogv_file_ls = file_list(self.game_data, 'ogv')
            self._upscale_file_count += len(ogv_file_ls)

        if self.run_dict['video']:
            video_extension_ls = ['wmv', 'dat', 'mp4', 'avi', 'mpg', 'mkv']
            for video_extension in video_extension_ls:
                video_file_ls = [video_file for video_file in file_list(self.game_data, video_extension) if self.video_info(video_file)]
                self._upscale_file_count += len(video_file_ls)

    def upscale(self):
        # 计时
        start_time = time.time()
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
        for ini_file in file_list(input_folder, 'ini'):
            if ini_file.name == 'system.ini':
                encoding = self.get_encoding(ini_file)
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
                break
        return scwidth, scheight, encoding

    """
    ==================================================
    Artemis引擎脚本文件：ini, tbl, lua, iet, ipt, ast
    ==================================================
    """

    def script2x(self):
        self.emit_info('开始处理游戏脚本......')
        self.sysini2x()
        self.tbl2x()
        self.ipt2x()
        self.ast2x()
        self.lua2x()

    def sysini2x(self):
        '''
        游戏分辨率，存档位置修改
        '''
        sys_ini_file_ls = [ini_file for ini_file in file_list(self.game_data, 'ini') if ini_file.name == 'system.ini']
        for ini_file in sys_ini_file_ls:
            pattern1 = re.compile(r'(WIDTH|HEIGHT)(\W+)(\d+)(.*)')
            result = []
            lines, current_encoding = self.get_lines_encoding(ini_file)
            for line in lines:
                re_result = re.match(pattern1, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
                result.append(line)
            with open(self.a2p(ini_file), 'w', newline='', encoding=current_encoding) as f:
                _save_change = True
                pattern2 = re.compile(r'^(;?)(SAVEPATH.*)')
                for line in result:
                    re_result = re.match(pattern2, line)
                    if re_result:
                        if re_result.group(1):
                            if _save_change:
                                line = 'SAVEPATH = .\\savedataHD\r\n'
                                _save_change = False
                        else:
                            line = ';'+line
                    f.write(line)
            self._count_process += 1

    # def tbl2x(self):
    #     for tbl_file in file_list(self.game_data, 'tbl'):
    #         if tbl_file.name.startswith('list_windows_'):
    #             self.windows_xx_tbl2x(tbl_file)
    #         if tbl_file.name == 'list_windows.tbl':
    #             self.windwos_tbl2x(tbl_file)

    def tbl2x(self):
        tbl_file_ls = file_list(self.game_data, 'tbl')
        self.pool_run(self.windwos_tbl2x, tbl_file_ls)
        self._count_process += len(tbl_file_ls)

    def windows_xx_tbl2x(self, tbl_file):
        '''
        主要是字体修正
        '''
        keyn_ls = ['size', 'left', 'top', 'width', 'height', 'spacetop', 'spacemiddle', 'spacebottom', 'rubysize']
        result = []
        lines, current_encoding = self.get_lines_encoding(tbl_file)
        for line in lines:
            for keyn in keyn_ls:
                pattern = re.compile(rf'(.*?\W+{keyn}\W+)(\d+)(.*)')
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(tbl_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def windwos_tbl2x(self, tbl_file):
        '''
        主要是ui修正，游戏窗口，立绘定位
        '''
        result = []
        lines, current_encoding = self.get_lines_encoding(tbl_file)
        for line in lines:
            ls1 = ['game_scale', 'game_wasmbar', 'fontsize', 'line_size', 'line_window', 'line_back', 'line_scroll', 'line_name01', 'line_name02']
            # ls1 = ['game_scale', 'game_wasmbar', 'title_anime', 'fontsize', 'line_size', 'line_window', 'line_back', 'line_scroll', 'line_name01', 'line_name02']
            for keyn1 in ls1:
                if line.startswith(keyn1):
                    pattern_rule1 = '('+keyn1+r'\W+?\{'+')'+'(.*?)'+r'(\}.*)'
                    pattern1 = re.compile(pattern_rule1)
                    re_result1 = re.match(pattern1, line)
                    if re_result1:
                        line_ls = list(re_result1.groups())
                        tmp_ls = line_ls[1].split(',')
                        for i in range(len(tmp_ls)):
                            if real_digit(tmp_ls[i]):
                                tmp_ls[i] = str(int(int(tmp_ls[i])*self.scale_ratio))
                        line_ls[1] = ','.join(tmp_ls)
                        line = ''.join([i for i in line_ls if i != None])
            ls2 = ['x', 'y', 'w', 'h', 'r', 'cx', 'cy', 'cw', 'ch', 'fx', 'fy', 'fw', 'fh', 'left', 'top', 'size', 'width', 'height', 'spacetop', 'spacemiddle', 'spacebottom', 'kerning', 'rubysize']
            for keyn2 in ls2:
                pattern2 = re.compile(rf'(.*\W+{keyn2}\W+)(\d+)(.*)')
                re_result2 = re.match(pattern2, line)
                if re_result2:
                    line = self.line_pattern_num2x(re_result2)
            ls3 = ['clip', 'clip_a', 'clip_c', 'clip_d']
            for keyn3 in ls3:
                pattern3 = re.compile(rf'(.*\W+{keyn3}\W+?")(.*?)(".*)')
                re_result3 = re.match(pattern3, line)
                if re_result3:
                    line_ls = list(re_result3.groups())
                    tmp_ls = line_ls[1].split(',')
                    for i in range(len(tmp_ls)):
                        if real_digit(tmp_ls[i]):
                            tmp_ls[i] = str(int(int(tmp_ls[i])*self.scale_ratio))
                    line_ls[1] = ','.join(tmp_ls)
                    line = ''.join([i for i in line_ls if i != None])
            ls4 = ['game_width', 'game_height']
            for keyn4 in ls4:
                pattern4 = re.compile(rf'^({keyn4}\W+)(\d+)(.*)')
                re_result4 = re.match(pattern4, line)
                if re_result4:
                    line = self.line_pattern_num2x(re_result4)
            result.append(line)
        with open(self.a2p(tbl_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def ipt2x(self):
        '''
        粒子效果显示修正，部分游戏对话框修正
        '''
        ipt_file_ls = file_list(self.game_data, 'ipt')
        for ipt_file in ipt_file_ls:
            result = []
            lines, current_encoding = self.get_lines_encoding(ipt_file)
            for line in lines:
                keyn_ls = ['x', 'y', 'w', 'h', 'ax', 'ay']
                for keyn in keyn_ls:
                    pattern = re.compile(rf'(.*\W+{keyn}\W+)(\d+)(.*)')
                    re_result = re.match(pattern, line)
                    if re_result:
                        line = self.line_pattern_num2x(re_result)
                pattern2 = re.compile(r'(.*\W+")(\d+.*?)(".*)')
                re_result2 = re.match(pattern2, line)
                if re_result2:
                    line2ls = list(re_result2.groups())
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
            self._count_process += 1

    def ast2x(self):
        ast_file_ls = file_list(self.game_data, 'ast')
        self.pool_run(self.ast_file_2x, ast_file_ls)
        self._count_process += len(ast_file_ls)

    def ast_file_2x(self, ast_file):
        '''
        人物位置修正，剧本文件
        '''
        # for ast_file in file_list(self.game_data, 'ast'):
        result = []
        lines, current_encoding = self.get_lines_encoding(ast_file)
        for line in lines:
            keyn_ls = ['mx', 'my', 'ax', 'ay', 'bx', 'by', 'x', 'y', 'x2', 'y2']
            for keyn in keyn_ls:
                pattern = re.compile(rf'(.*\W+{keyn}\W+?)(-?\d+)(.*)')
                re_result = re.match(pattern, line)
                if re_result:
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        with open(self.a2p(ast_file), 'w', newline='', encoding=current_encoding) as f:
            for line in result:
                f.write(line)

    def lua2x(self):
        lua_file_ls = file_list(self.game_data, 'lua')
        self.pool_run(self.lua_file_2x, lua_file_ls)
        self._count_process += len(lua_file_ls)

    def lua_file_2x(self, lua_file):
        '''
        部分游戏音量值位置修正
        '''
        # for lua_file in file_list(self.game_data, 'lua'):
        changed_sign = 0
        lines, current_encoding = self.get_lines_encoding(lua_file)
        result = []
        keyn_ls = ['width', 'height', 'left', 'top', 'x', 'y']
        for line in lines:
            for keyn in keyn_ls:
                pattern = re.compile(rf'(.*\W+{keyn}\W+)(\d+)(.*)')
                re_result = re.match(pattern, line)
                if re_result:
                    changed_sign = 1
                    line = self.line_pattern_num2x(re_result)
            result.append(line)
        if changed_sign == 1:
            with open(self.a2p(lua_file), 'w', newline='', encoding=current_encoding) as f:
                for line in result:
                    f.write(line)

    """
    ==================================================
    Artemis引擎图片文件：png(可能包含立绘坐标)
    ==================================================
    """

    def image2x(self):
        self.emit_info('开始处理游戏图片......')
        self.png2x()

    def png2x(self):
        png_file_ls = file_list(self.game_data, 'png')
        for png_file in png_file_ls:
            fcopy(png_file, self.a2t(png_file).parent)
        self.image_upscale(self.tmp_folder, self.tmp_folder, self.scale_ratio, 'png', count_class=self.count_class)
        self.emit_info('正在将立绘坐标信息写入到png图片')
        png_text_dict = self.get_all_png_text()
        for png_file, png_text in png_text_dict.items():
            self.write_png_text_(png_file, png_text)
        for png_file in file_list(self.tmp_folder, 'png'):
            fmove(png_file, self.t2p(png_file).parent)
        self.tmp_clear()

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
            png_text = self.read_png_text(png_file)
            if png_text:
                scaled_png_text = self.png_text_2x(png_text, self.scale_ratio)
                png_text_dict[scaled_png_path] = scaled_png_text
        return png_text_dict

    """
    ==================================================
    Artemis引擎动画文件：ogv
    ==================================================
    """

    def animation2x(self):
        self.emit_info('开始处理游戏动画......')
        self.ogv2x()

    def ogv2x(self):
        ogv_file_ls = file_list(self.game_data, 'ogv')
        if ogv_file_ls:
            for ogv_file in ogv_file_ls:
                output_video = self.a2t(ogv_file)
                output_video = self.video_upscale(ogv_file, output_video, self.scale_ratio)
                target_ogv = fmove(output_video, self.t2p(output_video).parent)
                self.tmp_clear()
                self._count_process += 1
                self.emit_info(f'{target_ogv} saved!')

    """
    ==================================================
    Artemis引擎视频文件：wmv2、dat(wmv3)
    ==================================================
    """

    def video2x(self):
        self.emit_info('开始处理游戏视频......')
        video_extension_ls = ['wmv', 'dat', 'mp4', 'avi', 'mpg', 'mkv']
        for video_extension in video_extension_ls:
            video_file_ls = [video_file for video_file in file_list(self.game_data, video_extension) if self.video_info(video_file)]
            if video_file_ls:
                self.emit_info(f'{video_extension}视频放大中......')
                for video_file in video_file_ls:
                    self.emit_info(f'{video_file} 处理中......')
                    tmp_video = fcopy(video_file, self.a2t(video_file).parent)
                    if video_extension == 'dat':
                        tmp_video = tmp_video.replace(tmp_video.with_suffix('.wmv'))
                    output_vcodec = None
                    if self.video_info(video_file)['vcodec'] == 'wmv3':
                        output_vcodec = 'wmv2'
                    output_video = self.video_upscale(tmp_video, tmp_video, self.scale_ratio, output_vcodec=output_vcodec)
                    if video_extension == 'dat':
                        output_video = output_video.replace(output_video.with_suffix('.dat'))
                    target_video = fmove(output_video, self.t2p(output_video).parent)
                    self.tmp_clear()
                    self._count_process += 1
                    self.emit_info(f'{target_video} saved!')

    """
    ==================================================
    Artemis引擎封包文件：pfs
    ==================================================
    """

    class Pfs(KaitaiStruct):
        """
        @brief      Artemis引擎pfs封包文件，modified from https://github.com/Forlos/vn_re
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\x70\x66\x38")
            self.header = self._root.Header(self._io, self, self._root)
            self.entries = [None] * (self.header.file_entries_count)
            for i in range(self.header.file_entries_count):
                self.entries[i] = self._root.FileEntry(self._io, self, self._root)

        class Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.archive_data_size = self._io.read_u4le()
                self.file_entries_count = self._io.read_u4le()

        class FileEntry(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.file_name_size = self._io.read_u4le()
                self.file_name = self._io.read_bytes(self.file_name_size)
                self.unk = self._io.read_u4le()
                self.file_offset = self._io.read_u4le()
                self.file_size = self._io.read_u4le()

        @property
        def raw_archive_data(self):
            if hasattr(self, '_m_raw_archive_data'):
                return self._m_raw_archive_data if hasattr(self, '_m_raw_archive_data') else None

            _pos = self._io.pos()
            self._io.seek(7)
            self._m_raw_archive_data = self._io.read_bytes(self.header.archive_data_size)
            self._io.seek(_pos)
            return self._m_raw_archive_data if hasattr(self, '_m_raw_archive_data') else None

    def batch_extract_pfs(self, input_folder, output_folder, encoding='utf-8') -> list:
        """
        @brief      pfs批量解包

        @param      input_folder   输入文件夹
        @param      output_folder  输出文件夹
        @param      encoding       编码格式

        @return     输出文件列表
        """
        # 计时
        start_time = time.time()
        input_folder = Path(input_folder).resolve()
        output_folder = Path(output_folder).resolve()
        output_file_ls = []
        pfs_file_ls = [str(pfs_file) for pfs_file in file_list(input_folder) if '.pfs' in pfs_file.name]
        pfs_file_ls.sort()
        count = 0
        all_count = len(pfs_file_ls)
        for pfs_file in pfs_file_ls:
            self.emit_info(f'{pfs_file} extracting......')
            output_file_ls += self.extract_pfs(pfs_file, output_folder, encoding)
            if self.has_connected_ui:
                count += 1
                now_percent = int(count/all_count*100)
                _ui_runner_.progress_sig.emit(now_percent)
        # 去重
        # real_output_file_ls = list(set(output_file_ls))
        # real_output_file_ls.sort(key=output_file_ls.index)
        # 输出耗时
        timing_count = time.time() - start_time
        self.emit_info(seconds_format(timing_count))
        self.emit_info(f'拆包完成!\n请把游戏目录中类似script、movie等文件夹及*.ini文件也复制到：\n{output_folder}中')
        return output_file_ls

    def extract_pfs(self, pfs_file, output_folder, encoding='utf-8') -> list:
        """
        @brief      pfs解包

        @param      pfs_file       pfs文件路径
        @param      output_folder  输出文件夹
        @param      encoding       编码格式

        @return     输出文件列表
        """
        pfs_file = Path(pfs_file).resolve()
        pfs = Artemis.Pfs.from_file(pfs_file)
        s1 = hashlib.sha1()
        s1.update(pfs.raw_archive_data)
        digest = s1.digest()
        entry_name_contents_offset_list = []
        for entry in pfs.entries:
            with open(pfs_file, 'rb') as archive:
                archive.seek(entry.file_offset)
                a = entry.file_name.decode(encoding)
                b = bytearray(archive.read(entry.file_size))
                entry_name_contents_offset_list.append((a, b))
        target_file_ls = self.pool_run(self.decrypt_pfs_and_save_file, entry_name_contents_offset_list, output_folder, digest)
        return target_file_ls

    def decrypt_pfs_and_save_file(self, entry_name_contents_offset, output_folder, digest) -> Path:
        target_file = output_folder/entry_name_contents_offset[0]
        if not target_file.parent.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
        contents = entry_name_contents_offset[1]
        len_contents = len(contents)
        len_digest = len(digest)
        contents = self.decrypt_pfs_contents(contents, digest, len_contents, len_digest)
        with open(target_file, 'wb') as f:
            f.write(contents)
        return target_file

    @jit(fastmath=True)
    def decrypt_pfs_contents(self, contents, digest, len_contents, len_digest):
        for i in range(len_contents):
            contents[i] ^= digest[i % len_digest]
        return contents
