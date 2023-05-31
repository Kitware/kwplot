# Changelog

This changelog follows the specifications detailed in: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), although we have not yet reached a `1.0.0` release.

## Version 0.4.15 - Unreleased

### Added
* Experimental adjust-gui for normalization adjustments


## Version 0.4.14 - Released 2023-03-05

### Added
* Add `plot_points3d`
* Experimental top-level lazy attributes `plt` and `sns`, which call autoplt
  and autosns when invoked for the first time.
* New Modal CLI


### Fixed
* Minor issue in `plot_surface3d`


### Changed
* Tweaks to phantom legend
* Misc changes


## Version 0.4.13 - Released 2022-12-16

### Added
* Gifify script

### Fixed
* Fixed close figures with agg.


## Version 0.4.12 - Released 2022-09-27

### Added
* Add `kwplot.close_figures` and `kwplot.all_figures`.


### Changed
* Replaced deprecated pylab magic with matplotlib magic when in IPython.


## Version 0.4.11 - Released 2022-02-16


## Version 0.4.10 - Released 2021-11-05

### Added
* Add `show_ticks=False` keyword argument to `imshow`
* Add `phantom_legend` function
* Exposed `render_figure_to_image` function
* Added `__main__` script to show a normalized image.

## Version 0.4.9 - Released 2021-08-23

### Added
* `kwplot.autosns` for auto seaborn convenience.

## Version 0.4.8 - Released 2021-04-22

### Fixed
* Fixed potential crash in autompl on some systems with conflicting PyQt5 and
  python-opencv libraries. This involves falling back to agg if there *might*
  be a conflict. The environ KWPLOT_UNSAFE=1 can be set to use the old behavior


## Version 0.4.7 - Released 2020-08-26

### Added 
* Added "force" kwarg to autompl, which will change the backend and prevent
  future non-force autompl calls from changing the backend.

* BackendContext - a context manager for matplotlib backends. Primary purpose
  is to allow the user to ensure that the agg backend is used in certain
  places.

* `mpl_draw.draw_points` - draws 2d points

## Version 0.4.5 -

## Version 0.4.3

### Fixed
* Bugs in `plot_matrix`

## Version 0.4.2

### Changes
* Moved implementation of non-matplotlib drawing function to kwimage. This lets
  kwimage be independent of kwplot. These functions are still exposed in kwplot
  for backwards compatibility. This may change in the future.


## Version 0.4.0

### Changes
* Starting a changelog
* Tweaking build scripts and CI configurations. 
* Minor improvements to `multi_plot`
* `Color` no longer directly depends on `matplotlib`, might be ported to `kwimage` in the future.


## Version 0.3.0

* Changes at and before this version are undocumented
