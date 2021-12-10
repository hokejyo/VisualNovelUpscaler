# -*- coding:utf-8 -*-

from Globals import *


class GeneralEngine(object):
    """通用引擎"""

    def __init__(self, game_data):

        self.reload_vnc_config()
        # 默认必要参数
        self.game_data = os.path.abspath(game_data)
        self.tmp_folder = os.path.join(os.path.dirname(self.game_data), 'vnc_tmp')
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

    def image_scale(self, input_path, output_path=None, output_extention='png'):
        '''
        对图片进行放大处理

        注意：使用anime4k放大时，指定输出扩展名无效
        '''
        if not output_path:
            output_path = input_path

        if self.image_scale_mode == 'waifu2x':
            self.waifu2x(input_path, output_path=output_path, output_extention=output_extention)
        elif self.image_scale_mode == 'anime4k':
            self.anime4k(input_path, output_path=output_path)

    def waifu2x(self, input_path, output_path=None, output_extention='png'):
        '''
        使用waifu2x-caffe放大图片(机器学习，伪无损放大)，图片保存为指定格式

        如果不指定输出路径，相同格式覆盖原文件
        '''
        scale_ratio = str(self.scale_ratio)
        waifu2x_p = subprocess.run([self.waifu2x_exe, '-i', input_path, '-e', output_extention, '-m', self.scale_mode, '-s', scale_ratio, '-n', self.noise_level, '-p', self.process_mode, '-y', self.style_mode, '-c', self.crop_size, '-b', self.batch_size, '--gpu', self.gpu_No, '-t', self.tta, '-o', output_path], capture_output=True)
        # with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
        #     vlogf.write('*'*30+'\r\n')
        #     vlogf.write(waifu2x_p.stdout.decode('UTF-8'))

    def anime4k(self, input_path, output_path=None):
        '''
        使用anime4k放大图片(非机器学习)，图片格式不变

        如果不指定输出路径，覆盖原文件
        '''
        scale_ratio = str(self.scale_ratio)
        # cpu_cores = str(self.cpu_cores)
        # anime4k_p = subprocess.run([self.anime4k_exe, '-i', input_path, '-z', scale_ratio, '-o', output_path], capture_output=False)
        # anime4k_p = subprocess.run([self.anime4k_exe, '-i', input_path, '-z', scale_ratio, '-d', self.gpu_No, '-t', cpu_cores, '-o', output_path, '-q', '-w', '-A'], capture_output=False)
        anime4k_p = subprocess.run([self.anime4k_exe, '-i', input_path, '-z', scale_ratio, '-d', self.gpu_No, '-q', '-A', '-o', output_path], capture_output=False)
        with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
            vlogf.write('*'*30+'\r\n')
            vlogf.write(anime4k_p.stdout.decode('UTF-8'))

    def video_scale(self, input_video, output_extension=None, output_vcodec=None) -> str:
        '''
        视频放大、转码、压制，如果不指定扩展名和视频编码，将使用源视频的扩展名和编码
        '''
        if output_extension:
            output_video = input_video.replace('.'+extension_name(input_video), '.'+output_extension)
        else:
            output_video = input_video
        if not output_vcodec:
            output_vcodec = self.get_video_codec(input_video)
        tmp_video = self.anime4k_video_scale(input_video)
        self.video_codec_trans(tmp_video, output_video=output_video, output_vcodec=output_vcodec)
        os.remove(tmp_video)
        return output_video

    def anime4k_video_scale(self, input_video, output_video_name='tmp.mkv') -> str:
        '''
        使用anime4k放大视频(非机器学习)，默认输出tmp.mkv视频文件
        '''
        scale_ratio = str(self.scale_ratio)
        output_video = os.path.join(os.path.dirname(input_video), output_video_name)
        anime4k_video_p = subprocess.run([self.anime4k_exe, '-i', input_video, '-z', scale_ratio, '-d', self.gpu_No, '-v', '-q', '-o', output_video], capture_output=True)
        with open(self.vnc_log_file, 'a+', newline='', encoding='UTF-8') as vlogf:
            vlogf.write('*'*30+'\r\n')
            vlogf.write(anime4k_video_p.stdout.decode('UTF-8'))
        return output_video

    def video_codec_trans(self, input_video, output_video, output_vcodec=None):
        '''
        视频转码、压制
        '''
        special_vcodecs = ['theora']
        if output_vcodec not in special_vcodecs:
            video_quality = self.video_quality
        else:
            # 特殊编码视频的质量设定与常规视频不统一
            video_quality = str(10 - int(self.video_quality))
        format_trans_p = subprocess.run([self.ffmpeg, '-i', input_video, '-c:v', output_vcodec, '-q:v', video_quality, '-y', output_video], capture_output=True)
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
        # 图片处理模式
        self.image_scale_mode = vc.image_scale_mode
        # 并行核数
        self.cpu_cores = vc.cpu_cores
        # 显卡序号
        self.gpu_No = vc.gpu_No
        # waifu2x设置
        self.process_mode = vc.process_mode
        self.crop_size = vc.crop_size
        self.scale_mode = vc.scale_mode
        self.noise_level = vc.noise_level
        self.style_mode = vc.style_mode
        self.batch_size = vc.batch_size
        self.tta = vc.tta
        # ffmpeg设置
        self.video_quality = vc.video_quality
        # 依赖文件
        self.vnc_config_file = vc.vnc_config_file
        self.vnc_log_file = vc.vnc_log_file
        self.vnc_lic_file = vc.vnc_lic_file
        self.ffmpeg = vc.ffmpeg
        self.ffprobe = vc.ffprobe
        self.waifu2x_exe = vc.waifu2x_exe
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
        gpu_No_choice = input('\n请选择显卡序号：\n[0]0\n[1]1\n[2]其它\n显卡序号可以在任务管理器查看，如果指定的显卡不存在，则会使用默认显卡进行处理\n请选择显卡序号(默认0)：')
        if gpu_No_choice == '0':
            gpu_No = '0'
        elif gpu_No_choice == '1':
            gpu_No = '1'
        elif gpu_No_choice == '2':
            gpu_No = input('请输入指定的显卡序号：')
        else:
            gpu_No = '0'
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
            vc.vnc_config.set('General', 'gpu_No', gpu_No)
            vc.vnc_config.set('waifu2x', 'process_mode', process_mode)
            vc.vnc_config.set('waifu2x', 'style_mode', style_mode)
            vc.vnc_config.set('waifu2x', 'crop_size', crop_size)
            vc.vnc_config.write(vcf)
        self.reload_vnc_config()
        input('配置修改完成，按回车返回：')

    def reset_vnc_config(self):
        os.system('cls')
        vc.write_vnc_config(reset_mode=True)
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
