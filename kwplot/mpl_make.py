# -*- coding: utf-8 -*-
"""
DEPRECATED: use kwimage versions instead

Functions used to explicitly make images as ndarrays using mpl/cv2 utilities
"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['make_heatmask', 'make_vector_field', 'make_orimask']

from kwimage import make_heatmask, make_vector_field, make_orimask  # NOQA
