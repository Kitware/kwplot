from typing import List
from os import PathLike
import scriptconfig as scfg
from _typeshed import Incomplete


class Gifify(scfg.DataConfig):
    __command__: str
    __alias__: Incomplete
    image_list: Incomplete
    delay: Incomplete
    output: Incomplete
    max_width: Incomplete
    frames_per_second: Incomplete

    @classmethod
    def main(cls, cmdline: bool = ..., **kwargs):
        ...


def ffmpeg_animate_frames(frame_fpaths: List[PathLike],
                          output_fpath: PathLike,
                          in_framerate: int = 1,
                          verbose: int = ...,
                          max_width: Incomplete | None = ...) -> None:
    ...


__notes__: str
