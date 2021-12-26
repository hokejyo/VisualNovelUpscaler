# -*- coding:utf-8 -*-

from Globals import *
from VNCConfig import vc


class GeneralEngine(object):
    """通用引擎"""

    def __init__(self, game_data):

        self.reload_vnc_config()
        # 默认必要参数
        self.game_data = Path(game_data).resolve()
        self.tmp_folder = self.game_data.parent/'vnc_tmp'
        self.encoding, self.scwidth, self.scheight = 'shift-jis', 1280, 720

    def get_default_scale_ratio(self) -> float:
        if self.scwidth/self.scheight == 16/9:
            scale_ratio = float(1080/self.scheight)
        else:
            scale_ratio = float(2)
        return scale_ratio

    def get_hd_resolution(self):
        if self.scwidth/self.scheight == 16/9:
            if self.scheight*self.scale_ratio == 1080:
                hd_resolution = '1080P'
            elif self.scheight*self.scale_ratio == 1440:
                hd_resolution = '2K'
            elif self.scheight*self.scale_ratio == 2160:
                hd_resolution = '4K'
            else:
                hd_resolution = '%d*%d' % (int(self.scwidth*self.scale_ratio), int(self.scheight*self.scale_ratio))
        else:
            hd_resolution = '%d*%d' % (int(self.scwidth*self.scale_ratio), int(self.scheight*self.scale_ratio))
        return hd_resolution

    def change_scale_ratio(self):
        sep_line = '-'*80
        os.system('cls')
        if self.scwidth/self.scheight == 16/9:
            choice = input(f'{sep_line}\n请选择高清重制后的分辨率：\n{sep_line}\n[1]1080P\n[2]2K\n[3]4K\n[4]自定义\n{sep_line}\n请选择(默认1080P)：')
            if choice == '1':
                scale_ratio = float(1080/self.scheight)
            elif choice == '2':
                scale_ratio = float(1440/self.scheight)
            elif choice == '3':
                scale_ratio = float(2160/self.scheight)
            elif choice == '4':
                scale_ratio = float(input('\n请手动输入放大倍数：'))
            else:
                scale_ratio = float(1080/self.scheight)
        else:
            scale_ratio = float(input('游戏原生分辨率非16:9，请手动输入放大倍数：'))
        self.scale_ratio = scale_ratio

    def get_lines_encoding(self, text_file):
        '''
        返回文本内容和编码
        '''
        try:
            with open(text_file, newline='', encoding=self.encoding) as f:
                lines = f.readlines()
                current_encoding = self.encoding
        except UnicodeDecodeError:
            current_encoding = get_encoding(text_file)
            with open(text_file, newline='', encoding=current_encoding) as f:
                lines = f.readlines()
        return lines, current_encoding

    def image_scale(self, input_path, extention):
        """
        @brief      对文件夹内的图片文件进行放大，文件夹内的图片格式需相同

        @param      input_path  输入文件夹路径
        @param      extention   文件夹中的图片格式
        """
        input_path = Path(input_path)
        folders = input_path.rglob('**/')
        for folder in folders:
            match self.super_resolution_engine:
                case 'waifu2x_ncnn':
                    scaled_image_file = self.waifu2x_ncnn(folder, extention)
                case 'real_esrgan':
                    scaled_image_file = self.real_esrgan(folder, extention)
                case _:
                    print('请选择正确的超分辨率引擎')

    def waifu2x_ncnn(self, input_folder, extention):
        """
        @brief      使用waifu2x-ncnn-valkan放大单个文件夹中的图片，文件夹内图片格式需保持一致，目前的最佳选择，失真较小

        @param      input_folder  输入文件夹
        @param      extention     图片格式
        """
        input_folder = Path(input_folder)
        # 记录原文件名/放大后的临时文件名
        ori_image_ls = file_list(input_folder, extention, walk_mode=False)
        tmp_image_ls = [ori_image.with_suffix('.png') for ori_image in ori_image_ls]
        # 将指定放大倍数转换成waifu2x-ncnn-valkan支持的放大倍数
        actiual_scale_ratio = 2**ceil(log2(self.scale_ratio))
        # 放大，全部输出为png格式
        options = [self.waifu2x_ncnn_exe,
                   '-i', input_folder,
                   '-o', input_folder,
                   '-n', self.waifu2x_ncnn_noise_level,
                   '-s', str(actiual_scale_ratio),
                   '-t', self.waifu2x_ncnn_tile_size,
                   '-m', self.waifu2x_ncnn_model_path,
                   '-g', self.gpu_id,
                   '-j', self.waifu2x_ncnn_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.waifu2x_ncnn_tta == '0':
            options.remove('-x')
        waifu2x_ncnn_p = subprocess.run(options, capture_output=True)
        # 转格式
        if extention != 'png':
            self.vn_image_convert(tmp_image_ls, extention, del_input=True)
        # 缩放
        zoom_factor = self.scale_ratio/actiual_scale_ratio
        if zoom_factor != 1:
            self.vn_image_zoom(ori_image_ls, zoom_factor)

    # def waifu2x_ncnn(self, input_folder, extention) -> Path:
    #     """
    #     @brief      使用waifu2x-ncnn-valkan放大单个文件夹中的图片，文件夹内图片格式需保持一致，目前的最佳选择，失真较小

    #     @param      input_folder  输入文件夹
    #     @param      extention     图片格式

    #     @return     输出图片路径
    #     """
    #     input_folder = Path(input_folder)
    #     # 记录原文件名/放大后的临时文件名
    #     ori_image_ls = file_list(input_folder, extention, walk_mode=False)
    #     tmp_image_ls = [ori_image.with_suffix('.png') for ori_image in ori_image_ls]
    #     # 放大，全部输出为png格式
    #     options = [self.waifu2x_ncnn_exe,
    #                '-i', input_folder,
    #                '-o', input_folder,
    #                '-n', self.waifu2x_ncnn_noise_level,
    #                '-s', '2',
    #                '-t', self.waifu2x_ncnn_tile_size,
    #                '-m', self.waifu2x_ncnn_model_path,
    #                '-g', self.gpu_id,
    #                '-j', self.waifu2x_ncnn_load_proc_save,
    #                '-f', 'png',
    #                '-x'
    #                ]
    #     if self.waifu2x_ncnn_tta == '0':
    #         options.remove('-x')
    #     current_scale_ratio = 1
    #     while current_scale_ratio < self.scale_ratio:
    #         waifu2x_ncnn_p = subprocess.run(options, capture_output=True)
    #         if (extention != 'png') and (current_scale_ratio == 1):
    #             [ori_image.unlink() for ori_image in ori_image_ls]
    #         current_scale_ratio *= 2
    #     # 缩放
    #     zoom_factor = self.scale_ratio/current_scale_ratio
    #     if zoom_factor != 1:
    #         self.vn_image_zoom(tmp_image_ls, zoom_factor)
    #     # 转格式
    #     if extention != 'png':
    #         self.vn_image_convert(tmp_image_ls, extention)

    def real_esrgan(self, input_folder, extention):
        """
        @brief      使用Real-ESRGAN放大单个文件夹中的图片，文件夹内图片格式需保持一致，画面更锐利

        @param      input_folder  输入文件夹
        @param      extention     图片格式
        """
        input_folder = Path(input_folder)
        # 记录原文件名/放大后的临时文件名
        ori_image_ls = file_list(input_folder, extention, walk_mode=False)
        tmp_image_ls = [ori_image.with_suffix('.png') for ori_image in ori_image_ls]
        # 放大，全部输出为png格式
        options = [self.real_esrgan_exe,
                   '-i', input_folder,
                   '-o', input_folder,
                   # 放大倍率为4时才能正常放大
                   '-s', '4',
                   '-t', self.real_esrgan_tile_size,
                   '-m', self.real_esrgan_model_path,
                   '-n', self.real_esrgan_model_name,
                   '-g', self.gpu_id,
                   '-j', self.real_esrgan_load_proc_save,
                   '-f', 'png',
                   '-x'
                   ]
        if self.real_esrgan_tta == '0':
            options.remove('-x')
        current_scale_ratio = 1
        while current_scale_ratio < self.scale_ratio:
            realesrgan_p = subprocess.run(options, capture_output=True)
            if (extention != 'png') and (current_scale_ratio == 1):
                [ori_image.unlink() for ori_image in ori_image_ls]
            current_scale_ratio *= 4
        # 转格式
        if extention != 'png':
            self.vn_image_convert(tmp_image_ls, extention, del_input=True)
        # 缩放
        zoom_factor = self.scale_ratio/current_scale_ratio
        if zoom_factor != 1:
            self.vn_image_zoom(ori_image_ls, zoom_factor)

    def vn_image_zoom(self, image_file_ls, zoom_factor):
        vn_image_zoom_pool = Pool(self.cpu_cores)
        for image_file in image_file_ls:
            vn_image_zoom_pool.apply_async(image_zoom, args=(image_file, zoom_factor))
        vn_image_zoom_pool.close()
        vn_image_zoom_pool.join()

    def vn_image_convert(self, image_file_ls, extention, del_input=True):
        vn_image_convert_pool = Pool(self.cpu_cores)
        for image_file in image_file_ls:
            vn_image_convert_pool.apply_async(image_convert, args=(image_file, extention, del_input))
        vn_image_convert_pool.close()
        vn_image_convert_pool.join()

    def video_scale(self, input_video, output_extension=None, output_vcodec=None) -> str:
        '''
        视频放大、转码、压制，如果不指定扩展名和视频编码，将使用源视频的扩展名和编码
        '''
        input_video = Path(input_video)
        if output_extension:
            output_video = input_video.with_suffix('.'+output_extension)
        else:
            output_video = input_video
        if not output_vcodec:
            output_vcodec = self.get_video_codec(input_video)
        tmp_video = self.anime4k_video_scale(input_video)
        self.video_codec_trans(tmp_video, output_video=output_video, output_vcodec=output_vcodec)
        tmp_video.unlink()
        return output_video

    def anime4k_video_scale(self, input_video, output_video_name='tmp.mkv') -> str:
        '''
        使用anime4k放大视频(非机器学习)，默认输出tmp.mkv视频文件
        '''
        output_video = Path(input_video).parent/output_video_name
        options = [self.anime4k_exe,
                   '-i', input_video,
                   '-z', str(self.scale_ratio),
                   '-d', self.gpu_id,
                   '-v',
                   '-q',
                   '-o', output_video
                   ]
        anime4k_video_p = subprocess.run(options, capture_output=True)
        with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
            vlogf.write('*'*30+'\r\n')
            vlogf.write(anime4k_video_p.stdout.decode('UTF-8'))
        return output_video

    def video_codec_trans(self, input_video, output_video, output_vcodec):
        '''
        视频转码、压制
        '''
        special_vcodecs = ['theora']
        if output_vcodec not in special_vcodecs:
            video_quality = self.video_quality
        else:
            # 特殊编码视频的质量设定与常规视频不统一
            video_quality = str(10 - int(self.video_quality))
        options = [self.ffmpeg,
                   '-i', input_video,
                   '-c:v', output_vcodec,
                   '-q:v', video_quality,
                   '-y',
                   output_video
                   ]
        format_trans_p = subprocess.run(options, capture_output=True)
        with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
            vlogf.write('*'*30+'\r\n')
            vlogf.write(format_trans_p.stdout.decode('UTF-8'))

    def get_video_codec(self, video_file) -> str:
        '''
        获取视频编码格式
        '''
        get_codec_p = subprocess.run([self.ffprobe, video_file], capture_output=True)
        with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
            vlogf.write('*'*30+'\r\n')
            vlogf.write(get_codec_p.stdout.decode('UTF-8'))
        pattern = re.compile(r'Stream.*\WVideo\W+([a-zA-Z0-9]+)\W')
        codec_type_c = re.search(pattern, str(get_codec_p))
        if codec_type_c:
            codec_type = codec_type_c.group(1)
        else:
            codec_type = None
        return codec_type

    def reload_vnc_config(self):
        vc.read_vnc_config()
        # # 工作目录
        self.bundle_dir = vc.bundle_dir
        # 超分辨率引擎
        self.super_resolution_engine = vc.super_resolution_engine
        # 并行核数
        self.cpu_cores = vc.cpu_cores
        # 显卡序号
        self.gpu_id = vc.gpu_id
        # waifu2x-ncnn-vulkan设置
        self.waifu2x_ncnn_exe = vc.waifu2x_ncnn_exe
        self.waifu2x_ncnn_noise_level = vc.waifu2x_ncnn_noise_level
        self.waifu2x_ncnn_tile_size = vc.waifu2x_ncnn_tile_size
        self.waifu2x_ncnn_model_path = vc.waifu2x_ncnn_model_path
        self.waifu2x_ncnn_load_proc_save = vc.waifu2x_ncnn_load_proc_save
        self.waifu2x_ncnn_tta = vc.waifu2x_ncnn_tta
        # Real-ESRGAN设置
        self.real_esrgan_exe = vc.real_esrgan_exe
        self.real_esrgan_model_path = vc.real_esrgan_model_path
        self.real_esrgan_tile_size = vc.real_esrgan_tile_size
        self.real_esrgan_model_name = vc.real_esrgan_model_name
        self.real_esrgan_load_proc_save = vc.real_esrgan_load_proc_save
        self.real_esrgan_tta = vc.real_esrgan_tta
        # ffmpeg设置
        self.video_quality = vc.video_quality
        # 依赖文件
        self.vnc_config_file = vc.vnc_config_file
        self.vnc_log_file = vc.vnc_log_file
        self.vnc_lic_file = vc.vnc_lic_file
        self.ffmpeg = vc.ffmpeg
        self.ffprobe = vc.ffprobe
        self.anime4k_exe = vc.anime4k_exe
        self.psb_de_exe = vc.psb_de_exe
        self.psb_en_exe = vc.psb_en_exe
        self.tlg2png_exe = vc.tlg2png_exe
        self.png2tlg6_exe = vc.png2tlg6_exe
        self.krkrtpc_exe = vc.krkrtpc_exe
        self.amv_de_exe = vc.amv_de_exe
        self.amv_de_folder = vc.amv_de_folder
        self.amv_en_exe = vc.amv_en_exe

    def change_vnc_config(self):
        '''
        配置文件修改
        '''
        os.system('cls')
        cpu_cores = input('\n请输入使用的CPU核数：')
        gpu_id_choice = input('\n请选择显卡序号：\n[0]0\n[1]1\n[2]其它\n显卡序号可以在任务管理器查看，如果指定的显卡不存在，则会使用默认显卡进行处理\n请选择显卡序号(默认0)：')
        if gpu_id_choice == '0':
            gpu_id = '0'
        elif gpu_id_choice == '1':
            gpu_id = '1'
        elif gpu_id_choice == '2':
            gpu_id = input('请输入指定的显卡序号：')
        else:
            gpu_id = '0'
        process_mode_choice = input('\n请选择图片处理模式：\n[1]cdunn\n[2]gpu\n[3]cpu\n图片处理速度：cudnn>gpu>>cpu。建议10系以上的N卡，记得装好驱动\n请选择(默认cudnn)：')
        if process_mode_choice == '1':
            process_mode = 'cudnn'
        elif process_mode_choice == '2':
            process_mode = 'gpu'
        elif process_mode_choice == '3':
            process_mode = 'cpu'
        else:
            process_mode = 'cudnn'
        style_mode_choice = input('\n请选择图片处理模型：\n[1]UpRGB\n[2]UpResNet10\n[3]CUnet\nCUnet模型显存占用较高，但风格最适合Galgame\n请选择(默认CUnet)：')
        if style_mode_choice == '1':
            style_mode = 'upconv_7_anime_style_art_rgb'
        elif process_mode_choice == '2':
            style_mode = 'upresnet10'
        elif process_mode_choice == '3':
            style_mode = 'cunet'
        else:
            style_mode = 'cunet'
        crop_size_choice = input('\n请选择图片拆分尺寸：\n[1]64\n[2]128\n[3]256\n拆分尺寸越大，处理速度越快，但若显存不足会崩溃\n请选择(默认128)：')
        if crop_size_choice == '1':
            crop_size = '64'
        elif crop_size_choice == '2':
            crop_size = '128'
        elif crop_size_choice == '3':
            crop_size = '256'
        else:
            crop_size = '128'
        # 写入配置文件
        with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
            vc.vnc_config.set('General', 'cpu_cores', cpu_cores)
            vc.vnc_config.set('General', 'gpu_id', gpu_id)
            vc.vnc_config.set('waifu2x', 'process_mode', process_mode)
            vc.vnc_config.set('waifu2x', 'style_mode', style_mode)
            vc.vnc_config.set('waifu2x', 'crop_size', crop_size)
            vc.vnc_config.write(vcf)
        self.reload_vnc_config()
        input('配置修改完成，按回车返回：')

    def reset_vnc_config(self):
        os.system('cls')
        vc.reset_vnc_config()
        self.reload_vnc_config()
        input('配置重制完成，按回车返回：')

    def print_vnc_config(self):
        os.system('cls')
        with open(self.vnc_config_file, newline='', encoding='utf-8') as vcf:
            print(vcf.read())
        input('按回车返回：')

    def print_license(self):
        os.system('cls')
        print('-'*80)
        with open(self.vnc_lic_file, newline='', encoding='utf-8') as vlicf:
            print(vlicf.read())
        print('-'*80)
        input('按回车返回：')
