<p align="center">
  <img src="docs/_static/jwstfits2.png" alt="jwstfits logo" width="200"/>
</p>

# jwstfits

A small utility module for quick inspection and data extraction from JWST `.fits` files. Currently supports NIRSpec `x1d` and `x1dints` outputs. MIRI LRS and MRS `s3d` and `x1d` support coming soon...

## Features

- View FITS structure (`tree`, `head`, `columns`)
- Extract wavelength, flux, and error from 1D or time-series spectra
- Handle unit conversion (e.g. from `Jy` to `W/m²/μm`; more being added.)
- Clip wavelength ranges or outliers
- Output as arrays, pandas DataFrames, or dict-style cubes

## Units

By default, native JWST pipeline units (typically wavelength in `μm` and flux in `Jy`) are used unless `flux_unit` is specified.

## Coming Soon

- Support for MIRI `s3d` and `x1d` files
- Simple "first-look" plots

## Contribute

Use other JWST formats? PRs always very welcome!

## Docs

https://jwstfits.readthedocs.io  
(pending publication)

## Install

```bash
pip install jwstfits
```

## Memes

<p float="left">
  <img src="/jwstfits/images/confusedfits.jpeg" height="250" />
  <img src="/jwstfits/images/onedoesnotsimplyopenfitsfile.jpg" height="250" /> 
</p>
