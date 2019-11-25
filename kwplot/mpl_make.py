# -*- coding: utf-8 -*-
"""
Functions used to explicitly make images as ndarrays using mpl/cv2 utilities
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from kwimage import make_heatmask, make_vector_field, make_orimask  # NOQA

# import numpy as np
# def make_heatmask(probs, cmap='plasma', with_alpha=1.0, space='rgb',
#                   dsize=None):
#     """
#     Colorizes a single-channel intensity mask (with an alpha channel)

#     Args:
#         probs (ndarray): 2D probability map with values between 0 and 1
#         cmap (str): mpl colormap
#         with_alpha (float): between 0 and 1, uses probs as the alpha multipled
#             by this number.
#         space (str): output colorspace
#         dsize (tuple): if not None, then output is resized to W,H=dsize

#     SeeAlso:
#         kwimage.overlay_alpha_images

#     Example:
#         >>> probs = np.tile(np.linspace(0, 1, 10), (10, 1))
#         >>> heatmask = make_heatmask(probs, with_alpha=0.8, dsize=(100, 100))
#         >>> # xdoc: +REQUIRES(--show)
#         >>> import kwplot
#         >>> kwplot.imshow(heatmask, fnum=1, doclf=True, colorspace='rgb')
#         >>> kwplot.show_if_requested()
#     """
#     import matplotlib as mpl
#     import kwimage
#     import matplotlib.cm  # NOQA
#     assert len(probs.shape) == 2
#     cmap_ = mpl.cm.get_cmap(cmap)
#     probs = kwimage.ensure_float01(probs)
#     heatmask = cmap_(probs).astype(np.float32)
#     heatmask = kwimage.convert_colorspace(heatmask, 'rgba', space, implicit=True)
#     if with_alpha is not False and with_alpha is not None:
#         heatmask[:, :, 3] = (probs * with_alpha)  # assign probs to alpha channel
#     if dsize is not None:
#         import cv2
#         heatmask = cv2.resize(heatmask, tuple(dsize), interpolation=cv2.INTER_NEAREST)
#     return heatmask


# def make_orimask(radians, mag=None, alpha=1.0):
#     """
#     Makes a colormap in HSV space where the orientation changes color and mag
#     changes the saturation/value.

#     Args:
#         radians (ndarray): orientation in radians
#         mag (ndarray): magnitude (must be normalized between 0 and 1)
#         alpha (float | ndarray):
#             if False or None, then the image is returned without alpha
#             if a float, then mag is scaled by this and used as the alpha channel
#             if an ndarray, then this is explicilty set as the alpha channel

#     Returns:
#         ndarray[float32]: an rgb / rgba image in 01 space

#     SeeAlso:
#         kwimage.overlay_alpha_images

#     Example:
#         >>> x, y = np.meshgrid(np.arange(64), np.arange(64))
#         >>> dx, dy = x - 32, y - 32
#         >>> radians = np.arctan2(dx, dy)
#         >>> mag = np.sqrt(dx ** 2 + dy ** 2)
#         >>> orimask = make_orimask(radians, mag)
#         >>> # xdoc: +REQUIRES(--show)
#         >>> import kwplot
#         >>> kwplot.imshow(orimask, fnum=1, doclf=True, colorspace='rgb')
#         >>> kwplot.show_if_requested()
#     """
#     import matplotlib as mpl
#     import matplotlib.cm  # NOQA
#     TAU = np.pi * 2
#     # Map radians to 0 to 1
#     ori01 = (radians % TAU) / TAU
#     cmap_ = mpl.cm.get_cmap('hsv')
#     color_rgb = cmap_(ori01)[..., 0:3].astype(np.float32)
#     if mag is not None:
#         import kwimage
#         if mag.max() > 1:
#             mag = mag / mag.max()
#         color_hsv = kwimage.convert_colorspace(color_rgb, 'rgb', 'hsv')
#         color_hsv[..., 1:3] = mag[..., None]
#         color_rgb = kwimage.convert_colorspace(color_hsv, 'hsv', 'rgb')
#     else:
#         mag = 1
#     orimask = np.array(color_rgb, dtype=np.float32)

