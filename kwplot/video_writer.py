"""
A tool to write videos with different backends from different types of inputs.


Inputs Implementation Status:

    - [x] List of paths to frame images

    - [ ] List of in-memory frame arrays

Backend Implementation Status:

    - [x] ffmpeg

    - [x] imagemagik

    - [ ] cv2

    - [ ] PIL (for gifs)

TODO:

    - [ ] Does this belong in kwimage?

Note:
    Used by :mod:`kwcoco.cli.gifify`
"""
import ubelt as ub


def ffmpeg_animate_frames(frame_fpaths, output_fpath, in_framerate=1,
                          verbose=3, max_width=None, temp_dpath=None):
    """
    Use ffmpeg to transform a series of frames into a video.

    Args:
        frame_fpaths (List[PathLike]):
            ordered list of frames to be combined into an animation

        output_fpath (PathLike):
            output video name, as either a gif, avi, mp4, etc.

        in_framerate (int):
            number of input frames per second to use (lower is slower)

    References:
        https://superuser.com/questions/624563/how-to-resize-a-video-to-make-it-smaller-with-ffmpeg

    Example:
        >>> # xdoctest: +REQUIRES(module:kwcoco)
        >>> from kwplot.video_writer import *  # NOQA
        >>> import kwcoco
        >>> dset = kwcoco.CocoDataset.demo('shapes8')
        >>> ffmpeg_exe = ub.find_exe('ffmpeg')
        >>> if ffmpeg_exe is None:
        >>>     import pytest
        >>>     pytest.skip('test requires ffmpeg')
        >>> frame_fpaths = sorted(dset.images().gpath)
        >>> test_dpath = ub.Path.appdir('gifify', 'test').ensuredir()
        >>> # Test output to MP4
        >>> output_fpath = test_dpath / 'test.mp4'
        >>> ffmpeg_animate_frames(frame_fpaths, output_fpath, in_framerate=0.5)

    Example:
        >>> # xdoctest: +REQUIRES(module:kwcoco)
        >>> from kwplot.video_writer import *  # NOQA
        >>> import kwcoco
        >>> dset = kwcoco.CocoDataset.demo('shapes8')
        >>> ffmpeg_exe = ub.find_exe('ffmpeg')
        >>> if ffmpeg_exe is None:
        >>>     import pytest
        >>>     pytest.skip('test requires ffmpeg')
        >>> frame_fpaths = sorted(dset.images().gpath)
        >>> test_dpath = ub.Path.appdir('gifify', 'test').ensuredir()
        >>> # Test output to GIF
        >>> output_fpath = test_dpath / 'test.gif'
        >>> ffmpeg_animate_frames(frame_fpaths, output_fpath, in_framerate=0.5)
        >>> # Test number of frames is correct
        >>> from PIL import Image
        >>> pil_gif = Image.open(output_fpath)
        >>> try:
        >>>     while 1:
        >>>         pil_gif.seek(pil_gif.tell()+1)
        >>>         # do something to im
        >>> except EOFError:
        >>>     pass # end of sequence
        >>> assert pil_gif.tell() + 1 == dset.n_images
        >>> # Test output to video
        >>> output_fpath = test_dpath / 'test.mp4'
    """
    inputs = VideoFrameInputs(frame_fpaths)
    writer = FFMPEG_FrameWriter(inputs, output_fpath)
    writer.verbose = verbose
    writer.config['in_framerate'] = in_framerate
    writer.config['max_width'] = max_width


class VideoInputs:
    """
    Abstract class for frame-path or in-memory-array video inputs
    """


