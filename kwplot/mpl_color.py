# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import six
import ubelt as ub


class Color(ub.NiceRepr):
    """
    move to colorutil?

    Args:
        space (str): colorspace of wrapped color.
            Assume RGB if not specified and it cannot be inferred

    Example:
        >>> print(Color('g'))
        >>> print(Color('orangered'))
        >>> print(Color('#AAAAAA').as255())
        >>> print(Color([0, 255, 0]))
        >>> print(Color([1, 1, 1.]))
        >>> print(Color([1, 1, 1]))
        >>> print(Color(Color([1, 1, 1])).as255())
        >>> print(Color(Color([1., 0, 1, 0])).ashex())
        >>> print(Color([1, 1, 1], alpha=255))
        >>> print(Color([1, 1, 1], alpha=255, space='lab'))
    """
    def __init__(self, color, alpha=None, space=None):
        try:
            # Hack for ipython reload
            is_color_cls = color.__class__.__name__ == 'Color'
        except Exception:
            is_color_cls = isinstance(color, Color)

        if is_color_cls:
            assert alpha is None
            assert space is None
            space = color.space
            color = color.color01
        else:
            color = self._ensure_color01(color)
            if alpha is not None:
                alpha = self._ensure_color01([alpha])[0]

        if space is None:
            space = 'rgb'

        # always normalize the color down to 01
        color01 = list(color)

        if alpha is not None:
            if len(color01) not in [1, 3]:
                raise ValueError('alpha already in color')
            color01 = color01 + [alpha]

        # correct space if alpha is given
        if len(color01) in [2, 4]:
            if not space.endswith('a'):
                space += 'a'

        self.color01 = color01

        self.space = space

    def __nice__(self):
        colorpart = ', '.join(['{:.2f}'.format(c) for c in self.color01])
        return self.space + ': ' + colorpart

    def ashex(self, space=None):
        c255 = self.as255(space)
        return '#' + ''.join(['{:02x}'.format(c) for c in c255])

    def as255(self, space=None):
        color = (np.array(self.as01(space)) * 255).astype(np.uint8)
        return tuple(map(int, color))

    def as01(self, space=None):
        """
        self = mplutil.Color('red')
        mplutil.Color('green').as01('rgba')

        """
        color = tuple(self.color01)
        if space is not None:
            if space == self.space:
                pass
            elif space == 'rgba' and self.space == 'rgb':
                color = color + (1,)
            elif space == 'bgr' and self.space == 'rgb':
                color = color[::-1]
            elif space == 'rgb' and self.space == 'bgr':
                color = color[::-1]
            else:
                assert False
        return tuple(map(float, color))

    @classmethod
    def _is_base01(channels):
        """ check if a color is in base 01 """
        def _test_base01(channels):
            tests01 = {
                'is_float': all([isinstance(c, (float, np.float64)) for c in channels]),
                'is_01': all([c >= 0.0 and c <= 1.0 for c in channels]),
            }
            return tests01
        if isinstance(channels, six.string_types):
            return False
        return all(_test_base01(channels).values())

    @classmethod
    def _is_base255(Color, channels):
        """ there is a one corner case where all pixels are 1 or less """
        if (all(c > 0.0 and c <= 255.0 for c in channels) and any(c > 1.0 for c in channels)):
            # Definately in 255 space
            return True
        else:
            # might be in 01 or 255
            return all(isinstance(c, int) for c in channels)

    @classmethod
    def _hex_to_01(Color, hex_color):
        """
        hex_color = '#6A5AFFAF'
        """
        assert hex_color.startswith('#'), 'not a hex string %r' % (hex_color,)
        parts = hex_color[1:].strip()
        color255 = tuple(int(parts[i: i + 2], 16) for i in range(0, len(parts), 2))
        assert len(color255) in [3, 4], 'must be length 3 or 4'
        return Color._255_to_01(color255)

    def _ensure_color01(Color, color):
        """ Infer what type color is and normalize to 01 """
        if isinstance(color, six.string_types):
            color = Color._string_to_01(color)
        elif Color._is_base255(color):
            color = Color._255_to_01(color)
        return color

    @classmethod
    def _255_to_01(Color, color255):
        """ converts base 255 color to base 01 color """
        return [channel / 255.0 for channel in color255]

    @classmethod
    def _string_to_01(Color, color):
        """
        mplutil.Color._string_to_01('green')
        mplutil.Color._string_to_01('red')
        """
        if color == 'random':
            import random
            color = random.choice(Color.named_colors())

        from matplotlib import colors as mcolors
        if color in mcolors.BASE_COLORS:
            color01 = mcolors.BASE_COLORS[color]
        elif color in mcolors.CSS4_COLORS:
            color_hex = mcolors.CSS4_COLORS[color]
            color01 = Color._hex_to_01(color_hex)
        elif color.startswith('#'):
            color01 = Color._hex_to_01(color)
        else:
            raise ValueError('unknown color=%r' % (color,))
        return color01

    @classmethod
    def named_colors(cls):
        """
        Returns:
            List[str]: names of colors that Color accepts
        """
        from matplotlib import colors as mcolors
        names = sorted(list(mcolors.BASE_COLORS.keys()) + list(mcolors.CSS4_COLORS.keys()))
        return names

    @classmethod
    def distinct(Color, num, space='rgb'):
        """
        Make multiple distinct colors
        """
        import matplotlib as mpl
        import matplotlib._cm  as _cm
        cm = mpl.colors.LinearSegmentedColormap.from_list(
            'gist_rainbow', _cm.datad['gist_rainbow'],
            mpl.rcParams['image.lut'])
        distinct_colors = [
            np.array(cm(i / num)).tolist()[0:3]
            for i in range(num)
        ]
        if space == 'rgb':
            return distinct_colors
        else:
            return [Color(c, space='rgb').as01(space=space) for c in distinct_colors]

    @classmethod
    def random(Color, pool='named'):
        return Color('random')
