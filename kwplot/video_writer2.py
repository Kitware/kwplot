import os
import sys
import uuid
import math
from pathlib import Path

import ubelt as ub


class VideoInputs:
    """
    Abstract class for frame-path or in-memory-array video inputs.

    Input types:
      - frame_fpaths: list of file paths to image frames
      - ndarray: in-memory arrays of shape (N, H, W, C)
    """

    def __init__(self):
        self.temp_dpath = None
        self.input_dsize = None

    @classmethod
    def coerce(cls, inputs):
        """
        Factory: choose appropriate subclass based on inputs type.
        """
        import numpy as np

        if isinstance(inputs, cls):
            return inputs
        elif isinstance(inputs, np.ndarray) or (
            hasattr(inputs, '__iter__') and len(inputs) and isinstance(inputs[0], np.ndarray)
        ):
            return VideoArrayInputs(inputs)
        elif hasattr(inputs, '__iter__'):
            return VideoFramePathInputs(inputs)
        else:
            raise ValueError(f"Cannot coerce inputs of type {type(inputs)}")

    def _ensure_temp_dpath(self):
        if self.temp_dpath is None:
            base = Path(ub.Path.appdir('kwplot', 'video_writer', 'temp'))
            self.temp_dpath = (base / uuid.uuid4().hex).expanduser().resolve()
            self.temp_dpath.mkdir(parents=True, exist_ok=True)


class VideoFramePathInputs(VideoInputs):
    """
    Represents a list of paths to frames on disk.
    """

    def __init__(self, frame_fpaths, verbose=0):
        super().__init__()
        self.frame_fpaths = [Path(p) for p in frame_fpaths]
        self.verbose = verbose

    def __len__(self):
        return len(self.frame_fpaths)

    def _ensure_input_dsize(self):
        if self.input_dsize is None:
            import kwimage
            widths, heights = [], []
            for f in self.frame_fpaths:
                h, w, *_ = kwimage.load_image_shape(f)
                widths.append(w)
                heights.append(h)
            self.input_dsize = (max(widths), max(heights))

    def as_file_list_manifest(self):
        """
        Write a ffmpeg-concat-formatted list file.
        """
        self._ensure_temp_dpath()
        manifest = self.temp_dpath / f'frames_{uuid.uuid4().hex}.txt'
        lines = [f"file '{str(p.absolute())}'" for p in self.frame_fpaths]
        manifest.write_text("\n".join(lines) + "\n")
        return manifest


class VideoArrayInputs(VideoInputs):
    """
    Represents an in-memory list/ndarray of frames.
    """

    def __init__(self, frame_arrays):
        super().__init__()
        import numpy as np
        self.frame_arrays = np.asarray(frame_arrays)

    def __len__(self):
        return len(self.frame_arrays)

    def _ensure_input_dsize(self):
        if self.input_dsize is None:
            arr = self.frame_arrays
            if arr.ndim == 4:
                _, h, w, *_ = arr.shape
            else:
                heights, widths = [], []
                for img in arr:
                    h, w, *_ = img.shape
                    heights.append(h)
                    widths.append(w)
                h, w = max(heights), max(widths)
            self.input_dsize = (w, h)

    def _write_frames_to_disk(self):
        self._ensure_temp_dpath()
        import kwimage
        frame_dir = self.temp_dpath / 'frames'
        frame_dir.mkdir(parents=True, exist_ok=True)
        self.frame_fpaths = []
        for i, frame in enumerate(self.frame_arrays):
            fpath = frame_dir / f'frame_{i:06d}.jpg'
            kwimage.imwrite(fpath, frame)
            self.frame_fpaths.append(fpath)

    def as_file_list_manifest(self):
        self._write_frames_to_disk()
        return super().as_file_list_manifest()