class VideoFrameInputs(VideoInputs):
    """
    Represents a list of video frames as inputs.
    Metadata about inputs can be passed or introspected.
    """

    def __init__(self, frame_fpaths=None, input_dsize=None, temp_dpath=None,
                 verbose=0):
        self.frame_fpaths = frame_fpaths
        self.input_dsize = None
        self.verbose = verbose
        self.temp_dpath = None

    def __len__(self):
        return len(self.frame_fpaths)

    def _ensure_input_dsize(self):
        """
        Infer input width / height if not given
        """
        # Determine the maximum size of the image
        if self.input_dsize is None:
            imgsize_jobs = ub.JobPool(max_workers=0)
            import kwimage
            for fpath in self.frame_fpaths:
                imgsize_jobs.submit(kwimage.load_image_shape, fpath)
            max_w = 0
            max_h = 0
            for result in imgsize_jobs.as_completed():
                shape = result.result()
                h, w, *_ = shape
                max_h = max(max_h, h)
                max_w = max(max_w, w)
            self.input_dsize = (max_w, max_h)

    def _ensure_temp_dpath(self):
        """
        Infer input width / height if not given
        """
        if self.temp_dpath is None:
            self.temp_dpath = ub.Path.appdir('kwplot', 'gifify', 'temp').ensuredir()

    def as_file_list_manifest(self):
        """
        Convert to a file list input (for ffmpeg)
        """
        import uuid
        self._ensure_temp_dpath()
        temp_fpath = self.temp_dpath / f'temp_list_{uuid.uuid4()}.txt'
        lines = ["file '{}'".format(ub.Path(fpath).absolute())
                 for fpath in self.frame_fpaths]
        text = '\n'.join(lines)
        with open(temp_fpath, 'w') as file:
            file.write(text + '\n')
        return temp_fpath


class VideoArrayInputs(VideoInputs):
    """
    Represents a list of video frames as inputs
    """

    def __init__(self, frame_arrays):
        self.frame_arrays = frame_arrays


class CV2_FrameWriter:
    def __init__(self, inputs=None, output_fpath=None):
        self.inputs = inputs
        self.output_fpath = output_fpath
        self.verbose = 0
        self.config = {
            'max_width': None,
            'in_framerate': 1,
        }

    def find_convert(self):
        exe = ub.find_exe('convert') or ub.find_exe('convert.exe')
        if exe is None:
            raise FileNotFoundError('Cannot find convert, cannot use ImageMagik_FrameWriter')
        return exe

    def write(self):
        import cv2
        import os
        import kwimage
        self.inputs._ensure_input_dsize()
        max_w, max_h = self.inputs.input_dsize
        in_framerate = float(self.config['in_framerate'])
        dsize = (max_w, max_h)
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        output_fpath = os.fspath(self.output_fpath)
        output = cv2.VideoWriter(
            output_fpath, fourcc, in_framerate, dsize)
        try:
            for frame_fpath in self.inputs.frame_fpaths:
                frame = kwimage.imread(frame_fpath, space='bgr')
                output.write(frame)
        finally:
            output.release()


class ImageMagik_FrameWriter:
    def __init__(self, inputs=None, output_fpath=None):
        self.inputs = inputs
        self.output_fpath = output_fpath
        self.verbose = 0
        self.config = {
            'max_width': None,
            'in_framerate': 1,
        }

    def find_convert(self):
        exe = ub.find_exe('convert') or ub.find_exe('convert.exe')
        if exe is None:
            raise FileNotFoundError('Cannot find convert, cannot use ImageMagik_FrameWriter')
        return exe

    def write(self):
        import os
        convert_exe = self.find_convert()
        escaped_gif_fpath = os.fspath(self.output_fpath).replace('%', '%%')

        delay = (1 / self.config['in_framerate']) * 100
        # Note: delay might not work unless writing to a gif
        # https://superuser.com/questions/1416395/imagemagick-convert-is-not-adjusting-mp4-framerate-as-expected
        # https://imagemagick.org/script/command-line-options.php?#delay
        command = [convert_exe, '-delay', str(delay), '-loop', '0']
        command += self.inputs.frame_fpaths
        command += [escaped_gif_fpath]
        print('Converting {} images to gif: {}'.format(len(self.inputs), escaped_gif_fpath))
        info = ub.cmd(command, verbose=3)
        print('finished')
        if info['ret'] != 0:
            print(info['out'])
            print(info['err'])
            raise RuntimeError(info['err'])


