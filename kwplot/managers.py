"""
Manager classes to help construct concise matplotlib figures.
"""
import ubelt as ub
import matplotlib as mpl
import matplotlib.text  # NOQA


class FigureManager:
    """
    Combines a figure finalizer, and label manager.

    SeeAlso:
        :class:`LabelManager`.
        :class:`FigureFinalizer`.
    """

    def __init__(figman, **kwargs):
        """
        Args:
            **kwargs: See :class:`FigureFinalizer`.
                dpi : float
                format : str
                metadata : dict
                bbox_inches : str
                pad_inches : float
                facecolor : color
                edgecolor : color
                backend : str
                orientation :
                papertype :
                transparent :
                bbox_extra_artists :
                pil_kwargs :
        """
        figman.finalizer = FigureFinalizer(**kwargs)
        figman.labels = LabelManager()
        figman.fig = None

    def figure(figman, *args, **kwargs):
        import kwplot
        fig = kwplot.figure(*args, **kwargs)
        figman.fig = fig
        return fig

    def finalize(self, fpath, fig=None, **kwargs):
        if fig is None:
            fig = self.fig
        final_fpath = self.finalizer.finalize(fig, fpath, **kwargs)
        return final_fpath

    def set_figtitle(self, *args, **kwargs):
        import kwplot
        kwplot.set_figtitle(*args, **kwargs, fig=self.fig)


