# -*- coding: utf-8 -*-

from Globals import *


class Config(object):
    """配置设置"""

    def __init__(self):
        self.bundle_dir = Path(sys.argv[0]).resolve().parent
        self.vnc_config = configparser.ConfigParser()
        self.vnc_config_file = self.bundle_dir/'config.ini'
        self.vnc_log_file = self.bundle_dir/'log_records.txt'
        self.vnc_lic_file = self.bundle_dir/'LICENSE'
        try:
            self.load_config()
        except:
            print('设置文件未正确配置或不存在，将重置设置')
            self.reset_config()
            self.load_config()

    def reset_config(self):
        self.vnc_config = configparser.ConfigParser()
        with open(self.vnc_config_file, 'w', newline='', encoding='utf-8') as vcf:
            self.vnc_config.add_section('General')
            self.vnc_config.set('General', 'super_resolution_engine', 'waifu2x_ncnn')
            self.vnc_config.set('General', 'cpu_cores', str(cpu_count()))
            self.vnc_config.set('General', 'gpu_id', '0')
            # waifu2x-ncnn-vulkan相关配置
            self.vnc_config.add_section('waifu2x_ncnn')
            self.vnc_config.set('waifu2x_ncnn', 'noise_level', '3')
            self.vnc_config.set('waifu2x_ncnn', 'tile_size', '0')
            self.vnc_config.set('waifu2x_ncnn', 'model_name', 'models-cunet')
            self.vnc_config.set('waifu2x_ncnn', 'load_proc_save', '1:2:2')
            self.vnc_config.set('waifu2x_ncnn', 'tta', '0')
            # Real-ESRGAN相关配置
            self.vnc_config.add_section('real_esrgan')
            self.vnc_config.set('real_esrgan', 'tile_size', '0')
            self.vnc_config.set('real_esrgan', 'model_name', 'realesrgan-x4plus-anime')
            self.vnc_config.set('real_esrgan', 'load_proc_save', '1:2:2')
            self.vnc_config.set('real_esrgan', 'tta', '0')
            # ffmpeg相关配置
            self.vnc_config.add_section('ffmpeg')
            self.vnc_config.set('ffmpeg', 'video_quality', '2')
            self.vnc_config.write(vcf)

    def load_config(self):
        # 依赖工具集文件路径
        self.toolkit_path = self.bundle_dir/'Dependencies'
        # https://github.com/FFmpeg/FFmpeg
        self.ffmpeg = self.toolkit_path/'ffmpeg'/'bin'/'ffmpeg.exe'
        self.ffprobe = self.toolkit_path/'ffmpeg'/'bin'/'ffprobe.exe'
        # https://github.com/nihui/waifu2x-ncnn-vulkan
        self.waifu2x_ncnn_exe = self.toolkit_path/'waifu2x-ncnn-vulkan'/'waifu2x-ncnn-vulkan.exe'
        # https://github.com/xinntao/Real-ESRGAN
        self.real_esrgan_exe = self.toolkit_path/'Real-ESRGAN'/'realesrgan-ncnn-vulkan.exe'
        self.real_esrgan_model_path = self.real_esrgan_exe.parent/'models'
        # https://github.com/TianZerL/Anime4KCPP
        self.anime4k_exe = self.toolkit_path/'Anime4KCPP_CLI'/'Anime4KCPP_CLI.exe'
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
        self.super_resolution_engine = self.vnc_config.get('General', 'super_resolution_engine')
        self.cpu_cores = self.vnc_config.getint('General', 'cpu_cores')
        self.gpu_id = self.vnc_config.get('General', 'gpu_id')
        # waifu2x-ncnn-vulkan相关配置
        self.waifu2x_ncnn_noise_level = self.vnc_config.get('waifu2x_ncnn', 'noise_level')
        self.waifu2x_ncnn_tile_size = self.vnc_config.get('waifu2x_ncnn', 'tile_size')
        self.waifu2x_ncnn_model_path = (self.waifu2x_ncnn_exe.parent)/(self.vnc_config.get('waifu2x_ncnn', 'model_name'))
        self.waifu2x_ncnn_load_proc_save = self.vnc_config.get('waifu2x_ncnn', 'load_proc_save')
        self.waifu2x_ncnn_tta = self.vnc_config.get('waifu2x_ncnn', 'tta')
        # Real-ESRGAN相关配置
        self.real_esrgan_tile_size = self.vnc_config.get('real_esrgan', 'tile_size')
        self.real_esrgan_model_name = self.vnc_config.get('real_esrgan', 'model_name')
        self.real_esrgan_load_proc_save = self.vnc_config.get('real_esrgan', 'load_proc_save')
        self.real_esrgan_tta = self.vnc_config.get('real_esrgan', 'tta')
        # ffmpeg相关配置
        self.video_quality = self.vnc_config.get('ffmpeg', 'video_quality')