class FFMPEG_FrameWriter:
    def __init__(self, inputs=None, output_fpath=None):
        self.inputs = inputs
        self.output_fpath = output_fpath
        self.verbose = 0
        self.config = {
            'max_width': None,
            'in_framerate': 1,
        }

    def find_ffmpeg(self):
        ffmpeg_exe = ub.find_exe('ffmpeg') or ub.find_exe('ffmpeg.exe')
        if ffmpeg_exe is None:
            raise FileNotFoundError('Cannot find ffmpeg, cannot use FFMPEG_Writer')
        return ffmpeg_exe

    def write(self):
        import sys
        import math
        ffmpeg_exe = self.find_ffmpeg()

        self.inputs._ensure_input_dsize()
        max_w, max_h = self.inputs.input_dsize
        temp_fpath = self.inputs.as_file_list_manifest()

        # https://stackoverflow.com/questions/20847674/ffmpeg-libx264-height-not-divisible-by-2
        # evan_pad_option = '-filter:v pad="width=ceil(iw/2)*2:height=ceil(ih/2)*2"'
        # vid_options = '-c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p'

        fmtkw = dict(
            IN=temp_fpath,
            OUT=self.output_fpath,
        )

        global_options = []
        input_options = [
            '-r {IN_FRAMERATE} ',
            '-f concat -safe 0',
            # '-framerate {IN_FRAMERATE} ',
        ]
        fmtkw.update(dict(
            IN_FRAMERATE=self.config['in_framerate'],
        ))

        output_options = [
            # '-qscale 0',
            # '-crf 20',
            # '-r {OUT_FRAMERATE}',
            # '-filter:v scale=512:-1',

            # higher quality
            # https://stackoverflow.com/questions/42980663/ffmpeg-high-quality-animated-gif
            # '-filter_complex "fps=10;scale=500:-1:flags=lanczos,palettegen=stats_mode=full"'
            # '-filter_complex "fps=10;scale=500:-1:flags=lanczos,palettegen=stats_mode=full"'
            # '-filter_complex "fps=10;scale=500:-1:flags=lanczos,split[v1][v2]; [v1]palettegen=stats_mode=full [palette];[v2]palette]paletteuse=dither=sierra2_4a" -t 10'
        ]
        fmtkw.update(dict(
            # OUT_FRAMERATE=5,
        ))

        filtergraph_parts = []
        max_width = self.config['max_width']

        if max_width is not None:
            filtergraph_parts.append(f'scale={max_width}:-1')

        # scale_options.append(
        #     'force_original_aspect_ratio=decrease'
        # )
        # output_options += [
        #     '-vf scale="{}:-1"'.format(max_width)
        # ]

        # Ensure width and height are even for mp4 outputs
        max_w = int(2 * math.ceil(max_w / 2.))
        max_h = int(2 * math.ceil(max_h / 2.))

        # Ensure all padding happens to the bottom right by setting the
        # frame size to something constant and putting the data at x,y=0,0
        filtergraph_parts += [
            f"pad=w={max_w}:h={max_h}:x=0:y=0:color=black",
        ]

        # if output_fpath.endswith('.mp4'):
        #     # filtergraph_parts += [
        #     #     'pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2:x=0:y=0',
        #     # ]
        #     # output_options += [
        #     #     # MP4 needs even width
        #     #     # https://stackoverflow.com/questions/20847674/ffmpeg-div2
        #     #     '-filter:v "pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2"',
        #     # ]

        if filtergraph_parts:
            filtergraph = ','.join(filtergraph_parts)
            output_options += [
                f'-filter:v "{filtergraph}"'
            ]

        cmd_fmt = ' '.join(
            [ffmpeg_exe, '-y'] +
            global_options +
            input_options +
            ['-i {IN}'] +
            output_options +
            ["'{OUT}'"]
        )

        command = cmd_fmt.format(**fmtkw)

        if self.verbose > 0:
            print('Converting {} images to animation: {}'.format(len(self.inputs), self.output_fpath))

        try:
            info = ub.cmd(command, verbose=3 if self.verbose > 1 else 0, shell=True)
        finally:
            if sys.stdout.isatty():
                # ffmpeg seems prone to breaking tty output, this seems to fix it.
                ub.cmd('stty sane')

        if self.verbose > 0:
            print('finished')

        if info['ret'] != 0:
            # if not verbose:
            # print(info['out'])
            # print(info['err'])
            raise RuntimeError(info['err'])
        # -f concat -i mylist.txt
        #   ffmpeg \
        # -framerate 60 \
        # -pattern_type glob \
        # -i '*.png' \
        # -r 15 \
        # -vf scale=512:-1 \
        # out.gif
        return self.output_fpath


