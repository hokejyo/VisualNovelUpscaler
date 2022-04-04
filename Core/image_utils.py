# -*- coding: utf-8 -*-

from .functions import *


class ImageUtils(object):
    """
    @brief      专用于处理图片文件
    """

    @staticmethod
    def read_png_text(png_file) -> tuple:
        """
        @brief      读取png图片中的文本信息

        @param      png_file  图片文件

        @return     以元组保存的文本信息块
        """
        reader = png.Reader(filename=png_file)
        for text_chunk in reader.chunks():
            if text_chunk[0] == b'tEXt':
                return text_chunk
        return None

    def png_text_2x(self, text_chunk, scale_ratio) -> tuple:
        """
        @brief      将png图片中的文本信息中的数字放大(适用于部分将坐标存储在png图片中的游戏)

        @param      text_chunk   文本信息元组
        @param      scale_ratio  放大倍数

        @return     放大后的文本信息元组
        """
        text_ls = list(text_chunk)
        text = text_ls[1]
        for png_text_encoding in self.encoding_list:
            try:
                tmp_ls = str(text, png_text_encoding).split(',')
                current_encoding = png_text_encoding
                break
            except:
                continue
        for i in range(len(tmp_ls)):
            if real_digit(tmp_ls[i]):
                tmp_ls[i] = str(int(int(tmp_ls[i]) * scale_ratio))
        new_text = ','.join(tmp_ls)
        new_text2bytes = bytes(new_text, current_encoding)
        text_ls[1] = new_text2bytes
        return tuple(text_ls)

    @staticmethod
    def write_png_text_(png_file, png_text) -> Path:
        """
        @brief      将文本信息写入到png图片

        @param      png_file  需要写入文本的png图片
        @param      png_text  文本信息元组，格式：(b'tEXt', b'')
        """
        reader = png.Reader(filename=png_file)
        # 删除原图片中的文本信息块
        new_chunks = [chunk for chunk in reader.chunks() if chunk[0] != b'tEXt']
        # 插入文本块
        new_chunks.insert(1, png_text)
        with open(png_file, 'wb') as f:
            png.write_chunks(f, new_chunks)
        return png_file

    @staticmethod
    def get_image_format(image_path) -> str:
        """
        @brief      获取图片真实格式

        @param      image_path  图片路径

        @return     图片格式
        """
        return Image.open(image_path).format.lower()

    @staticmethod
    def image_resize_(image_file, zoom_factor) -> Path:
        """
        @brief      图片缩放，覆盖原图片，基于pillow

        @param      image_file   图片文件路径
        @param      zoom_factor  缩放系数
        """
        image = Image.open(image_file)
        if zoom_factor != 1:
            image_resize = image.resize((int(image.width * zoom_factor),
                                         int(image.height * zoom_factor)),
                                        Image.LANCZOS).save(image_file)
        return image_file

    @staticmethod
    def image_convert_(input_path, output_extention) -> Path:
        """
        @brief      图片格式转换，删除原图片，基于pillow

        @param      input_path        输入图片路径
        @param      output_extention  输出图片格式

        @return     输出图片路径对象
        """
        output_path = input_path.with_suffix('.' + output_extention)
        if output_path != input_path:
            try:
                Image.open(input_path).save(output_path, quality=100)
            except:
                Image.open(input_path).convert('RGB').save(output_path, quality=100)
            input_path.unlink()
        return output_path

    @staticmethod
    def _palette_png_pre_(input_path) -> Path:
        """
        @brief      PALETTE PNG图片预处理为RGBA或RGB

        @param      input_path  输入路径

        @return     输出文件路径
        """
        if input_path.suffix.lower() == '.png':
            img = Image.open(input_path)
            if img.mode == 'P':
                for chunk_tuple in png.Reader(filename=input_path).chunks():
                    if b'tRNS' in chunk_tuple:
                        img.convert('RGBA').save(input_path, quality=100)
                        return input_path
                img.convert('RGB').save(input_path, quality=100)
                return input_path

    def image_upscale(self,
                      input_path,
                      output_folder,
                      scale_ratio=2.0,
                      output_extention='png',
                      filters=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'],
                      walk_mode=True,
                      video_mode=False
                      ) -> list:
        """
        @brief      放大图片

        @param      input_path        输入图片路径，可以是文件或文件夹
        @param      output_folder     输出文件夹
        @param      scale_ratio       放大倍数
        @param      output_extention  输出图片格式
        @param      filters           格式过滤器
        @param      walk_mode         是否处理子文件夹中的图片，默认是
        @param      video_mode        使用视频超分引擎

        @return     所有输出图片的路径对象列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        single_file_mode = False if input_path.is_dir() else True
        # 获取超分引擎和分组数量
        sr_engine = self.video_sr_engine if video_mode else self.image_sr_engine
        upscale_batch_size = self.video_batch_size if video_mode else self.image_batch_size
        # 获取原始图片文件列表
        org_image_ls = []
        _filters = [('.' + extension).lower() for extension in filters]
        if single_file_mode:
            if input_path.suffix.lower() in _filters:
                org_image_ls.append(input_path)
        else:
            org_image_ls = [file_path for file_path in input_path.file_list(walk_mode=walk_mode) if file_path.suffix.lower() in _filters]
        output_image_list = []
        # 记录总数和开始时间
        len_org_image_ls = len(org_image_ls)
        _start_time = time.time()
        if len_org_image_ls != 0:
            group_list = batch_group_list(org_image_ls, batch_size=upscale_batch_size)
            for group in group_list:
                # 创建两个临时文件夹
                with tempfile.TemporaryDirectory() as img_tmp_folder1:
                    img_tmp_folder1 = Path(img_tmp_folder1)
                    with tempfile.TemporaryDirectory() as img_tmp_folder2:
                        img_tmp_folder2 = Path(img_tmp_folder2)
                        # 避免不同文件夹重名文件错误覆盖
                        tmp_target_dict = {}
                        for image_file in group:
                            tmp_stem = self.create_str()
                            if single_file_mode:
                                target_image_file = image_file.reio_path(input_path.parent, output_folder, mk_dir=True).with_suffix('.' + output_extention)
                            else:
                                target_image_file = image_file.reio_path(input_path, output_folder, mk_dir=True).with_suffix('.' + output_extention)
                            tmp_target_dict[tmp_stem] = target_image_file
                            tmp_image_file = img_tmp_folder1 / (tmp_stem + image_file.suffix)
                            image_file.copy_as(tmp_image_file)
                            # 预处理
                            self._palette_png_pre_(tmp_image_file)
                        # 放大tmp1到tmp2
                        options, step_scale_ratio = self._get_options_and_step_scale_ratio(img_tmp_folder1, img_tmp_folder2, sr_engine)
                        image_upscale_p = subprocess.run(options, capture_output=True)
                        actual_scale_ratio = step_scale_ratio
                        # 未达指定倍数循环放大
                        while actual_scale_ratio < scale_ratio:
                            img_tmp_folder2.move_as(img_tmp_folder1)
                            img_tmp_folder2.mk_dir(parents=True, exist_ok=True)
                            image_upscale_p = subprocess.run(options, capture_output=True)
                            actual_scale_ratio *= step_scale_ratio
                        tmp_image_ls = img_tmp_folder2.file_list()
                        # 缩放
                        zoom_factor = scale_ratio/actual_scale_ratio
                        if zoom_factor != 1:
                            tmp_image_ls = self.pool_run(self.image_resize_, tmp_image_ls, zoom_factor)
                        # 转格式
                        tmp_image_ls = self.pool_run(self.image_convert_, tmp_image_ls, output_extention)
                        for tmp_image in tmp_image_ls:
                            target_image_file = tmp_target_dict[tmp_image.stem]
                            tmp_image.move_as(target_image_file)
                            output_image_list.append(target_image_file)
                # 进度更新
                len_finished_image_list = len(output_image_list)
                _now_time = time.time()
                self._update_progress_and_left_time(len_org_image_ls, len_finished_image_list, _start_time, _now_time)
        else:
            self.emit_progress(100, 0)
        return output_image_list

    def _get_options_and_step_scale_ratio(self, in_folder, out_folder, sr_engine):
        if sr_engine == 'waifu2x_ncnn':
            options, step_scale_ratio = self._waifu2x_ncnn_options_and_step_scale_ratio(in_folder, out_folder)
        elif sr_engine == 'real_cugan':
            options, step_scale_ratio = self._real_cugan_options_and_step_scale_ratio(in_folder, out_folder)
        elif sr_engine == 'real_esrgan':
            options, step_scale_ratio = self._real_esrgan_options_and_step_scale_ratio(in_folder, out_folder)
        elif sr_engine == 'srmd_ncnn':
            options, step_scale_ratio = self._srmd_ncnn_options_and_step_scale_ratio(in_folder, out_folder)
        elif sr_engine == 'realsr_ncnn':
            options, step_scale_ratio = self._realsr_ncnn_options_and_step_scale_ratio(in_folder, out_folder)
        elif sr_engine == 'anime4k':
            options, step_scale_ratio = self._anime4k_options_and_step_scale_ratio(in_folder, out_folder)
        else:
            raise Exception('请选择正确的超分引擎！')
        return options, step_scale_ratio

    def _waifu2x_ncnn_options_and_step_scale_ratio(self, in_folder, out_folder):
        step_scale_ratio = 2
        options = [self.waifu2x_ncnn_exe,
                   '-i', in_folder,
                   '-o', out_folder,
                   '-n', self.waifu2x_ncnn_noise_level,
                   '-s', str(step_scale_ratio),
                   '-t', self.waifu2x_ncnn_tile_size,
                   '-m', self.waifu2x_ncnn_model_path,
                   '-g', self.gpu_id,
                   '-j', self.waifu2x_ncnn_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.tta == '0':
            options.remove('-x')
        return options, step_scale_ratio

    def _real_cugan_options_and_step_scale_ratio(self, in_folder, out_folder):
        # 因为原版3倍和4倍不稳定，暂时只保留2倍
        step_scale_ratio = 2
        options = [self.real_cugan_exe,
                   '-i', in_folder,
                   '-o', out_folder,
                   '-n', self.real_cugan_noise_level,
                   '-s', str(step_scale_ratio),
                   '-t', self.real_cugan_tile_size,
                   '-c', self.real_cugan_sync_gap_mode,
                   '-m', self.real_cugan_model_path,
                   '-g', self.gpu_id,
                   '-j', self.real_cugan_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.tta == '0':
            options.remove('-x')
        return options, step_scale_ratio

    def _real_esrgan_options_and_step_scale_ratio(self, in_folder, out_folder):
        if self.real_esrgan_model_name == 'RealESRGANv2-animevideo-xsx2':
            step_scale_ratio = 2
        else:
            step_scale_ratio = 4
        options = [self.real_esrgan_exe,
                   '-i', in_folder,
                   '-o', out_folder,
                   '-s', str(step_scale_ratio),
                   '-t', self.real_esrgan_tile_size,
                   '-m', self.real_esrgan_model_path,
                   '-n', self.real_esrgan_model_name,
                   '-g', self.gpu_id,
                   '-j', self.real_esrgan_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.tta == '0':
            options.remove('-x')
        return options, step_scale_ratio

    def _srmd_ncnn_options_and_step_scale_ratio(self, in_folder, out_folder):
        step_scale_ratio = 2
        options = [self.srmd_ncnn_exe,
                   '-i', in_folder,
                   '-o', out_folder,
                   '-n', self.srmd_ncnn_noise_level,
                   '-s', str(step_scale_ratio),
                   '-t', self.srmd_ncnn_tile_size,
                   '-m', self.srmd_ncnn_model_path,
                   '-g', self.gpu_id,
                   '-j', self.srmd_ncnn_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.tta == '0':
            options.remove('-x')
        return options, step_scale_ratio

    def _realsr_ncnn_options_and_step_scale_ratio(self, in_folder, out_folder):
        step_scale_ratio = 4
        options = [self.realsr_ncnn_exe,
                   '-i', in_folder,
                   '-o', out_folder,
                   '-s', str(step_scale_ratio),
                   '-t', self.realsr_ncnn_tile_size,
                   '-m', self.realsr_ncnn_model_path,
                   '-g', self.gpu_id,
                   '-j', self.realsr_ncnn_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.tta == '0':
            options.remove('-x')
        return options, step_scale_ratio

    def _anime4k_options_and_step_scale_ratio(self, in_folder, out_folder):
        step_scale_ratio = 2
        options = [self.anime4k_exe,
                   '-i', in_folder,
                   '-z', str(step_scale_ratio),
                   '-t', str(self.cpu_cores),
                   '-b',
                   '-q',
                   '-d', self.gpu_id,
                   '-A',
                   '-o', out_folder
                   ]
        if self.anime4k_acnet == '1':
            options.insert(-2, '-w')
            if self.anime4k_hdn_mode == '1':
                options.insert(-2, '-H')
                options.insert(-2, '-L')
                options.insert(-2, self.anime4k_hdn_level)
        return options, step_scale_ratio

    def _update_progress_and_left_time(self, len_org_image_ls, len_finished_image_list, _start_time, _now_time):
        if len_finished_image_list == 0:
            _percent = 0
            _lefe_time = 0
        else:
            _progress = len_finished_image_list / len_org_image_ls
            passed_time = _now_time - _start_time
            _percent = int(_progress * 100)
            _lefe_time = passed_time / _progress - passed_time
        self.emit_progress(_percent, _lefe_time)
