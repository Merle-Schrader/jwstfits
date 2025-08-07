.. jwstfits documentation master file, created by
   sphinx-quickstart on Thu Aug  7 13:38:31 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

jwstfits documentation
======================
.. jwstfits documentation master file

A small Python module to streamline working with JWST pipeline FITS outputs.
It enables quick inspection, data extraction, and unit conversion without having to dig through HDUs.

.. contents:: Table of Contents
   :depth: 2

Functionality
-------------
- Load and inspect FITS files (tree, head, columns).
- Extract 1D and time-series spectra from x1d/x1dints files.
- Convert units from Jy to W/m²/μm [others coming soon].
- [Coming soon] MIRI and other JWST instrument support.
- [Coming soon] First look at the data: simple plotting options.

Contributing
------------
We welcome contributors!

If you use other JWST instrument data and would like to add them (e.g., NIRCam, MIRI IFU, etc.), please submit an issue or pull request on GitHub:
https://github.com/Merle-Schrader/jwstfits

Coming Soon
-----------
- MIRI MRS and LRS data support
- Plotting options to allow first look at the data

API Reference
-------------
.. autofunction:: jwstfits.nirspec.x1d
.. autofunction:: jwstfits.nirspec.x1dints
.. autofunction:: jwstfits.utils.columns
.. autofunction:: jwstfits.utils.tree
.. autofunction:: jwstfits.utils.head

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   jwstfits