class LabelManager:
    """
    Registers multiple ways to relabel text on axes

    CommandLine:
        xdoctest -m kwplot.managers LabelManager --show

    Example:
        >>> # xdoctest: +REQUIRES(module:pandas)
        >>> from kwplot.managers import *  # NOQA
        >>> import pandas as pd
        >>> import kwarray
        >>> rng = kwarray.ensure_rng(0)
        >>> models = ['category1', 'category2', 'category3']
        >>> data = pd.DataFrame([
        >>>     {
        >>>         'node.metrics.tpr': rng.rand(),
        >>>         'node.metrics.fpr': rng.rand(),
        >>>         'node.metrics.f1': rng.rand(),
        >>>         'node.param.model': rng.choice(models),
        >>>     } for _ in range(100)])
        >>> # xdoctest +REQUIRES(module:seaborn)
        >>> import kwplot
        >>> sns = kwplot.autosns()
        >>> fig = kwplot.figure(fnum=1, pnum=(1, 2, 1), doclf=1)
        >>> ax1 = sns.boxplot(data=data, x='node.param.model', y='node.metrics.f1')
        >>> ax1.set_title('My node.param.model boxplot')
        >>> kwplot.figure(fnum=1, pnum=(1, 2, 2))
        >>> ax2 = sns.scatterplot(data=data, x='node.metrics.tpr', y='node.metrics.f1', hue='node.param.model')
        >>> ax2.set_title('My node.param.model scatterplot')
        >>> ax = ax2
        >>> #
        >>> def mapping(text):
        >>>     text = text.replace('node.param.', '')
        >>>     text = text.replace('node.metrics.', '')
        >>>     return text
        >>> #
        >>> self = LabelManager(mapping)
        >>> self.add_mapping({'category2': 'FOO', 'category3': 'BAR'})
        >>> #fig.canvas.draw()
        >>> #
        >>> self.relabel(ax=ax1)
        >>> self.relabel(ax=ax2)
        >>> fig.canvas.draw()
        >>> kwplot.show_if_requested()
    """

    def __init__(self, mapping=None):
        self._dict_mapper = {}
        self._func_mappers = []
        self.add_mapping(mapping)

    def copy(self):
        new = self.__class__()
        new.add_mapping(self._dict_mappem.copy())
        for m in self._func_mappers:
            new.add_mapping(m)
        return new

    def add_mapping(self, mapping):
        if mapping is not None:
            if callable(mapping):
                self._func_mappers.append(mapping)
            elif hasattr(mapping, 'get'):
                self._dict_mapper.update(mapping)
                self._dict_mapper.update(ub.udict(mapping).map_keys(str))
        return self

    def update(self, dict_mapping):
        self._dict_mapper.update(dict_mapping)
        self._dict_mapper.update(ub.udict(dict_mapping).map_keys(str))
        return self

    def _modify_text(self, text: str):
        # Handles strings, which we call text by convention, but that is
        # confusing here.
        new_text = text
        mapper = self._dict_mapper
        new_text = mapper.get(str(new_text), new_text)
        new_text = mapper.get(new_text, new_text)
        for mapper in self._func_mappers:
            new_text = mapper(new_text)
        return new_text

    def _modify_labels(self, label: mpl.text.Text):
        # Handles labels, which are mpl Text objects
        text = label.get_text()
        new_text = self._modify_text(text)
        label.set_text(new_text)
        return label

    def _modify_legend(self, legend):
        leg_title = legend.get_title()
        if isinstance(leg_title, str):
            new_leg_title = self._modify_text(leg_title)
            legend.set_text(new_leg_title)
        else:
            self._modify_labels(leg_title)
        for label in legend.texts:
            self._modify_labels(label)

    def relabel_yticks(self, ax=None):
        old_ytick_labels = ax.get_yticklabels()
        new_yticklabels = [self._modify_labels(label) for label in old_ytick_labels]
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(new_yticklabels)

    def relabel_xticks(self, ax=None):
        # Set xticks and yticks first before setting tick labels
        # https://stackoverflow.com/questions/63723514/userwarning-fixedformatter-should-only-be-used-together-with-fixedlocator
        # print(f'new_xlabel={new_xlabel}')
        # print(f'new_ylabel={new_ylabel}')
        # print(f'old_xticks={old_xticks}')
        # print(f'old_yticks={old_yticks}')
        # print(f'old_xtick_labels={old_xtick_labels}')
        # print(f'old_ytick_labels={old_ytick_labels}')
        # print(f'new_xticklabels={new_xticklabels}')
        # print(f'new_yticklabels={new_yticklabels}')
        old_xtick_labels = ax.get_xticklabels()
        new_xticklabels = [self._modify_labels(label) for label in old_xtick_labels]

        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(new_xticklabels)

    def _coerce_axes(self, ax=None):
        if ax is None:
            import kwplot
            ax = kwplot.plt.gca()
        return ax

    def _coerce_axis(self, axis, ax=None):
        """
        Get x or y axis
        """
        if isinstance(axis, str):
            ax = self._coerce_axes(ax)
            if axis == 'x':
                return ax.xaxis
            elif axis == 'y':
                return ax.yaxis
            else:
                raise KeyError(axis)
        return axis

    # def _get_axis_attr(self, axis, attr, ax=None):
    #     """
    #     Get x or y axis
    #     """
    #     if isinstance(axis, str):
    #         ax = self._coerce_axes(ax)
    #         assert axis in 'xy'
    #         func = getattr(ax, 'get_{axis}{attr}')
    #     return axis

    def relabel_axes_labels(self, ax=None):
        old_xlabel = ax.get_xlabel()
        old_ylabel = ax.get_ylabel()
        old_title = ax.get_title()

        new_xlabel = self._modify_text(old_xlabel)
        new_ylabel = self._modify_text(old_ylabel)
        new_title = self._modify_text(old_title)

        ax.set_xlabel(new_xlabel)
        ax.set_ylabel(new_ylabel)
        ax.set_title(new_title)

    def relabel_legend(self, ax=None):
        if ax.legend_ is not None:
            self._modify_legend(ax.legend_)

    def relabel(self, ax=None, ticks=True, axes_labels=True, legend=True):
        if axes_labels:
            self.relabel_axes_labels(ax)
        if ticks:
            self.relabel_xticks(ax)
            self.relabel_yticks(ax)
        if legend:
            self.relabel_legend(ax)

    def force_integer_xticks(self, ax=None):
        ax = self._coerce_axes(ax)
        axis = ax.xaxis
        self.force_integer_ticks(axis)

    def force_integer_yticks(self, ax=None):
        ax = self._coerce_axes(ax)
        axis = ax.xaxis
        self.force_integer_ticks(axis)

    def force_integer_ticks(self, axis, ax=None, method='ticker', hack_labels=False):
        """
        References:
            https://stackoverflow.com/questions/30914462/how-to-force-integer-tick-labels

        Example:
            >>> import kwplot
            >>> from kwplot.managers import *  # NOQA
            >>> import numpy as np
            >>> fig = kwplot.figure()
            >>> ax = fig.gca()
            >>> ax.set_xlim(0, 22.2)
            >>> ax.set_ylim(0, 21.1)
            >>> self = LabelManager()
            >>> xticks = ax.get_xticks()
            >>> assert not np.all(xticks.round() == xticks), 'ticks are not integers by default'
            >>> self.force_integer_ticks('x')
            >>> xticks = ax.get_xticks()
            >>> assert np.all(xticks.round() == xticks), 'ticks should be integers now'
        """
        axis = self._coerce_axis(axis)
        if method == 'maxn':
            from matplotlib.ticker import MaxNLocator
            axis.set_major_locator(MaxNLocator(integer=True))
        elif method == 'ticker':
            import matplotlib.ticker as tck
            offset = 0.0
            try:
                axis.set_major_locator(tck.MultipleLocator(offset=offset))
            except TypeError:
                if offset != 0.0:
                    raise RuntimeError('update matplotlib to use a nonzero offset')
                axis.set_major_locator(tck.MultipleLocator())
            # axis.set_major_locator(tck.MultipleLocator())
        else:
            raise KeyError(method)

        if hack_labels:
            new_labels = []
            needs_fix = 0
            for label in axis.get_ticklabels():
                print(f'label={label}')
                text = label.get_text()
                if '.' in text:
                    text = str(int(float(text)))
                    label.set_text(text)
                    needs_fix = 1
                new_labels.append(label)
            if needs_fix:
                axis.set_ticklabels(new_labels)

    def __call__(self, ax=None):
        self.relabel(ax)


