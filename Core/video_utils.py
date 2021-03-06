# -*- coding: utf-8 -*-

from .functions import *


class VideoUtils(object):
    """
    @brief      专用于处理视频文件
    """

    def video_info(self, input_video) -> dict or bool:
        """
        @brief      调用ffprobe获取视频信息

        @param      input_video  输入视频

        @return     返回视频信息字典，未识别视频返回False
        """
        input_video = Path(input_video)
        options = [self.ffprobe,
                   '-show_format',
                   '-show_streams',
                   '-of', 'json',
                   input_video
                   ]
        get_video_info_p = subprocess.run(options, capture_output=True, shell=True)
        unsort_video_info = json.loads(get_video_info_p.stdout.decode('utf-8'))
        # 非常规编码视频返回空字典
        if not unsort_video_info or len(unsort_video_info['streams']) == 0:
            return False
        else:
            if len(unsort_video_info['streams']) == 1:
                video = 0
                audio = None
            elif unsort_video_info['streams'][0]['codec_type'] == 'video' and unsort_video_info['streams'][1]['codec_type'] == 'audio':
                video = 0
                audio = 1
            elif unsort_video_info['streams'][1]['codec_type'] == 'video' and unsort_video_info['streams'][0]['codec_type'] == 'audio':
                video = 1
                audio = 0
            video_info = {}
            video_info['vcodec'] = unsort_video_info['streams'][video]['codec_name']
            video_info['width'] = unsort_video_info['streams'][video]['width']
            video_info['height'] = unsort_video_info['streams'][video]['height']
            try:
                video_info['frame_rate'] = '%.2f' % eval(unsort_video_info['streams'][video]['avg_frame_rate'])
            except:
                video_info['frame_rate'] = '%.2f' % eval(unsort_video_info['streams'][video]['r_frame_rate'])
            # video_info['bit_rate'] = unsort_video_info['streams'][video]['bit_rate']
            video_info['video_duration'] = unsort_video_info['streams'][video]['duration']
            if audio != None:
                video_info['acodec'] = unsort_video_info['streams'][audio]['codec_name']
                video_info['audio_duration'] = unsort_video_info['streams'][audio]['duration']
            return video_info

    def vcodec_trans(self, input_video, output_video, output_vcodec):
        """
        @brief      视频转码、压制

        @param      input_video    输入视频路径
        @param      output_video   输出视频路径
        @param      output_vcodec  输出视频编码
        """
        input_video = Path(input_video)
        output_video = Path(output_video)
        options = [self.ffmpeg, '-y',
                   '-i', input_video,
                   '-c:v', output_vcodec,
                   '-q:v', self.output_video_quality(output_vcodec),
                   output_video
                   ]
        format_trans_p = subprocess.run(options, capture_output=True, shell=True)
        return output_video

    def video2png(self, input_video, output_folder):
        """
        @brief      将视频转换为png图片序列

        @param      input_video    输入视频
        @param      output_folder  输出文件夹

        @return     输出文件夹, 图片序列名称
        """
        input_video = Path(input_video)
        output_folder = Path(output_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
        png_sequence = output_folder/(input_video.stem+'_%08d.png')
        options = [self.ffmpeg, '-y',
                   '-i', input_video,
                   '-qscale:v', '1',
                   '-qmin', '1',
                   '-qmax', '1',
                   '-vsync', '0',
                   '-threads', str(self.cpu_cores),
                   png_sequence
                   ]
        video2png_p = subprocess.run(options, capture_output=True, shell=True)
        return png_sequence

    def output_video_quality(self, output_vcodec) -> str:
        """
        @brief      返回ffmpeg输出视频的质量参数

        @param      output_vcodec  输出视频编码

        @return     视频质量参数
        """
        special_vcodecs = ['theora']
        if output_vcodec not in special_vcodecs:
            video_quality = str(10 - int(self.video_quality))
        else:
            # 特殊编码视频的质量设定与常规视频不统一
            video_quality = self.video_quality
        return video_quality

    def png2video(self, png_sequence, origin_video, output_video, output_vcodec=None):
        """
        @brief      将放大后的png图片序列转换回视频

        @param      png_sequence   png图片序列
        @param      origin_video   原始视频(提供音频)
        @param      output_video   输出视频路径
        @param      output_vcodec  输出视频编码格式，默认为原视频编码格式

        @return     输出视频路径
        """
        png_sequence = Path(png_sequence)
        origin_video = Path(origin_video)
        output_video = Path(output_video)
        origin_video_info = self.video_info(origin_video)
        if output_vcodec is None:
            output_vcodec = origin_video_info['vcodec']
            if output_vcodec == 'wmv3':
                output_vcodec = 'wmv2'
        elif output_vcodec == 'wmv3':
            raise ValueError('输出视频编码不能为wmv3')
        options = [self.ffmpeg, '-y',
                   '-r', origin_video_info['frame_rate'],
                   '-i', png_sequence.to_str,
                   '-i', origin_video,
                   '-map', '0:v:0',
                   '-map', '1:a:0?',
                   '-c:a', 'copy',
                   '-c:v', output_vcodec,
                   '-r', origin_video_info['frame_rate'],
                   '-q:v', self.output_video_quality(output_vcodec),
                   '-threads', str(self.cpu_cores),
                   output_video
                   ]
        png2video_p = subprocess.run(options, capture_output=True, shell=True)
        return output_video

    def video_upscale(self, input_video, output_video, scale_ratio=2.0, output_vcodec=None):
        """
        @brief      视频放大

        @param      input_video    输出视频路径
        @param      output_video   输出视频路径
        @param      scale_ratio    视频放大倍数
        @param      output_vcodec  输出视频编码

        @return     输出视频路径
        """
        input_video = Path(input_video)
        output_video = Path(output_video)
        if not output_video.parent.exists():
            output_video.parent.mkdir(parents=True)
        if output_vcodec is None:
            output_vcodec = self.video_info(input_video)['vcodec']
            # ffmpeg不支持wmv3编码
            if output_vcodec == 'wmv3':
                output_vcodec = 'wmv2'
        elif output_vcodec == 'wmv3':
            raise ValueError('输出视频编码不能为wmv3')
        with tempfile.TemporaryDirectory() as video_tmp_folder1:
            video_tmp_folder1 = Path(video_tmp_folder1)
            self.emit_info(f'{input_video}拆帧中......')
            png_sequence = self.video2png(input_video, video_tmp_folder1)
            self.emit_info(f'{input_video}放大中......')
            self.image_upscale(video_tmp_folder1, video_tmp_folder1, scale_ratio, video_mode=True)
            tmp_video = video_tmp_folder1/output_video.name
            self.emit_info(f'{output_video}编码中......')
            tmp_video = self.png2video(png_sequence, input_video, tmp_video, output_vcodec)
            tmp_video.move_as(output_video)
        return output_video
