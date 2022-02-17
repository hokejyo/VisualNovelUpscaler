# -*- coding: utf-8 -*-

from .functions import *


class Config(object):
    """配置设置"""

    def __init__(self):
        self.bundle_dir = Path(sys.argv[0]).resolve().parent
        self.vnc_config = configparser.ConfigParser()
        self.vnc_config_file = self.bundle_dir/'config.ini'
        self.vnc_log_file = self.bundle_dir/'log.txt'
        self.vnc_lic_file = self.bundle_dir/'LICENSE'

    def reset_config(self):
        # 初始化
        self.vnc_config = configparser.ConfigParser()
        with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
            self.vnc_config.add_section('General')
            self.vnc_config.set('General', 'cpu_cores', str(cpu_count()))
            self.vnc_config.set('General', 'gpu_id', '0')
            self.vnc_config.set('General', 'encoding_list', 'shift-jis,utf-8,gbk,utf-16,cp932')
            self.vnc_config.set('General', 'image_sr_engine', 'waifu2x_ncnn')
            self.vnc_config.set('General', 'video_sr_engine', 'anime4k')
            self.vnc_config.set('General', 'tta', '0')
            # waifu2x-ncnn-vulkan相关配置
            self.vnc_config.add_section('waifu2x_ncnn')
            self.vnc_config.set('waifu2x_ncnn', 'noise_level', '3')
            self.vnc_config.set('waifu2x_ncnn', 'tile_size', '0')
            self.vnc_config.set('waifu2x_ncnn', 'model_name', 'models-cunet')
            self.vnc_config.set('waifu2x_ncnn', 'load_proc_save', '1:2:2')
            # Real-CUGAN相关配置
            self.vnc_config.add_section('real_cugan')
            self.vnc_config.set('real_cugan', 'noise_level', '3')
            self.vnc_config.set('real_cugan', 'tile_size', '200')
            self.vnc_config.set('real_cugan', 'sync_gap_mode', '2')
            self.vnc_config.set('real_cugan', 'model_name', 'models-se')
            self.vnc_config.set('real_cugan', 'load_proc_save', '1:2:2')
            # Real-ESRGAN相关配置
            self.vnc_config.add_section('real_esrgan')
            self.vnc_config.set('real_esrgan', 'tile_size', '0')
            self.vnc_config.set('real_esrgan', 'model_name', 'realesrgan-x4plus-anime')
            self.vnc_config.set('real_esrgan', 'load_proc_save', '1:2:2')
            # srmd-ncnn-vulkan相关配置
            self.vnc_config.add_section('srmd_ncnn')
            self.vnc_config.set('srmd_ncnn', 'noise_level', '3')
            self.vnc_config.set('srmd_ncnn', 'tile_size', '0')
            self.vnc_config.set('srmd_ncnn', 'load_proc_save', '1:2:2')
            # realsr-ncnn-vulkan相关配置
            self.vnc_config.add_section('realsr_ncnn')
            self.vnc_config.set('realsr_ncnn', 'tile_size', '0')
            self.vnc_config.set('realsr_ncnn', 'model_name', 'models-DF2K_JPEG')
            self.vnc_config.set('realsr_ncnn', 'load_proc_save', '1:2:2')
            # anime4kcpp相关配置
            self.vnc_config.add_section('anime4k')
            self.vnc_config.set('anime4k', 'acnet', '1')
            # 视频设置
            self.vnc_config.add_section('ffmpeg')
            self.vnc_config.set('ffmpeg', 'video_quality', '2')
            self.vnc_config.write(vcf)
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
        # 通用参数
        self.vnc_config.read(self.vnc_config_file)
        self.cpu_cores = self.vnc_config.getint('General', 'cpu_cores')
        self.gpu_id = self.vnc_config.get('General', 'gpu_id')
        self.encoding_list = [encoding.strip() for encoding in self.vnc_config.get('General', 'encoding_list').split(',')]
        self.image_sr_engine = self.vnc_config.get('General', 'image_sr_engine')
        self.video_sr_engine = self.vnc_config.get('General', 'video_sr_engine')
        self.tta = self.vnc_config.get('General', 'tta')
        # waifu2x-ncnn-vulkan相关配置
        # https://github.com/nihui/waifu2x-ncnn-vulkan
        self.waifu2x_ncnn_exe = self.toolkit_path/'waifu2x-ncnn-vulkan'/'waifu2x-ncnn-vulkan.exe'
        self.waifu2x_ncnn_noise_level = self.vnc_config.get('waifu2x_ncnn', 'noise_level')
        self.waifu2x_ncnn_tile_size = self.vnc_config.get('waifu2x_ncnn', 'tile_size')
        self.waifu2x_ncnn_model_name = self.vnc_config.get('waifu2x_ncnn', 'model_name')
        self.waifu2x_ncnn_model_path = self.waifu2x_ncnn_exe.parent/self.waifu2x_ncnn_model_name
        self.waifu2x_ncnn_load_proc_save = self.vnc_config.get('waifu2x_ncnn', 'load_proc_save')
        # Real-CUGAN相关配置
        # https://github.com/nihui/realcugan-ncnn-vulkan
        self.real_cugan_exe = self.toolkit_path/'realcugan-ncnn-vulkan'/'realcugan-ncnn-vulkan.exe'
        self.real_cugan_noise_level = self.vnc_config.get('real_cugan', 'noise_level')
        self.real_cugan_tile_size = self.vnc_config.get('real_cugan', 'tile_size')
        self.real_cugan_sync_gap_mode = self.vnc_config.get('real_cugan', 'sync_gap_mode')
        # self.real_cugan_model_path = self.vnc_config.get('real_cugan', 'model_name')
        self.real_cugan_model_name = self.vnc_config.get('real_cugan', 'model_name')
        self.real_cugan_model_path = self.real_cugan_exe.parent/self.real_cugan_model_name
        self.real_cugan_load_proc_save = self.vnc_config.get('real_cugan', 'load_proc_save')
        # Real-ESRGAN相关配置
        # https://github.com/xinntao/Real-ESRGAN
        self.real_esrgan_exe = self.toolkit_path/'realesrgan-ncnn-vulkan'/'realesrgan-ncnn-vulkan.exe'
        self.real_esrgan_model_path = self.real_esrgan_exe.parent/'models'
        self.real_esrgan_tile_size = self.vnc_config.get('real_esrgan', 'tile_size')
        self.real_esrgan_model_name = self.vnc_config.get('real_esrgan', 'model_name')
        self.real_esrgan_load_proc_save = self.vnc_config.get('real_esrgan', 'load_proc_save')
        # srmd-ncnn-vulkan相关配置
        # https://github.com/nihui/srmd-ncnn-vulkan
        self.srmd_ncnn_exe = self.toolkit_path/'srmd-ncnn-vulkan'/'srmd-ncnn-vulkan.exe'
        self.srmd_ncnn_model_path = self.srmd_ncnn_exe.parent/'models-srmd'
        self.srmd_ncnn_noise_level = self.vnc_config.get('srmd_ncnn', 'noise_level')
        self.srmd_ncnn_tile_size = self.vnc_config.get('srmd_ncnn', 'tile_size')
        self.srmd_ncnn_load_proc_save = self.vnc_config.get('srmd_ncnn', 'load_proc_save')
        # realsr-ncnn-vulkan相关配置
        # https://github.com/nihui/realsr-ncnn-vulkan
        self.realsr_ncnn_exe = self.toolkit_path/'realsr-ncnn-vulkan'/'realsr-ncnn-vulkan.exe'
        self.realsr_ncnn_tile_size = self.vnc_config.get('realsr_ncnn', 'tile_size')
        self.realsr_ncnn_model_name = self.vnc_config.get('realsr_ncnn', 'model_name')
        self.realsr_ncnn_model_path = self.realsr_ncnn_exe.parent/self.realsr_ncnn_model_name
        self.realsr_ncnn_load_proc_save = self.vnc_config.get('realsr_ncnn', 'load_proc_save')
        # anime4k相关配置
        # https://github.com/TianZerL/Anime4KCPP
        self.anime4k_exe = self.toolkit_path/'Anime4KCPP_CLI'/'Anime4KCPP_CLI.exe'
        self.anime4k_acnet = self.vnc_config.get('anime4k', 'acnet')
        # 视频设置
        self.video_quality = self.vnc_config.get('ffmpeg', 'video_quality')