class BaseFrameWriter:
    """
    Base class for backend writers.

    Common config options:
      - in_framerate (float): input FPS (all backends)
      - max_width (int): downscale filter max width (ffmpeg, cv2)
      - loop (int): number of loops for GIF (PIL, imagemagik)
      - quality (int or str): compression quality (ffmpeg CRF, imagemagik -quality)
      - codec (str): video codec name (ffmpeg, cv2)
    """
    def __init__(self, inputs, output_fpath):
        self.inputs = inputs
        self.output_fpath = Path(output_fpath)
        self.verbose = 0
        self.config = {
            'in_framerate': 1,
            'max_width': None,
            'loop': 0,           # 0=infinite (GIF)
            'quality': None,     # CRF for ffmpeg, -quality for imagemagik
            'codec': None,       # e.g. 'libx264' or 'mp4v'
        }

    def write(self):
        raise NotImplementedError


class FFMPEG_FrameWriter(BaseFrameWriter):
    """
    ffmpeg writer backend.

    Applies:
      - in_framerate -> -r
      - max_width -> scale filter
      - quality -> -crf
      - codec -> -c:v
    """
    def find_ffmpeg(self):
        exe = ub.find_exe('ffmpeg') or ub.find_exe('ffmpeg.exe')
        if exe is None:
            raise FileNotFoundError("ffmpeg executable not found")
        return exe

    def write(self):
        ffmpeg = self.find_ffmpeg()
        self.inputs._ensure_input_dsize()
        w, h = self.inputs.input_dsize
        w = int(2 * math.ceil(w / 2))
        h = int(2 * math.ceil(h / 2))

        manifest = self.inputs.as_file_list_manifest()
        fr = self.config['in_framerate']
        maxw = self.config['max_width']

        filters = []
        if maxw:
            filters.append(f'scale={maxw}:-2')
        filters.append(f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black')
        vf = ','.join(filters)

        opts = []
        if self.config['codec']:
            opts += ['-c:v', self.config['codec']]
        if self.config['quality'] is not None:
            opts += ['-crf', str(self.config['quality'])]

        cmd = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-r', str(fr),
               '-i', str(manifest), '-vf', vf] + opts + [str(self.output_fpath)]

        if self.verbose:
            print('FFMPEG CMD:', ' '.join(cmd))
        result = ub.cmd(cmd, shell=False, verbose=int(self.verbose > 1))
        if result['ret'] != 0:
            raise RuntimeError(result['err'])
        return self.output_fpath


class CV2_FrameWriter(BaseFrameWriter):
    """
    OpenCV writer backend.

    Applies:
      - in_framerate -> FPS arg
      - max_width -> manual resize (not implemented)
      - codec -> fourcc code
    """
    def write(self):
        import cv2
        import kwimage
        self.inputs._ensure_input_dsize()
        w, h = self.inputs.input_dsize
        fr = float(self.config['in_framerate'])
        codec = self.config['codec'] or 'mp4v'
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(str(self.output_fpath), fourcc, fr, (w, h))
        for p in getattr(self.inputs, 'frame_fpaths', []):
            frame = kwimage.imread(p, space='bgr')
            out.write(frame)
        out.release()
        return self.output_fpath


class ImageMagik_FrameWriter(BaseFrameWriter):
    """
    ImageMagick writer backend (via `convert`).

    Applies:
      - loop -> -loop
      - quality -> -quality
      - in_framerate -> -delay
    """
    def find_convert(self):
        exe = ub.find_exe('convert') or ub.find_exe('convert.exe')
        if exe is None:
            raise FileNotFoundError('ImageMagick convert not found')
        return exe

    def write(self):
        convert = self.find_convert()
        self.inputs._ensure_input_dsize()
        fr = self.config['in_framerate']
        delay = int(100 / fr)
        loop = self.config['loop']
        quality = self.config['quality']

        cmd = [convert, '-delay', str(delay), '-loop', str(loop)]
        if quality is not None:
            cmd += ['-quality', str(quality)]
        cmd += [str(p) for p in self.inputs.as_file_list_manifest().parent.iterdir()]
        cmd += [str(self.output_fpath)]

        if self.verbose:
            print('ImageMagick CMD:', ' '.join(cmd))
        info = ub.cmd(cmd, shell=False, verbose=int(self.verbose > 1))
        if info['ret']:
            raise RuntimeError(info['err'])
        return self.output_fpath


