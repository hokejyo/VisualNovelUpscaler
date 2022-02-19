# -*- coding: utf-8 -*-

from .functions import *


class ImageUtils(object):
    """
    @brief      专用于处理图片文件
    """

    def read_png_text(self, png_file) -> tuple:
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
                tmp_ls[i] = str(int(int(tmp_ls[i])*scale_ratio))
        new_text = ','.join(tmp_ls)
        new_text2bytes = bytes(new_text, current_encoding)
        text_ls[1] = new_text2bytes
        return tuple(text_ls)

    def write_png_text(self, png_file, png_text):
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

    def alpha_image(self, image_path) -> bool:
        """
        @brief      检查图片是否含有alpha通道

        @param      image_path  图片路径

        @return     bool
        """
        return True if Image.open(image_path).mode in ['RGBA', 'LA'] else False

    def get_image_format(self, image_path) -> str:
        """
        @brief      获取图片真实格式

        @param      image_path  图片路径

        @return     图片格式
        """
        return Image.open(image_path).format.lower()

    def zoom_image_(self, image_file, zoom_factor) -> Path:
        """
        @brief      图片缩放，覆盖原图片

        @param      image_file   图片文件路径
        @param      zoom_factor  缩放系数
        """
        image_file = Path(image_file)
        image = Image.open(image_file)
        image_resize = image.resize((int(image.width*zoom_factor),
                                     int(image.height*zoom_factor)),
                                    Image.ANTIALIAS)
        image_resize.save(image_file)
        return image_file

    def convert_image_(self, input_path, output_extention) -> Path:
        """
        @brief      图片格式转换，删除原图片

        @param      input_path        输入图片路径
        @param      output_extention  输出图片格式

        @return     输出图片路径对象
        """
        input_path = Path(input_path)
        output_path = input_path.with_suffix('.'+output_extention)
        if output_path != input_path:
            try:
                Image.open(input_path).save(output_path, quality=100)
            except:
                Image.open(input_path).convert('RGB').save(output_path, quality=100)
            input_path.unlink()
        return output_path

    def get_actual_scale_ratio(self, legal_scale_ratio) -> int:
        """
        @brief      获取不同超分辨率引擎下的实际放大倍率

        @param      legal_scale_ratio  不同超分辨率引擎支持的放大倍率

        @return     实际放大倍率
        """
        actual_scale_ratio = legal_scale_ratio**ceil(log(self.scale_ratio, legal_scale_ratio))
        return actual_scale_ratio

    def image_upscale(self,
                      input_path,
                      output_folder,
                      output_extention='png',
                      filters=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'],
                      walk_mode=True,
                      video_mode=False
                      ) -> list:
        """
        @brief      放大图片

        @param      input_path        输入图片路径，可以是文件或文件夹
        @param      output_folder     输出文件夹
        @param      output_extention  输出图片格式
        @param      filters           格式过滤器
        @param      walk_mode         是否处理子文件夹中的图片，默认是
        @param      video_mode        使用视频超分引擎

        @return     所有输出图片的路径对象列表
        """
        input_path = Path(input_path).resolve()
        single_file_mode = False if input_path.is_dir() else True
        output_folder = Path(output_folder).resolve()
        sr_engine = self.video_sr_engine if video_mode else self.image_sr_engine
        output_image_ls = []
        for extension in filters:
            if single_file_mode:
                org_image_ls = []
                org_image_ls.append(input_path)
            else:
                org_image_ls = file_list(input_path, extension, walk_mode=walk_mode)
            if org_image_ls:
                tmp_folder1 = output_folder.parent/('sr_tmp1_'+self.create_str())
                tmp_folder2 = output_folder.parent/('sr_tmp2_'+self.create_str())
                group_list = batch_group_list(org_image_ls, batch_size=self.upscale_batch_size)
                for group in group_list:
                    tmp_folder1.mkdir(parents=True)
                    tmp_folder2.mkdir(parents=True)
                    # 避免不同文件夹重名文件错误覆盖
                    tmp_target_dict = {}
                    for image_file in group:
                        tmp_name = self.create_str()
                        if single_file_mode:
                            target_image_file = p2p(image_file, input_path.parent, output_folder)
                        else:
                            target_image_file = p2p(image_file, input_path, output_folder)
                        tmp_target_dict[tmp_name] = target_image_file
                        tmp_image_file = tmp_folder1/(tmp_name+image_file.suffix)
                        shutil.copy(image_file, tmp_image_file)
                    # 放大tmp1到tmp2
                    options, zoom_factor = self.get_options_and_zoom_factor(tmp_folder1, tmp_folder2, sr_engine)
                    image_upscale_p = subprocess.run(options, capture_output=True)
                    tmp_image_ls = file_list(tmp_folder2)
                    # 缩放
                    if zoom_factor != 1:
                        tmp_image_ls = self.pool_run(self.zoom_image_, tmp_image_ls, zoom_factor)
                    # 转格式
                    tmp_image_ls = self.pool_run(self.convert_image_, tmp_image_ls, output_extention)
                    for tmp_image in tmp_image_ls:
                        target_image_file = tmp_target_dict[tmp_image.stem]
                        tmp_image.replace(target_image_file)
                        print(f'{target_image_file} saved!')
                        output_image_ls.append(target_image_file)
                    shutil.rmtree(tmp_folder1)
                    shutil.rmtree(tmp_folder2)
            if single_file_mode:
                break
        return output_image_ls

    def get_options_and_zoom_factor(self, in_folder, out_folder, sr_engine):
        """
        @brief      获取image_upscale函数所需的命令和实际缩放系数

        @param      in_folder   输出文件夹
        @param      out_folder  输出文件夹
        @param      sr_engine   超分引擎

        @return     命令和实际缩放系数
        """
        match sr_engine:
            case 'waifu2x_ncnn':
                # 将指定放大倍数转换成waifu2x-ncnn-valkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.waifu2x_ncnn_exe,
                           '-i', in_folder,
                           '-o', out_folder,
                           '-n', self.waifu2x_ncnn_noise_level,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.waifu2x_ncnn_tile_size,
                           '-m', self.waifu2x_ncnn_model_path,
                           '-g', self.gpu_id,
                           '-j', self.waifu2x_ncnn_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
                if self.tta == '0':
                    options.remove('-x')
            case 'real_cugan':
                # 将指定放大倍数转换成Real-CUGAN支持的放大倍数
                if self.scale_ratio <= 4:
                    actiual_scale_ratio = ceil(self.scale_ratio)
                    # 等bug修复后删除下面两行
                    if actual_scale_ratio == 3:
                        actual_scale_ratio = 4
                else:
                    raise Exception('Real-Cugan仅支持4倍以下放大倍率!')
                options = [self.real_cugan_exe,
                           '-i', in_folder,
                           '-o', out_folder,
                           '-n', self.real_cugan_noise_level,
                           '-s', str(actiual_scale_ratio),
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
            case 'real_esrgan':
                # 将指定放大倍数转换成Real-ESRGAN支持的放大倍数
                if self.real_esrgan_model_name == 'RealESRGANv2-animevideo-xsx2':
                    actiual_scale_ratio = self.get_actual_scale_ratio(2)
                else:
                    actiual_scale_ratio = self.get_actual_scale_ratio(4)
                options = [self.real_esrgan_exe,
                           '-i', in_folder,
                           '-o', out_folder,
                           '-s', str(actiual_scale_ratio),
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
            case 'srmd_ncnn':
                # 将指定放大倍数转换成srmd-ncnn-vulkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.srmd_ncnn_exe,
                           '-i', in_folder,
                           '-o', out_folder,
                           '-n', self.srmd_ncnn_noise_level,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.srmd_ncnn_tile_size,
                           '-m', self.srmd_ncnn_model_path,
                           '-g', self.gpu_id,
                           '-j', self.srmd_ncnn_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
                if self.tta == '0':
                    options.remove('-x')
            case 'realsr_ncnn':
                # 将指定放大倍数转换成realsr-ncnn-vulkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(4)
                options = [self.realsr_ncnn_exe,
                           '-i', in_folder,
                           '-o', out_folder,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.realsr_ncnn_tile_size,
                           '-m', self.realsr_ncnn_model_path,
                           '-g', self.gpu_id,
                           '-j', self.realsr_ncnn_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
                if self.tta == '0':
                    options.remove('-x')
            case 'anime4k':
                # anime4kcpp非整数倍放大会有alpha通道错位的bug
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.anime4k_exe,
                           '-i', in_folder,
                           '-z', str(actiual_scale_ratio),
                           '-t', str(self.cpu_cores),
                           '-b',
                           '-q',
                           '-d', self.gpu_id,
                           '-w',
                           '-A',
                           '-o', out_folder
                           ]
                if self.anime4k_acnet == '0':
                    options.remove('-w')
            case _:
                raise Exception('请选择正确的超分引擎！')
        zoom_factor = self.scale_ratio/actiual_scale_ratio
        return options, zoom_factor
