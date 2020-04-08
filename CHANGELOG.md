# Changelog

This changelog follows the specifications detailed in: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), although we have not yet reached a `1.0.0` release.

## Version 0.4.6 - Unreleased

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