class PIL_FrameWriter(BaseFrameWriter):
    """
    PIL writer backend for animated GIF.

    Applies:
      - loop -> save_all & loop
      - in_framerate -> duration
      - quality -> optimize flag (not exact)
    """
    def write(self):
        from PIL import Image
        self.inputs._ensure_input_dsize()
        frames = []
        if hasattr(self.inputs, 'frame_fpaths'):
            for p in self.inputs.frame_fpaths:
                frames.append(Image.open(p))
        else:
            for arr in self.inputs.frame_arrays:
                frames.append(Image.fromarray(arr))

        duration = int(1000 / self.config['in_framerate'])
        first, *rest = frames
        save_kwargs = dict(save_all=True, append_images=rest,
                           duration=duration, loop=self.config['loop'])
        if self.config['quality'] is not None:
            save_kwargs['optimize'] = True

        first.save(self.output_fpath, **save_kwargs)
        return self.output_fpath


class VideoWriter:
    """
    High-level interface to write videos/GIFs from frames.

    Options (common config):

    | Option        | Type       | Applies To           | Effect
    |---------------|------------|----------------------|-----------------------------
    | in_framerate  | float      | all                  | Sets input frames per second
    | max_width     | int        | ffmpeg, cv2          | Downscale to this width
    | loop          | int        | GIF backends         | Number of loops (0=infinite)
    | quality       | int/str    | ffmpeg, imagemagik   | CRF (ffmpeg) or quality pct
    | codec         | str        | ffmpeg, cv2          | Video codec name (e.g. mp4v, libx264)

    Example:
        writer = VideoWriter.from_frame_paths(frames)
        writer.write(
            output='out.gif', backend='imagemagik',
            in_framerate=10, loop=0, quality=75
        )
    """
    def __init__(self, inputs=None, output=None, backend='ffmpeg'):
        self.inputs = VideoInputs.coerce(inputs) if inputs else None
        self.output = Path(output) if output else None
        self.backend = backend.lower()
        self.verbose = 0
        self.config = {}

    @classmethod
    def from_frame_paths(cls, frame_fpaths):
        return cls(inputs=VideoFramePathInputs(frame_fpaths))

    def write(self, output=None, backend=None, **options):
        if output:
            self.output = Path(output)
        if backend:
            self.backend = backend.lower()
        self.config.update(options)

        writers = {
            'ffmpeg': FFMPEG_FrameWriter,
            'cv2': CV2_FrameWriter,
            'imagemagik': ImageMagik_FrameWriter,
            'pil': PIL_FrameWriter,
        }
        if self.backend not in writers:
            raise ValueError(f"Unsupported backend: {self.backend}")

        writer = writers[self.backend](self.inputs, self.output)
        writer.verbose = self.verbose
        writer.config.update({
            'in_framerate': options.get('in_framerate', 1),
            'max_width': options.get('max_width'),
            'loop': options.get('loop', 0),
            'quality': options.get('quality'),
            'codec': options.get('codec'),
        })
        return writer.write()

# Aliases
ffmpeg_animate_frames = lambda fps, out, **kw: VideoWriter(fps, out, backend='ffmpeg').write(**kw)


def benchmark_video_writer():
    """
    Run benchmark across backends (ffmpeg, imagemagik, cv2, pil) on demo data.

    Returns:
        dict: mapping backend names to elapsed time in seconds.

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/code/kwplot'))
        >>> from kwplot.video_writer2 import *  # NOQA
        >>> from kwplot.video_writer import benchmark_video_writer
        >>> results = benchmark_video_writer()
        >>> isinstance(results, dict)
        True
    """
    import time
    import ubelt as ub
    import kwcoco

    dset = kwcoco.CocoDataset.demo('shapes8')
    frames = sorted(dset.images().gpath)
    results = {}
    for backend in ['ffmpeg', 'imagemagik', 'cv2', 'pil']:
        writer = VideoWriter.from_frame_paths(frames)
        out_dir = ub.Path.appdir('kwplot', 'video_bench').ensuredir()
        ext = 'gif' if backend in ['imagemagik', 'pil'] else 'mp4'
        out = out_dir / f'bench_{backend}.{ext}'
        start = time.time()
        try:
            writer.write(output=out, backend=backend, in_framerate=2, loop=0, quality=50)
            elapsed = time.time() - start
        except Exception:
            elapsed = None
        results[backend] = elapsed
    return results