class FigureFinalizer(ub.NiceRepr):
    """
    Helper for defining where and how figures will be saved on disk.

    Known Parameters:
        dpi : float
        format : str
        metadata : dict
        bbox_inches : str
        pad_inches : float
        facecolor : color
        edgecolor : color
        backend : str
        orientation :
        papertype :
        transparent :
        bbox_extra_artists :
        pil_kwargs :

    Example:
        self = FigureFinalizer()
        print('self = {}'.format(ub.urepr(self, nl=1)))
        self.update(dpi=300)

    """

    def __init__(
        self,
        dpath='.',
        size_inches=None,
        cropwhite=True,
        tight_layout=True,
        verbose=0,
        **kwargs
    ):
        locals_ = ub.udict(locals())
        locals_ -= {'self', 'kwargs'}
        locals_.update(kwargs)
        self.verbose = verbose
        self.update(locals_)

    def __nice__(self):
        return ub.urepr(self.__dict__)

    def copy(self):
        """
        Create a copy of this object.
        """
        new = self.__class__(**self.__dict__)
        return new

    def update(self, *args, **kwargs):
        """
        Modify this config
        """
        self.__dict__.update(*args, **kwargs)

    def finalize(self, fig, fpath, **kwargs):
        """
        Sets the figure properties, like size, tight layout, etc, writes to
        disk, and then crops the whitespace out.

        Args:
            fig (matplotlib.figure.Figure): figure to safe

            fpath (str | PathLike): where to save the figure image

            **kwargs: overrides this config for this finalize only
        """
        config = ub.udict(self.__dict__) | kwargs

        dpath = ub.Path(config['dpath']).ensuredir()
        final_fpath = dpath / fpath
        if self.verbose:
            from kwutil.util_rich import rich_print
            rich_print(f'Write: {final_fpath}')
        savekw = {}
        if config.get('dpi', None) is not None:
            savekw['dpi'] = config['dpi']
            # fig.set_dpi(savekw['dpi'])
        if config['size_inches'] is not None:
            fig.set_size_inches(config['size_inches'])
        if config['tight_layout'] is not None:
            fig.tight_layout()
        # TODO: could save to memory and then write as an image
        fig.savefig(final_fpath, **savekw)
        if self.cropwhite:
            cropwhite_ondisk(final_fpath)
        return final_fpath

    def __call__(self, fig, fpath, **kwargs):
        """
        Alias for finalize
        """
        return self.finalize(fig, fpath, **kwargs)


