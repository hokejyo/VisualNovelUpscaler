# -*- coding: utf-8 -*-

from .functions import *


class VideoUtils(object):
    """
    @brief      专用于处理视频文件
    """

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