#     if isinstance(alpha, np.ndarray):
#         # Alpha specified as explicit numpy array
#         orimask = kwimage.ensure_alpha_channel(orimask)
#         orimask[:, :, 3] = alpha
#     elif alpha is not False and alpha is not None:
#         orimask = kwimage.ensure_alpha_channel(orimask)
#         orimask[:, :, 3] = mag * alpha
#     return orimask


# def make_vector_field(dx, dy, stride=1, thresh=0.0, scale=1.0, alpha=1.0,
#                       color='red', thickness=1, tipLength=0.1, line_type='aa'):
#     """
#     Create an image representing a 2D vector field.

#     Args:
#         dx (ndarray): grid of vector x components
#         dy (ndarray): grid of vector y components
#         stride (int): sparsity of vectors
#         thresh (float): only plot vectors with magnitude greater than thres
#         scale (float): multiply magnitude for easier visualization
#         alpha (float): alpha value for vectors. Non-vector regions receive 0
#             alpha (if False, no alpha channel is used)
#         color (str | tuple | kwplot.Color): RGB color of the vectors
#         thickness (int, default=1): thickness of arrows
#         tipLength (float, default=0.1): fraction of line length
#         line_type (int): either cv2.LINE_4, cv2.LINE_8, or cv2.LINE_AA

#     Returns:
#         ndarray[float32]: vec_img: an rgb/rgba image in 0-1 space

#     SeeAlso:
#         kwimage.overlay_alpha_images

#     Example:
#         >>> x, y = np.meshgrid(np.arange(512), np.arange(512))
#         >>> dx, dy = x - 256.01, y - 256.01
#         >>> radians = np.arctan2(dx, dy)
#         >>> mag = np.sqrt(dx ** 2 + dy ** 2)
#         >>> dx, dy = dx / mag, dy / mag
#         >>> img = make_vector_field(dx, dy, stride=10, scale=10, alpha=False)
#         >>> # xdoctest: +REQUIRES(--show)
#         >>> import kwplot
#         >>> kwplot.autompl()
#         >>> kwplot.imshow(img)
#         >>> kwplot.show_if_requested()
#     """
#     import cv2
#     import kwplot
#     import kwimage
#     color = kwplot.Color(color).as255('rgb')
#     vecmask = np.zeros(dx.shape + (3,), dtype=np.uint8)

#     line_type_lookup = {'aa': cv2.LINE_AA}
#     line_type = line_type_lookup.get(line_type, line_type)

#     x_grid = np.arange(0, dx.shape[1], 1)
#     y_grid = np.arange(0, dy.shape[0], 1)
#     # Vector locations and directions
#     X, Y = np.meshgrid(x_grid, y_grid)
#     U, V = dx, dy

#     XYUV = [X, Y, U, V]

#     # stride the points
#     if stride is not None and stride > 1:
#         XYUV = [a[::stride, ::stride] for a in XYUV]

#     # flatten the points
#     XYUV = [a.ravel() for a in XYUV]

#     # Filter out points with low magnitudes
#     if thresh is not None and thresh > 0:
#         M = np.sqrt((XYUV[2] ** 2) + (XYUV[3] ** 2)).ravel()
#         XYUV = np.array(XYUV)
#         flags = M > thresh
#         XYUV = [a[flags] for a in XYUV]

#     # Adjust vector magnitude for visibility
#     if scale is not None:
#         XYUV[2] *= scale
#         XYUV[3] *= scale

#     for (x, y, u, v) in zip(*XYUV):
#         pt1 = (int(x), int(y))
#         pt2 = tuple(map(int, map(np.round, (x + u, y + v))))
#         cv2.arrowedLine(vecmask, pt1, pt2, color=color, thickness=thickness,
#                         tipLength=tipLength,
#                         line_type=line_type)

#     vecmask = kwimage.ensure_float01(vecmask)
#     if isinstance(alpha, np.ndarray):
#         # Alpha specified as explicit numpy array
#         vecmask = kwimage.ensure_alpha_channel(vecmask)
#         vecmask[:, :, 3] = alpha
#     elif alpha is not False and alpha is not None:
#         # Alpha specified as a scale factor
#         vecmask = kwimage.ensure_alpha_channel(vecmask)
#         # vecmask[:, :, 3] = (vecmask[:, :, 0:3].sum(axis=2) > 0) * alpha
#         vecmask[:, :, 3] = vecmask[:, :, 0:3].sum(axis=2) * alpha
#     return vecmask