class ArtistManager:
    """
    Accumulates artist collections (e.g. lines, patches, ellipses) the user is
    interested in drawing so we can draw them efficiently.

    References:
        https://matplotlib.org/stable/api/collections_api.html
        https://matplotlib.org/stable/gallery/shapes_and_collections/ellipse_collection.html
        https://stackoverflow.com/questions/32444037/how-can-i-plot-many-thousands-of-circles-quickly

    Example:
        >>> # xdoctest: +REQUIRES(module:seaborn)
        >>> from kwplot.managers import *  # NOQA
        >>> import kwplot
        >>> sns = kwplot.autosns()
        >>> fig = kwplot.figure(fnum=1)
        >>> self = ArtistManager()
        >>> import kwimage
        >>> points = kwimage.Polygon.star().data['exterior'].data
        >>> self.add_linestring(points)
        >>> ax = fig.gca()
        >>> self.add_to_axes(ax)
        >>> ax.relim()
        >>> ax.set_xlim(-1, 1)
        >>> ax.set_ylim(-1, 1)
        >>> kwplot.show_if_requested()

    Example:
        >>> # xdoctest: +REQUIRES(module:seaborn)
        >>> from kwplot.managers import *  # NOQA
        >>> import numpy as np
        >>> import kwplot
        >>> sns = kwplot.autosns()
        >>> fig = kwplot.figure(fnum=1)
        >>> self = ArtistManager()
        >>> import kwimage
        >>> points = kwimage.Polygon.star().data['exterior'].data
        >>> y = 1
        >>> self.add_linestring([(0, y), (1, y)], color='kitware_blue')
        >>> y = 2
        >>> self.add_linestring([(0, y), (1, y)], color='kitware_green')
        >>> y = 3
        >>> self.add_circle((0, y), r=.1, color='kitware_darkgreen')
        >>> self.add_circle((0.5, y), r=.1, color='kitware_darkblue')
        >>> self.add_circle((0.2, y), r=.1, color='kitware_darkblue')
        >>> self.add_circle((1.0, y), r=.1, color='kitware_darkblue')
        >>> self.add_ellipse((0.2, 1), .1, .2, angle=10, color='kitware_gray')
        >>> self.add_linestring([(0, y), (1, y)], color='kitware_blue')
        >>> y = 4
        >>> self.add_linestring([(0, y), (1, y)], color='kitware_blue')
        >>> self.add_circle_marker((0, y), r=10, color='kitware_darkgreen')
        >>> self.add_circle_marker((0.5, y), r=10, color='kitware_darkblue')
        >>> self.add_circle_marker((0.2, y), r=10, color='kitware_darkblue')
        >>> self.add_circle_marker((1.0, y), r=10, color='kitware_darkblue')
        >>> self.add_ellipse_marker((0.2, 2), 10, 20, angle=10, color='kitware_gray')
        >>> self.add_linestring(np.array([
        ...     (0.2, 0.5),
        ...     (0.45, 1.6),
        ...     (0.62, 2.3),
        ...     (0.82, 4.9),
        >>> ]), color='kitware_yellow')
        >>> self.add_to_axes()
        >>> ax = fig.gca()
        >>> ax.set_xlim(0, 1)
        >>> ax.set_ylim(0, 5)
        >>> ax.autoscale_view()
        >>> kwplot.show_if_requested()
    """

    def __init__(self):
        self.group_to_line_segments = ub.ddict(list)
        self.group_to_patches = ub.ddict(lambda : ub.ddict(list))
        self.group_to_ellipse_markers = ub.ddict(lambda: {
            'xy': [],
            'rx': [],
            'ry': [],
            'angle': [],
        })
        self.group_to_attrs = {}

    def _normalize_attrs(self, attrs):
        import kwimage
        attrs = ub.udict(attrs)
        if 'color' in attrs:
            attrs['color'] = kwimage.Color.coerce(attrs['color']).as01()
        if 'hashid' in attrs:
            attrs = attrs - {'hashid'}
        hashid = ub.hash_data(sorted(attrs.items()))[0:8]
        return hashid, attrs

    def plot(self, xs, ys, **attrs):
        """
        Alternative way to add lines
        """
        import numpy as np
        ys = [ys] if not ub.iterable(ys) else ys
        xs = [xs] if not ub.iterable(xs) else xs
        if len(ys) == 1 and len(xs) > 1:
            ys = ys * len(xs)
        if len(xs) == 1 and len(ys) > 1:
            xs = xs * len(ys)
        points = np.array(list(zip(xs, ys)))
        self.add_linestring(points, **attrs)

    def add_linestring(self, points, **attrs):
        """
        Prepares points to be added in a LineCollection

        Args:
            points (List[Tuple[float, float]] | ndarray):
                an Nx2 set of ordered points

            **attrs: color,

        NOTE:
            perhaps allow adding markers based on ax.scatter?
        """
        hashid, attrs = self._normalize_attrs(attrs)
        self.group_to_line_segments[hashid].append(points)
        self.group_to_attrs[hashid] = attrs

    def add_ellipse(self, xy, rx, ry, angle=0, **attrs):
        """
        Real ellipses in dataspace
        """
        hashid, attrs = self._normalize_attrs(attrs)
        ell = mpl.patches.Ellipse(xy, rx, ry, angle=angle, **attrs)
        self.group_to_patches[hashid]['ellipse'].append(ell)
        self.group_to_attrs[hashid] = attrs

    def add_circle(self, xy, r, **attrs):
        """
        Real ellipses in dataspace
        """
        hashid, attrs = self._normalize_attrs(attrs)
        ell = mpl.patches.Circle(xy, r, **attrs)
        self.group_to_patches[hashid]['circle'].append(ell)
        self.group_to_attrs[hashid] = attrs

    def add_ellipse_marker(self, xy, rx, ry, angle=0, color=None, **attrs):
        """
        Args:
            xy : center
            rx : radius in the first axis (size is in points, i.e. same way plot markers are sized)
            ry : radius in the second axis
            angle (float): The angles of the first axes, degrees CCW from the x-axis.

        """
        import numpy as np
        import kwimage
        if color is not None:
            if 'edgecolors' not in attrs:
                attrs['edgecolors'] = kwimage.Color.coerce(color).as01()
            if 'facecolors' not in attrs:
                attrs['facecolors'] = kwimage.Color.coerce(color).as01()

        hashid, attrs = self._normalize_attrs(attrs)
        cols = self.group_to_ellipse_markers[hashid]

        xy = np.array(xy)
        if len(xy.shape) == 1:
            assert xy.shape[0] == 2
            xy = xy[None, :]
        elif len(xy.shape) == 2:
            assert xy.shape[1] == 2
        else:
            raise ValueError

        # Broadcast shapes
        rx = [rx] if not ub.iterable(rx) else rx
        ry = [ry] if not ub.iterable(ry) else ry
        angle = [angle] if not ub.iterable(angle) else angle
        nums = list(map(len, (xy, rx, ry, angle)))
        if not ub.allsame(nums):
            new_n = max(nums)
            for n in nums:
                assert n == 1 or n == new_n
            if len(xy) == 1:
                xy = np.repeat(xy, new_n, axis=0)
            if len(rx) == 1:
                rx = np.repeat(rx, new_n, axis=0)
            if len(ry) == 1:
                ry = np.repeat(ry, new_n, axis=0)
            if len(angle) == 1:
                ry = np.repeat(ry, new_n, axis=0)

        cols['xy'].append(xy)
        cols['rx'].append(rx)
        cols['ry'].append(ry)
        cols['angle'].append(angle)
        self.group_to_attrs[hashid] = attrs

    def add_circle_marker(self, xy, r, **attrs):
        """
        Args:
            xy (List[Tuple[float, float]] | ndarray):
                an Nx2 set of circle centers
            r (List[float] | ndarray):
                an Nx1 set of circle radii
        """
        self.add_ellipse_marker(xy, rx=r, ry=r, angle=0, **attrs)

    def build_collections(self, ax=None):
        import numpy as np
        collections = []
        for hashid, segments in self.group_to_line_segments.items():
            attrs = self.group_to_attrs[hashid]
            collection = mpl.collections.LineCollection(segments, **attrs)
            collections.append(collection)

        for hashid, type_to_patches in self.group_to_patches.items():
            attrs = self.group_to_attrs[hashid]
            for ptype, patches in type_to_patches.items():
                collection = mpl.collections.PatchCollection(patches, **attrs)
                collections.append(collection)

        for hashid, cols in self.group_to_ellipse_markers.items():
            attrs = self.group_to_attrs[hashid] - {'hashid'}
            xy = np.concatenate(cols['xy'], axis=0)
            rx = np.concatenate(cols['rx'], axis=0)
            ry = np.concatenate(cols['ry'], axis=0)
            angles = np.concatenate(cols['angle'], axis=0)
            collection = mpl.collections.EllipseCollection(
                widths=rx, heights=ry, offsets=xy, angles=angles,
                units='points',
                # units='x',
                # units='xy',
                transOffset=ax.transData,
                **attrs
            )
            # collection.set_transOffset(ax.transData)
            collections.append(collection)

        return collections

    def add_to_axes(self, ax=None):
        import kwplot
        if ax is None:
            plt = kwplot.autoplt()
            ax = plt.gca()

        collections = self.build_collections(ax=ax)
        for collection in collections:
            ax.add_collection(collection)

    def bounds(self):
        import numpy as np
        all_lines = []
        for segments in self.group_to_line_segments.values():
            for lines in segments:
                lines = np.array(lines)
                all_lines.append(lines)

        all_coords = np.concatenate(all_lines, axis=0)
        import pandas as pd
        flags = pd.isnull(all_coords)
        all_coords[flags] = np.nan
        all_coords = all_coords.astype(float)

        minx, miny = np.nanmin(all_coords, axis=0) if len(all_coords) else 0
        maxx, maxy = np.nanmax(all_coords, axis=0) if len(all_coords) else 1
        ltrb = minx, miny, maxx, maxy
        return ltrb

    def setlims(self, ax=None):
        import kwplot
        if ax is None:
            plt = kwplot.autoplt()
            ax = plt.gca()

        from kwimage.structs import _generic
        minx, miny, maxx, maxy = self.bounds()
        _generic._setlim(minx, miny, maxx, maxy, 1.1, ax=ax)
        # ax.set_xlim(minx, maxx)
        # ax.set_ylim(miny, maxy)