class VideoWriter:
    """
    Abstracts different input types and backends for writing video files.

    Example:
        >>> # xdoctest: +REQUIRES(module:kwcoco)
        >>> from kwplot.cli.gifify import *  # NOQA
        >>> if ub.find_exe('ffmpeg') is None:
        >>>     import pytest
        >>>     pytest.skip('test requires ffmpeg')
        >>> # Get a list of images to turn into an animation
        >>> frame_fpaths = sorted(dset.images().gpath)
        >>> test_dpath = ub.Path.appdir('kwplot', 'video_maker', 'test').ensuredir()
        >>> # Test output to MP4
        >>> output_fpath = test_dpath / 'test.gif'
        >>> # Build the VideoWriter
        >>> self = VideoWriter.from_frame_paths(frame_fpaths)
        >>> self.output_fpath = output_fpath
        >>> self.config['in_framerate'] = 22
        >>> self.verbose = 1
        >>> self.write()
    """

    def __init__(self):
        self.inputs = None
        self.output_fpath = None
        self.backend = 'ffmpeg'
        self.verbose = 0
        # backend = 'imagemagik'
        # backend = 'cv2'
        self.config = ub.udict({
            'in_framerate': 1,
            'max_width': None,
        })

    @classmethod
    def demo(cls):
        import kwcoco
        dset = kwcoco.CocoDataset.demo(
            'vidshapes', num_videos=2, num_frames=32,
            image_size=(512, 512), background='carl')
        frame_fpaths = sorted(dset.images().gpath)
        self = VideoWriter.from_frame_paths(frame_fpaths)
        return self

    @classmethod
    def from_frame_paths(cls, frame_fpaths):
        """
        Create a video from a list of paths to frame iamges
        """
        self = cls()
        self.inputs = VideoFrameInputs(frame_fpaths)
        return self

    def write(self):
        if self.backend == 'ffmpeg':
            cls = FFMPEG_FrameWriter
        elif self.backend == 'imagemagik':
            cls = ImageMagik_FrameWriter
        elif self.backend == 'cv2':
            cls = CV2_FrameWriter
        else:
            raise NotImplementedError
        self.backend_writer = cls(self.inputs, self.output_fpath)
        self.backend_writer.verbose = self.verbose
        self.backend_writer.config.update(self.config)
        self.backend_writer.write()

        return self.output_fpath


def benchmark_video_maker():
    from kwplot.video_writer import VideoWriter

    test_dpath = ub.Path.appdir('kwplot', 'video_maker', 'benchmark').ensuredir()

    self = VideoWriter.demo()
    self.backend = 'ffmpeg'
    self.output_fpath = test_dpath / f'benchmark-{self.backend}.mp4'
    self.config['in_framerate'] = 5
    self.verbose = 1
    output_fpath = self.write()
    # Check details of written video
    _ = ub.cmd(f'ffmpeg -i {output_fpath}', verbose=3)

    self.backend = 'imagemagik'
    self.output_fpath = test_dpath / f'benchmark-{self.backend}.mp4'
    output_fpath = self.write()
    _ = ub.cmd(f'ffmpeg -i {output_fpath}', verbose=3)

    self.backend = 'cv2'
    self.output_fpath = test_dpath / f'benchmark-{self.backend}.mp4'
    output_fpath = self.write()
    _ = ub.cmd(f'ffmpeg -i {output_fpath}', verbose=3)

    self = self.backend_writer
