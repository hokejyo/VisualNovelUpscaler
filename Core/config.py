# -*- coding: utf-8 -*-

from .functions import *


class Config(object):
    """配置设置"""

    def __init__(self):
        self.bundle_dir = Path(sys.argv[0]).parent
        self.vnu_config = configparser.ConfigParser()
        self.vnu_config_file = self.bundle_dir/'config.ini'
        self.vnu_log_file = self.bundle_dir/'log.txt'
        self.vnu_lic_file = self.bundle_dir/'LICENSE'

    def reset_config(self):
        # 初始化
        self.vnu_config = configparser.ConfigParser()
        with open(self.vnu_config_file, 'w', newline='', encoding='utf-8') as vcf:
            self.vnu_config.add_section('General')
            self.vnu_config.set('General', 'cpu_cores', str(int(cpu_count()/2)))
            self.vnu_config.set('General', 'gpu_id', '0')
            self.vnu_config.set('General', 'encoding_list', 'Shift_JIS,UTF-8,GBK,UTF-16')
            # 图片设置
            self.vnu_config.add_section('Image')
            self.vnu_config.set('Image', 'image_sr_engine', 'waifu2x_ncnn')
            self.vnu_config.set('Image', 'image_batch_size', '20')
            # 视频设置
            self.vnu_config.add_section('Video')
            self.vnu_config.set('Video', 'video_sr_engine', 'anime4k')
            self.vnu_config.set('Video', 'video_batch_size', '40')
            self.vnu_config.set('Video', 'video_quality', '8')
            # 超分引擎设置
            self.vnu_config.add_section('SREngine')
            self.vnu_config.set('SREngine', 'tta', '0')
            # waifu2x-ncnn-vulkan相关配置
            self.vnu_config.add_section('waifu2x_ncnn')
            self.vnu_config.set('waifu2x_ncnn', 'noise_level', '3')
            self.vnu_config.set('waifu2x_ncnn', 'tile_size', '0')
            self.vnu_config.set('waifu2x_ncnn', 'model_name', 'models-cunet')
            self.vnu_config.set('waifu2x_ncnn', 'load_proc_save', '1:2:2')
            # Real-CUGAN相关配置
            self.vnu_config.add_section('real_cugan')
            self.vnu_config.set('real_cugan', 'noise_level', '3')
            self.vnu_config.set('real_cugan', 'tile_size', '0')
            self.vnu_config.set('real_cugan', 'sync_gap_mode', '3')
            self.vnu_config.set('real_cugan', 'model_name', 'models-se')
            self.vnu_config.set('real_cugan', 'load_proc_save', '1:2:2')
            # Real-ESRGAN相关配置
            self.vnu_config.add_section('real_esrgan')
            self.vnu_config.set('real_esrgan', 'tile_size', '0')
            self.vnu_config.set('real_esrgan', 'model_name', 'realesrgan-x4plus-anime')
            self.vnu_config.set('real_esrgan', 'load_proc_save', '1:2:2')
            # srmd-ncnn-vulkan相关配置
            self.vnu_config.add_section('srmd_ncnn')
            self.vnu_config.set('srmd_ncnn', 'noise_level', '3')
            self.vnu_config.set('srmd_ncnn', 'tile_size', '0')
            self.vnu_config.set('srmd_ncnn', 'load_proc_save', '1:2:2')
            # realsr-ncnn-vulkan相关配置
            self.vnu_config.add_section('realsr_ncnn')
            self.vnu_config.set('realsr_ncnn', 'tile_size', '0')
            self.vnu_config.set('realsr_ncnn', 'model_name', 'models-DF2K_JPEG')
            self.vnu_config.set('realsr_ncnn', 'load_proc_save', '1:2:2')
            # anime4kcpp相关配置
            self.vnu_config.add_section('anime4k')
            self.vnu_config.set('anime4k', 'acnet', '1')
            self.vnu_config.set('anime4k', 'hdn_mode', '1')
            self.vnu_config.set('anime4k', 'hdn_level', '1')
            self.vnu_config.write(vcf)
        self.load_config()

    def load_config(self):
        # 依赖工具集文件路径
        self.toolkit_path = self.bundle_dir/'Dependencies'
        # https://github.com/FFmpeg/FFmpeg
        self.ffmpeg = self.toolkit_path/'ffmpeg'/'bin'/'ffmpeg.exe'
        self.ffprobe = self.toolkit_path/'ffmpeg'/'bin'/'ffprobe.exe'
        # https://github.com/UlyssesWu/FreeMote
        self.psb_de_exe = self.toolkit_path/'FreeMoteToolkit'/'PsbDecompile.exe'
        self.psb_en_exe = self.toolkit_path/'FreeMoteToolkit'/'PsBuild.exe'
        # https://github.com/vn-toolkit/tlg2png
        self.tlg2png_exe = self.toolkit_path/'tlg2png'/'tlg2png.exe'
        # https://github.com/krkrz/krkr2
        self.krkrtpc_exe = self.toolkit_path/'krkrtpc'/'krkrtpc.exe'
        # https://github.com/zhiyb/png2tlg
        self.png2tlg6_exe = self.toolkit_path/'png2tlg6'/'png2tlg6.exe'
        # https://github.com/xmoeproject/AlphaMovieDecoder
        self.amv_de_exe = self.toolkit_path/'AlphaMovieDecoder'/'AlphaMovieDecoderFake.exe'
        self.amv_de_folder = self.toolkit_path/'AlphaMovieDecoder'/'video'
        # https://github.com/zhiyb/AlphaMovieEncoder
        self.amv_en_exe = self.toolkit_path/'AlphaMovieEncoder'/'amenc.exe'
        # https://github.com/AtomCrafty/MajiroTools
        self.mjotool_exe = self.toolkit_path/'MajiroTools'/'maji.exe'
        # 通用参数
        self.vnu_config.read(self.vnu_config_file)
        self.cpu_cores = self.vnu_config.getint('General', 'cpu_cores')
        self.gpu_id = self.vnu_config.get('General', 'gpu_id')
        self.encoding_list = [encoding.strip() for encoding in self.vnu_config.get('General', 'encoding_list').split(',')]
        # 图片设置
        self.image_sr_engine = self.vnu_config.get('Image', 'image_sr_engine')
        self.image_batch_size = self.vnu_config.getint('Image', 'image_batch_size')
        # 视频设置
        self.video_quality = self.vnu_config.get('Video', 'video_quality')
        self.video_batch_size = self.vnu_config.getint('Video', 'video_batch_size')
        self.video_sr_engine = self.vnu_config.get('Video', 'video_sr_engine')
        # 超分引擎设置
        self.tta = self.vnu_config.get('SREngine', 'tta')
        # waifu2x-ncnn-vulkan相关配置
        # https://github.com/nihui/waifu2x-ncnn-vulkan
        self.waifu2x_ncnn_exe = self.toolkit_path/'waifu2x-ncnn-vulkan'/'waifu2x-ncnn-vulkan.exe'
        self.waifu2x_ncnn_noise_level = self.vnu_config.get('waifu2x_ncnn', 'noise_level')
        self.waifu2x_ncnn_tile_size = self.vnu_config.get('waifu2x_ncnn', 'tile_size')
        self.waifu2x_ncnn_model_name = self.vnu_config.get('waifu2x_ncnn', 'model_name')
        self.waifu2x_ncnn_model_path = self.waifu2x_ncnn_exe.parent/self.waifu2x_ncnn_model_name
        self.waifu2x_ncnn_load_proc_save = self.vnu_config.get('waifu2x_ncnn', 'load_proc_save')
        # Real-CUGAN相关配置
        # https://github.com/nihui/realcugan-ncnn-vulkan
        self.real_cugan_exe = self.toolkit_path/'realcugan-ncnn-vulkan'/'realcugan-ncnn-vulkan.exe'
        self.real_cugan_noise_level = self.vnu_config.get('real_cugan', 'noise_level')
        self.real_cugan_tile_size = self.vnu_config.get('real_cugan', 'tile_size')
        self.real_cugan_sync_gap_mode = self.vnu_config.get('real_cugan', 'sync_gap_mode')
        # self.real_cugan_model_path = self.vnu_config.get('real_cugan', 'model_name')
        self.real_cugan_model_name = self.vnu_config.get('real_cugan', 'model_name')
        self.real_cugan_model_path = self.real_cugan_exe.parent/self.real_cugan_model_name
        self.real_cugan_load_proc_save = self.vnu_config.get('real_cugan', 'load_proc_save')
        # Real-ESRGAN相关配置
        # https://github.com/xinntao/Real-ESRGAN
        self.real_esrgan_exe = self.toolkit_path/'realesrgan-ncnn-vulkan'/'realesrgan-ncnn-vulkan.exe'
        self.real_esrgan_model_path = self.real_esrgan_exe.parent/'models'
        self.real_esrgan_tile_size = self.vnu_config.get('real_esrgan', 'tile_size')
        self.real_esrgan_model_name = self.vnu_config.get('real_esrgan', 'model_name')
        self.real_esrgan_load_proc_save = self.vnu_config.get('real_esrgan', 'load_proc_save')
        # srmd-ncnn-vulkan相关配置
        # https://github.com/nihui/srmd-ncnn-vulkan
        self.srmd_ncnn_exe = self.toolkit_path/'srmd-ncnn-vulkan'/'srmd-ncnn-vulkan.exe'
        self.srmd_ncnn_model_path = self.srmd_ncnn_exe.parent/'models-srmd'
        self.srmd_ncnn_noise_level = self.vnu_config.get('srmd_ncnn', 'noise_level')
        self.srmd_ncnn_tile_size = self.vnu_config.get('srmd_ncnn', 'tile_size')
        self.srmd_ncnn_load_proc_save = self.vnu_config.get('srmd_ncnn', 'load_proc_save')
        # realsr-ncnn-vulkan相关配置
        # https://github.com/nihui/realsr-ncnn-vulkan
        self.realsr_ncnn_exe = self.toolkit_path/'realsr-ncnn-vulkan'/'realsr-ncnn-vulkan.exe'
        self.realsr_ncnn_tile_size = self.vnu_config.get('realsr_ncnn', 'tile_size')
        self.realsr_ncnn_model_name = self.vnu_config.get('realsr_ncnn', 'model_name')
        self.realsr_ncnn_model_path = self.realsr_ncnn_exe.parent/self.realsr_ncnn_model_name
        self.realsr_ncnn_load_proc_save = self.vnu_config.get('realsr_ncnn', 'load_proc_save')
        # anime4k相关配置
        # https://github.com/TianZerL/Anime4KCPP
        self.anime4k_exe = self.toolkit_path/'Anime4KCPP_CLI'/'Anime4KCPP_CLI.exe'
        self.anime4k_acnet = self.vnu_config.get('anime4k', 'acnet')
        self.anime4k_hdn_mode = self.vnu_config.get('anime4k', 'hdn_mode')
        self.anime4k_hdn_level = self.vnu_config.get('anime4k', 'hdn_level')