class Palette(ub.udict):
    """
    Dictionary subclass that maps a label to a particular color.

    Explicit colors per label can be given, but for other unspecified labels we
    attempt to generate a distinct color.

    Example:
        >>> from kwplot.managers import *  # NOQA
        >>> self1 = Palette()
        >>> self1.add_labels(labels=['a', 'b'])
        >>> self1.update({'foo': 'blue'})
        >>> self1.update(['bar', 'baz'])
        >>> self2 = Palette.coerce({'foo': 'blue'})
        >>> self2.update(['a', 'b', 'bar', 'baz'])
        >>> self1 = self1.sorted_keys()
        >>> self2 = self2.sorted_keys()
        >>> # xdoctest: +REQUIRES(env:PLOTTING_DOCTESTS)
        >>> import kwplot
        >>> kwplot.autoplt()
        >>> canvas1 = self1.make_legend_img()
        >>> canvas2 = self2.make_legend_img()
        >>> canvas = kwimage.stack_images([canvas1, canvas2])
        >>> kwplot.imshow(canvas)
    """

    @classmethod
    def coerce(cls, data):
        self = cls()
        self.update(data)
        return self

    def update(self, other):
        if isinstance(other, dict):
            self.add_labels(label_to_color=other)
        else:
            self.add_labels(labels=other)

    def add_labels(self, label_to_color=None, labels=None):
        """
        Forces particular labels to take a specific color and then chooses
        colors for any other unspecified label.

        Args:
            label_to_color (Dict[str, Any] | None): mapping to colors that are forced
            labels (List[str] | None): new labels that should take distinct colors
        """
        import kwimage
        # Given an existing set of colors, add colors to things without it.
        if label_to_color is None:
            label_to_color = {}
        if labels is None:
            labels = []

        # Determine which labels in the input mapping are not explicitly given
        specified = {k: kwimage.Color.coerce(v).as01()
                     for k, v in label_to_color.items() if v is not None}
        unspecified = ub.oset(label_to_color.keys()) - specified

        # Merge specified colors into this pallet
        super().update(specified)

        # Determine which labels need a color.
        new_labels = (unspecified | ub.oset(labels)) - set(self.keys())
        num_new = len(new_labels)
        if num_new:
            existing_colors = list(self.values())
            new_colors = kwimage.Color.distinct(num_new,
                                                existing=existing_colors,
                                                legacy=False)
            new_label_to_color = dict(zip(new_labels, new_colors))
            super().update(new_label_to_color)

    def make_legend_img(self, dpi=300, **kwargs):
        import kwplot
        legend = kwplot.make_legend_img(self, dpi=dpi, **kwargs)
        return legend

    def sorted_keys(self):
        return self.__class__(super().sorted_keys())

    def reorder(self, head=None, tail=None):
        if head is None:
            head = []
        if tail is None:
            tail = []
        head_part = self.subdict(head)
        tail_part = self.subdict(tail)
        end_keys = (head_part.keys() | tail_part.keys())
        mid_part = self - end_keys
        new = self.__class__(head_part | mid_part | tail_part)
        return new

    """
    # Do we want to offer standard pallets for small datas

    # if num_regions < 10:
    #     colors = sns.color_palette(n_colors=num_regions)
    # else:
    #     colors = kwimage.Color.distinct(num_regions, legacy=False)
    #     colors = [kwimage.Color.coerce(c).adjust(saturate=-0.3, lighten=-0.1).as01()
    #               for c in kwimage.Color.distinct(num_regions, legacy=False)]
    """


