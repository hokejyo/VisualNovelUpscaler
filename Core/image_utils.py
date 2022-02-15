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
        @brief      将png图片中的文本信息中的数字放大

        @param      text_chunk  文本信息元组

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

    def zoom_image(self, image_file, zoom_factor):
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

    def convert_image(self, input_path, output_extention, del_input=False) -> Path:
        """
        @brief      图片格式转换

        @param      input_path        输入路径
        @param      output_extention  输出图片格式
        @param      del_input         是否删除输入图片

        @return     输出图片路径对象
        """
        input_path = Path(input_path)
        output_path = input_path.with_suffix('.'+output_extention)
        try:
            Image.open(input_path).save(output_path, quality=100)
        except:
            Image.open(input_path).convert('RGB').save(output_path, quality=100)
        if del_input and (output_path != input_path):
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

    def image_upscale(self, input_path, output_folder, output_extention='png') -> list:
        """
        @brief      放大图片

        @param      input_path        输入路径
        @param      output_folder     输出文件夹路径
        @param      output_extention  输出图片格式

        @return     输出图片路径对象列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        match self.super_resolution_engine:
            # 使用ncnn框架超分辨率引擎放大图片
            case 'waifu2x_ncnn' | 'real_esrgan' | 'srmd_ncnn' | 'realsr_ncnn':
                scaled_image_file_ls = self.ncnn_vulkan_series(input_path, output_folder, output_extention)
            case _:
                print('请选择正确的超分辨率引擎')
                scaled_image_file_ls = []
        return scaled_image_file_ls

    def ncnn_vulkan_series(self, input_path, output_folder, output_extention) -> list:
        """
        @brief      使用ncnn框架超分辨率引擎放大图片

        @param      input_path        输入路径
        @param      output_folder     输出文件夹路径
        @param      output_extention  输出图片格式

        @return     输出图片路径对象列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        scaled_image_file_ls = []
        if input_path.is_dir():
            folders = input_path.rglob('**/')
            for folder in folders:
                target_folder = output_folder/folder.relative_to(input_path)
                scaled_image_file_ls += self.ncnn_vulkan_folder(folder, target_folder, output_extention)
        elif input_path.is_file():
            scaled_image_file = self.ncnn_vulkan_single(input_path, output_folder, output_extention)
            scaled_image_file_ls.append(scaled_image_file)
        return scaled_image_file_ls

    def ncnn_vulkan_single(self, input_path, output_folder, output_extention) -> Path:
        """
        @brief      使用ncnn框架超分辨率引擎放大单张图片

        @param      input_path        输入路径
        @param      output_folder     输出文件夹
        @param      output_extention  输出图片格式

        @return     输出图片路径
        """
        input_path = Path(input_path)
        output_path = Path(output_folder)/(input_path.stem+'.'+output_extention)
        # 先全部输出为png格式的临时图片文件
        tmp_path = Path(output_folder)/(input_path.stem+'_tmp_output.png')
        match self.super_resolution_engine:
            case 'waifu2x_ncnn':
                # 将指定放大倍数转换成waifu2x-ncnn-valkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.waifu2x_ncnn_exe,
                           '-i', input_path,
                           '-o', tmp_path,
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
            case 'real_esrgan':
                # 将指定放大倍数转换成Real-ESRGAN支持的放大倍数
                if self.real_esrgan_model_name == 'RealESRGANv2-animevideo-xsx2':
                    actiual_scale_ratio = self.get_actual_scale_ratio(2)
                else:
                    actiual_scale_ratio = self.get_actual_scale_ratio(4)
                options = [self.real_esrgan_exe,
                           '-i', input_path,
                           '-o', tmp_path,
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
                           '-i', input_path,
                           '-o', tmp_path,
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
                           '-i', input_path,
                           '-o', tmp_path,
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
        ncnn_vulkan_p = subprocess.run(options, capture_output=True)
        # 缩放
        zoom_factor = self.scale_ratio/actiual_scale_ratio
        if zoom_factor != 1:
            self.zoom_image(tmp_path, zoom_factor)
        # 转格式
        if output_extention != 'png':
            tmp_path = self.convert_image(tmp_path, output_extention, del_input=True)
        tmp_path.replace(output_path)
        return output_path

    def ncnn_vulkan_folder(self, input_path, output_folder, output_extention) -> list:
        """
        @brief      使用ncnn框架超分辨率引擎放大单个文件夹中的图片，文件夹内图片格式需保持一致，目前的最佳选择，失真较小

        @param      input_path        输入文件夹
        @param      output_folder     输出文件夹
        @param      output_extention  输出图片格式

        @return     输出图片路径列表
        """
        # 记录原文件名/放大后的临时文件名
        input_folder = Path(input_path)
        output_folder = Path(output_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
        # 放大，先全部输出为png格式
        tmp_folder = output_folder.parent/(output_folder.name+'_tmp_output')
        tmp_folder.mkdir(parents=True, exist_ok=True)
        match self.super_resolution_engine:
            case 'waifu2x_ncnn':
                # 将指定放大倍数转换成waifu2x-ncnn-valkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.waifu2x_ncnn_exe,
                           '-i', input_folder,
                           '-o', tmp_folder,
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
            case 'real_esrgan':
                # 将指定放大倍数转换成Real-ESRGAN支持的放大倍数
                if self.real_esrgan_model_name == 'RealESRGANv2-animevideo-xsx2':
                    actiual_scale_ratio = self.get_actual_scale_ratio(2)
                else:
                    actiual_scale_ratio = self.get_actual_scale_ratio(4)
                options = [self.real_esrgan_exe,
                           '-i', input_folder,
                           '-o', tmp_folder,
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
                           '-i', input_folder,
                           '-o', tmp_folder,
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
                           '-i', input_folder,
                           '-o', tmp_folder,
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
        ncnn_vulkan_p = subprocess.run(options, capture_output=True)
        # 获取临时文件夹中的图片列表
        tmp_image_ls = file_list(tmp_folder, 'png', walk_mode=False)
        # 缩放
        zoom_factor = self.scale_ratio/actiual_scale_ratio
        if zoom_factor != 1:
            self.pool_run(self.zoom_image, tmp_image_ls, zoom_factor)
        # 转格式
        if output_extention != 'png':
            tmp_image_ls = self.pool_run(self.convert_image, tmp_image_ls, output_extention, True)
        output_image_ls = []
        for tmp_image in tmp_image_ls:
            output_image_ls.append(output_folder/tmp_image.name)
            fmove(tmp_image, output_folder)
        shutil.rmtree(tmp_folder)
        return output_image_ls
