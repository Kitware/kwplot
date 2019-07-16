# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import six
import ubelt as ub


class mcolors:
    # Duplicates data in matplotlib

    BASE_COLORS = {
        'b': (0, 0, 1),
        'g': (0, 0.5, 0),
        'r': (1, 0, 0),
        'c': (0, 0.75, 0.75),
        'm': (0.75, 0, 0.75),
        'y': (0.75, 0.75, 0),
        'k': (0, 0, 0),
        'w': (1, 1, 1)
    }

    CSS4_COLORS = {
        'aliceblue': '#F0F8FF', 'antiquewhite': '#FAEBD7', 'aqua': '#00FFFF',
        'aquamarine': '#7FFFD4', 'azure': '#F0FFFF', 'beige': '#F5F5DC',
        'bisque': '#FFE4C4', 'black': '#000000', 'blanchedalmond': '#FFEBCD',
        'blue': '#0000FF', 'blueviolet': '#8A2BE2', 'brown': '#A52A2A',
        'burlywood': '#DEB887', 'cadetblue': '#5F9EA0', 'chartreuse': '#7FFF00',
        'chocolate': '#D2691E', 'coral': '#FF7F50', 'cornflowerblue': '#6495ED',
        'cornsilk': '#FFF8DC', 'crimson': '#DC143C', 'cyan': '#00FFFF',
        'darkblue': '#00008B', 'darkcyan': '#008B8B', 'darkgoldenrod': '#B8860B',
        'darkgray': '#A9A9A9', 'darkgreen': '#006400', 'darkgrey': '#A9A9A9',
        'darkkhaki': '#BDB76B', 'darkmagenta': '#8B008B', 'darkolivegreen': '#556B2F',
        'darkorange': '#FF8C00', 'darkorchid': '#9932CC', 'darkred': '#8B0000',
        'darksalmon': '#E9967A', 'darkseagreen': '#8FBC8F', 'darkslateblue': '#483D8B',
        'darkslategray': '#2F4F4F', 'darkslategrey': '#2F4F4F', 'darkturquoise': '#00CED1',
        'darkviolet': '#9400D3', 'deeppink': '#FF1493', 'deepskyblue': '#00BFFF',
        'dimgray': '#696969', 'dimgrey': '#696969', 'dodgerblue': '#1E90FF',
        'firebrick': '#B22222', 'floralwhite': '#FFFAF0', 'forestgreen': '#228B22',
        'fuchsia': '#FF00FF', 'gainsboro': '#DCDCDC', 'ghostwhite': '#F8F8FF',
        'gold': '#FFD700', 'goldenrod': '#DAA520', 'gray': '#808080',
        'green': '#008000', 'greenyellow': '#ADFF2F', 'grey': '#808080',
        'honeydew': '#F0FFF0', 'hotpink': '#FF69B4', 'indianred': '#CD5C5C',
        'indigo': '#4B0082', 'ivory': '#FFFFF0', 'khaki': '#F0E68C',
        'lavender': '#E6E6FA', 'lavenderblush': '#FFF0F5', 'lawngreen': '#7CFC00',
        'lemonchiffon': '#FFFACD', 'lightblue': '#ADD8E6', 'lightcoral': '#F08080',
        'lightcyan': '#E0FFFF', 'lightgoldenrodyellow': '#FAFAD2', 'lightgray': '#D3D3D3',
        'lightgreen': '#90EE90', 'lightgrey': '#D3D3D3', 'lightpink': '#FFB6C1',
        'lightsalmon': '#FFA07A', 'lightseagreen': '#20B2AA', 'lightskyblue': '#87CEFA',
        'lightslategray': '#778899', 'lightslategrey': '#778899', 'lightsteelblue': '#B0C4DE',
        'lightyellow': '#FFFFE0', 'lime': '#00FF00', 'limegreen': '#32CD32',
        'linen': '#FAF0E6', 'magenta': '#FF00FF', 'maroon': '#800000',
        'mediumaquamarine': '#66CDAA', 'mediumblue': '#0000CD', 'mediumorchid': '#BA55D3',
        'mediumpurple': '#9370DB', 'mediumseagreen': '#3CB371', 'mediumslateblue': '#7B68EE',
        'mediumspringgreen': '#00FA9A', 'mediumturquoise': '#48D1CC', 'mediumvioletred': '#C71585',
        'midnightblue': '#191970', 'mintcream': '#F5FFFA', 'mistyrose': '#FFE4E1',
        'moccasin': '#FFE4B5', 'navajowhite': '#FFDEAD', 'navy': '#000080',
        'oldlace': '#FDF5E6', 'olive': '#808000', 'olivedrab': '#6B8E23',
        'orange': '#FFA500', 'orangered': '#FF4500', 'orchid': '#DA70D6',
        'palegoldenrod': '#EEE8AA', 'palegreen': '#98FB98', 'paleturquoise': '#AFEEEE',
        'palevioletred': '#DB7093', 'papayawhip': '#FFEFD5', 'peachpuff': '#FFDAB9',
        'peru': '#CD853F', 'pink': '#FFC0CB', 'plum': '#DDA0DD',
        'powderblue': '#B0E0E6', 'purple': '#800080', 'rebeccapurple': '#663399',
        'red': '#FF0000', 'rosybrown': '#BC8F8F', 'royalblue': '#4169E1',
        'saddlebrown': '#8B4513', 'salmon': '#FA8072', 'sandybrown': '#F4A460',
        'seagreen': '#2E8B57', 'seashell': '#FFF5EE', 'sienna': '#A0522D',
        'silver': '#C0C0C0', 'skyblue': '#87CEEB', 'slateblue': '#6A5ACD',
        'slategray': '#708090', 'slategrey': '#708090', 'snow': '#FFFAFA',
        'springgreen': '#00FF7F', 'steelblue': '#4682B4', 'tan': '#D2B48C',
        'teal': '#008080', 'thistle': '#D8BFD8', 'tomato': '#FF6347',
        'turquoise': '#40E0D0', 'violet': '#EE82EE', 'wheat': '#F5DEB3',
        'white': '#FFFFFF', 'whitesmoke': '#F5F5F5', 'yellow': '#FFFF00',
        'yellowgreen': '#9ACD32'
    }



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
        # from matplotlib import colors as mcolors
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
        # from matplotlib import colors as mcolors
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