class PaletteManager:
    """
    Manages colors that should be kept constant across different labels for
    multiple parameters.

    self = PaletteManager()
    self.update_params('region_id', {'region1': 'red'})
    """
    def __init__(self):
        self.param_to_palette = {}


def cropwhite_ondisk(fpath):
    import kwimage
    from kwplot.mpl_make import crop_border_by_color
    imdata = kwimage.imread(fpath)
    imdata = crop_border_by_color(imdata)
    kwimage.imwrite(fpath, imdata)


def extract_legend(ax):
    """
    Creates a new figure that contains the original legend.
    """
    # ax.get_legend().remove()
    orig_legend = ax.get_legend()
    if orig_legend is None:
        raise RuntimeError('no legend')
    orig_legend_title = orig_legend.get_title().get_text()
    legend_handles = ax.get_legend_handles_labels()

    # fnum = 321
    import kwplot
    fig_onlylegend = kwplot.figure(
        fnum=str(ax.figure.number) + '_onlylegend', doclf=1)
    new_ax = fig_onlylegend.gca()
    new_ax.axis('off')
    new_ax.legend(*legend_handles, title=orig_legend_title,
                            loc='lower center')
    return new_ax


def fix_matplotlib_dates(dates, format='mdate'):
    """

    Args:
        dates (List[None | Coerceble[datetime]]):
            input dates to fixup

        format (str):
            can be mdate for direct matplotlib usage or datetime for seaborn usage.

    Note:
        seaborn seems to do just fine with timestamps...
        todo:
            add regular matplotlib test for a real demo of where this is useful

    Example:
        >>> # xdoctest: +REQUIRES(module:kwutil)
        >>> from kwplot.managers import *  # NOQA
        >>> from kwutil.util_time import coerce_datetime
        >>> from kwutil.util_time import coerce_timedelta
        >>> import pandas as pd
        >>> import numpy as np
        >>> delta = coerce_timedelta('1 day')
        >>> n = 100
        >>> min_date = coerce_datetime('2020-01-01').timestamp()
        >>> max_date = coerce_datetime('2021-01-01').timestamp()
        >>> from kwarray.distributions import Uniform
        >>> distri = Uniform(min_date, max_date)
        >>> timestamps = distri.sample(n)
        >>> timestamps[np.random.rand(n) > 0.5] = np.nan
        >>> dates = list(map(coerce_datetime, timestamps))
        >>> scores = np.random.rand(len(dates))
        >>> table = pd.DataFrame({
        >>>     'isodates': [None if d is None else d.isoformat() for d in dates],
        >>>     'dates': dates,
        >>>     'timestamps': timestamps,
        >>>     'scores': scores
        >>> })
        >>> table['fixed_dates'] = fix_matplotlib_dates(table.dates, format='datetime')
        >>> table['fixed_timestamps'] = fix_matplotlib_dates(table.timestamps, format='datetime')
        >>> table['fixed_isodates'] = fix_matplotlib_dates(table.isodates, format='datetime')
        >>> table['mdate_dates'] = fix_matplotlib_dates(table.dates, format='mdate')
        >>> table['mdate_timestamps'] = fix_matplotlib_dates(table.timestamps, format='mdate')
        >>> table['mdate_isodates'] = fix_matplotlib_dates(table.isodates, format='mdate')
        >>> # xdoctest: +REQUIRES(env:PLOTTING_DOCTESTS)
        >>> import kwplot
        >>> sns = kwplot.autosns()
        >>> pnum_ = kwplot.PlotNums(nSubplots=8)
        >>> ax = kwplot.figure(fnum=1, doclf=1)
        >>> for key in table.columns.difference({'scores'}):
        >>>     ax = kwplot.figure(fnum=1, doclf=0, pnum=pnum_()).gca()
        >>>     sns.scatterplot(data=table, x=key, y='scores', ax=ax)
        >>>     if key.startswith('mdate_'):
        >>>         # TODO: make this formatter fixup work better.
        >>>         import matplotlib.dates as mdates
        >>>         ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        >>>         ax.xaxis.set_major_locator(mdates.DayLocator(interval=90))
    """
    from kwutil import util_time
    import matplotlib.dates as mdates
    new = []
    for d in dates:
        n = util_time.coerce_datetime(d)
        if n is not None:
            if format == 'mdate':
                n = mdates.date2num(n)
            elif format == 'datetime':
                ...
            else:
                raise KeyError(format)
        new.append(n)
    return new


def fix_matplotlib_timedeltas(deltas):
    from kwutil import util_time
    # import matplotlib.dates as mdates
    new = []
    for d in deltas:
        if d is None:
            n = None
        else:
            try:
                n = util_time.coerce_timedelta(d)
            except util_time.TimeValueError:
                n = None
        # if n is not None:
        #     n = mdates.num2timedelta(n)
        new.append(n)
    return new
