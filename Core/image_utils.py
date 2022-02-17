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

    def zoom_image_(self, image_file, zoom_factor):
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

    def image_upscale(self, input_path, output_folder, output_extention='png', video_mode=False) -> list:
        """
        @brief      图片超分辨率，递归处理子文件夹中的图片，输出时保持目录结构

        @param      input_path        输入路径，可以是文件或文件夹
        @param      output_folder     输出文件夹路径
        @param      output_extention  输出图片格式
        @param      video_mode        视频处理模式

        @return     输出图片的路径列表
        """
        input_path = Path(input_path)
        output_folder = Path(output_folder)
        sr_engine = self.video_sr_engine if video_mode else self.image_sr_engine
        scaled_image_file_ls = []
        match sr_engine:
            case 'waifu2x_ncnn' | 'real_cugan' | 'real_esrgan' | 'srmd_ncnn' | 'realsr_ncnn':
                if input_path.is_dir():
                    folders = list(input_path.rglob('**/'))
                    for folder in folders:
                        target_folder = output_folder/folder.relative_to(input_path)
                        scaled_image_file_ls += self.image_upscale_ncnn(folder, target_folder, output_extention, sr_engine)
                else:
                    scaled_image_file_ls = self.image_upscale_ncnn(input_path, output_folder, output_extention, sr_engine)
            case 'anime4k':
                scaled_image_file_ls = self.image_upscale_anime4k(input_path, output_folder, output_extention)
            case _:
                raise Exception('请选择正确的超分引擎！')
        return scaled_image_file_ls

    def image_upscale_ncnn(self, input_path, output_folder, output_extention, sr_engine) -> list:
        """
        @brief      使用nihui构建的ncnn系列超分辨率引擎处理

        @param      input_path        输入路径
        @param      output_folder     输出文件夹
        @param      output_extention  输出图片格式
        @param      sr_engine         使用的超分辨率引擎名称

        @return     输出图片的路径列表
        """
        input_path = Path(input_path).resolve()
        output_folder = Path(output_folder).resolve()

        tmp_folder = output_folder.parent/(output_folder.name+'_vnc_tmp_image_upscale')
        tmp_folder.mkdir(parents=True, exist_ok=True)
        if input_path.is_dir():
            output_path = tmp_folder
        else:
            output_path = tmp_folder/input_path.with_suffix('.png').name

        match sr_engine:
            case 'waifu2x_ncnn':
                # 将指定放大倍数转换成waifu2x-ncnn-valkan支持的放大倍数
                actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options = [self.waifu2x_ncnn_exe,
                           '-i', input_path,
                           '-o', output_path,
                           '-n', self.waifu2x_ncnn_noise_level,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.waifu2x_ncnn_tile_size,
                           '-m', self.waifu2x_ncnn_model_path,
                           '-g', self.gpu_id,
                           '-j', self.waifu2x_ncnn_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
            case 'real_cugan':
                # 将指定放大倍数转换成Real-CUGAN支持的放大倍数
                if self.scale_ratio <= 4:
                    actiual_scale_ratio = ceil(self.scale_ratio)
                else:
                    raise Exception('Real-Cugan仅支持4倍以下放大倍率!')
                    # actiual_scale_ratio = self.get_actual_scale_ratio(2)
                options=[self.real_cugan_exe,
                           '-i', input_path,
                           '-o', output_path,
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
            case 'real_esrgan':
                # 将指定放大倍数转换成Real-ESRGAN支持的放大倍数
                if self.real_esrgan_model_name == 'RealESRGANv2-animevideo-xsx2':
                    actiual_scale_ratio=self.get_actual_scale_ratio(2)
                else:
                    actiual_scale_ratio=self.get_actual_scale_ratio(4)
                options=[self.real_esrgan_exe,
                           '-i', input_path,
                           '-o', output_path,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.real_esrgan_tile_size,
                           '-m', self.real_esrgan_model_path,
                           '-n', self.real_esrgan_model_name,
                           '-g', self.gpu_id,
                           '-j', self.real_esrgan_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
            case 'srmd_ncnn':
                # 将指定放大倍数转换成srmd-ncnn-vulkan支持的放大倍数
                actiual_scale_ratio=self.get_actual_scale_ratio(2)
                options=[self.srmd_ncnn_exe,
                           '-i', input_path,
                           '-o', output_path,
                           '-n', self.srmd_ncnn_noise_level,
                           '-s', str(actiual_scale_ratio),
                           '-t', self.srmd_ncnn_tile_size,
                           '-m', self.srmd_ncnn_model_path,
                           '-g', self.gpu_id,
                           '-j', self.srmd_ncnn_load_proc_save,
                           '-f', 'png',
                           '-x'
                           ]
            case 'realsr_ncnn':
                # 将指定放大倍数转换成realsr-ncnn-vulkan支持的放大倍数
                actiual_scale_ratio=self.get_actual_scale_ratio(4)
                options=[self.realsr_ncnn_exe,
                           '-i', input_path,
                           '-o', output_path,
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
        ncnn_vulkan_p=subprocess.run(options, capture_output=False)
        # 获取临时文件夹中的图片列表
        tmp_image_ls=file_list(tmp_folder, 'png', walk_mode=False)
        # 缩放
        zoom_factor=self.scale_ratio/actiual_scale_ratio
        if zoom_factor != 1:
            self.pool_run(self.zoom_image_, tmp_image_ls, zoom_factor)
        # 转格式
        if output_extention != 'png':
            tmp_image_ls=self.pool_run(self.convert_image, tmp_image_ls, output_extention, True)
        output_image_ls=[]
        for tmp_image in tmp_image_ls:
            output_image_ls.append(output_folder/tmp_image.name)
            fmove(tmp_image, output_folder)
        shutil.rmtree(tmp_folder)
        return output_image_ls

    def image_upscale_anime4k(self, input_path, output_folder, output_extention) -> list:
        """
        @brief      使用anime4k放大图片

        @param      input_path        输入路径
        @param      output_folder     输出文件夹
        @param      output_extention  输出图片格式

        @return     输出图片路径列表
        """
        input_path=Path(input_path).resolve()
        output_folder=Path(output_folder).resolve()

        tmp_folder=output_folder.parent/(output_folder.name+'_vnc_tmp_image_upscale')
        tmp_folder.mkdir(parents=True, exist_ok=True)
        if input_path.is_dir():
            output_path=tmp_folder
        else:
            output_path=tmp_folder/input_path.with_suffix('.png').name
        # anime4kcpp非整数倍放大会有alpha通道错位的bug
        # actiual_scale_ratio = self.get_actual_scale_ratio(2)
        options=[self.anime4k_exe,
                   '-i', input_path,
                   # '-z', str(actiual_scale_ratio),
                   '-z', str(self.scale_ratio),
                   '-t', str(self.cpu_cores),
                   '-b',
                   '-q',
                   '-d', self.gpu_id,
                   '-w',
                   '-A',
                   '-o', output_path
                   ]
        if self.anime4k_acnet == '0':
            options.remove('-w')
        anime4k_p=subprocess.run(options, capture_output=False)
        # 获取临时文件夹中的图片列表
        tmp_image_ls=file_list(tmp_folder)
        # 缩放
        # zoom_factor = self.scale_ratio/actiual_scale_ratio
        # if zoom_factor != 1:
        #     self.pool_run(self.zoom_image_, tmp_image_ls, zoom_factor)
        # 转格式
        tmp_image_ls=self.pool_run(self.convert_image, tmp_image_ls, output_extention, True)
        output_image_ls=[]
        for tmp_image in tmp_image_ls:
            target_image=output_folder/tmp_image.relative_to(tmp_folder)
            output_image_ls.append(target_image)
            fmove(tmp_image, target_image.parent)
        shutil.rmtree(tmp_folder)
        return output_image_ls
