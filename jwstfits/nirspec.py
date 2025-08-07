import numpy as np
from astropy.io import fits
import pandas as pd


def _convert_flux_manually(flux, wavelength, to_unit):
    """
    Manually convert flux from Jansky (Jy) to other units.

    Parameters
    ----------
    flux : np.ndarray
        Flux array in Jy.
    wavelength : np.ndarray
        Wavelength array in microns (μm).
    to_unit : str
        Desired flux unit. Currently only supports "W/m2/um".

    Returns
    -------
    np.ndarray
        Flux array converted to the target unit.

    Raises
    ------
    ValueError
        If `to_unit` is not supported.
    """

    if to_unit == "W/m2/um":
        c = 2.9979e14  # speed of light in μm/s
        return (c * flux) / (wavelength ** 2) * 1e-26
    else:
        raise ValueError(f"Currently unsupported flux unit: {to_unit}. Consider adding a conversion to this package?")

def _kick_nan(w, f, fe, time=None, axis=1):
    """
    Remove NaNs across wavelength, flux, and error arrays.

    Parameters
    ----------
    w : np.ndarray
        Wavelength array.
    f : np.ndarray
        Flux array (1D or 2D).
    fe : np.ndarray
        Flux error array.
    time : np.ndarray, optional
        Time array (only used for x1dints files).
    axis : int, optional
        Axis to remove NaNs on if 2D. Default is 1 (time axis).

    Returns
    -------
    tuple
        Cleaned (wavelength, flux, error, time) arrays.
    """

    if f.ndim == 1:
        # 1D arrays (x1d)
        mask = ~np.isnan(f)
        return w[mask], f[mask], fe[mask], time
    elif f.ndim == 2:
        # 2D arrays (x1dints)
        mask = ~np.any(np.isnan(f), axis=axis)
        if axis == 1:
            return w[mask], f[mask], fe[mask], time
        elif axis == 0:
            return w[:, mask], f[:, mask], fe[:, mask], time[mask]
    else:
        raise ValueError("Flux array has unsupported number of dimensions.")
    
def _remove_outlier_range(wavelength, flux, error, outlier_range, buffer=2, iqr_threshold=1.5):
    """
    Remove outlier flux values in a given wavelength range with surrounding buffer.

    Parameters
    ----------
    wavelength : np.ndarray
        Wavelength array, shape (n,) or (n, t).
    flux : np.ndarray
        Flux array, same shape as wavelength.
    error : np.ndarray
        Error array, same shape as flux.
    outlier_range : tuple of float
        Range (min_wl, max_wl) in microns to search for outliers.
    buffer : int, optional
        Number of indices around outlier max to also remove. Default is 2.
    iqr_threshold : float, optional
        Placeholder for future robust outlier detection. Currently unused.

    Returns
    -------
    tuple
        Cleaned (wavelength, flux, error) arrays with outlier region removed.
    """

    if wavelength.ndim == 1:
        ref_wl = wavelength
    else:
        ref_wl = wavelength[:, 0]  # Assume same wavelength across time

    mask_range = (ref_wl >= outlier_range[0]) & (ref_wl <= outlier_range[1])
    broken_indices = np.where(mask_range)[0]

    if len(broken_indices) == 0:
        print("No indices found in outlier range.")
        return wavelength, flux, error

    # Find max flux index
    max_idx = broken_indices[np.argmax(np.max(flux[broken_indices], axis=-1))]

    # Add buffer
    clip_idx = np.arange(max_idx - buffer, max_idx + buffer + 1)
    clip_idx = clip_idx[(clip_idx >= 0) & (clip_idx < ref_wl.shape[0])]

    print(f"[outlier clip] Removing wavelengths: {ref_wl[clip_idx]}")

    # Delete along first axis
    wavelength = np.delete(wavelength, clip_idx, axis=0)
    flux = np.delete(flux, clip_idx, axis=0)
    error = np.delete(error, clip_idx, axis=0)

    return wavelength, flux, error


def x1d(path, wlrange=None, kicknan=False, flux_unit="Jy", output="arrays", outlier=None, buffer=2):
    """
    Load JWST NIRSpec x1d spectrum from a FITS file.

    Parameters
    ----------
    path : str
        Path to the x1d FITS file.
    wlrange : tuple of float, optional
        Wavelength range to clip, as (min, max) in microns.
    kicknan : bool, optional
        If True, remove NaNs from the spectrum. Default is False.
    flux_unit : str, optional
        Desired flux unit. Supports "Jy" or "W/m²/μm". Default is "Jy".
    output : str, optional
        Output format: "arrays", "dataframe", or "datacube". Default is "arrays".
    outlier : tuple of float, optional
        Wavelength range (min, max) to remove known outliers.
    buffer : int, optional
        Number of adjacent points to remove around outlier maximum. Default is 2.

    Returns
    -------
    tuple or pd.DataFrame or dict
        Depending on `output`:
        - "arrays": tuple of (wavelength, flux, flux_error)
        - "dataframe": pandas DataFrame
        - "datacube": dict with keys "wavelength", "flux", "error"

    Raises
    ------
    ValueError
        If the flux array contains only NaNs or if the output format is unknown.
    """

    hdul = fits.open(path)

    w = hdul[2].data['WAVELENGTH']
    f = hdul[2].data['FLUX']
    fe = hdul[2].data['FLUX_ERROR']

    #check if nan data:
    if not np.any(np.isfinite(f)):
        raise ValueError("Flux array contains only NaNs. Check your input file or extraction pipeline.")

    w, f, fe = np.asarray(w), np.asarray(f), np.asarray(fe)

    if wlrange:
        mask = (w >= wlrange[0]) & (w <= wlrange[1])
        w, f, fe = w[mask], f[mask], fe[mask]

    if kicknan:
        w, f, fe, _ = _kick_nan(w, f, fe, None)

    if flux_unit != "Jy":
        f = _convert_flux_manually(f, w, flux_unit)
        fe = _convert_flux_manually(fe, w, flux_unit)

    if outlier:
        w, f, fe = _remove_outlier_range(w, f, fe, outlier, buffer)

    hdul.close()

    if output == "arrays":
        return w, f, fe
    elif output == "dataframe":
        df = pd.DataFrame({
            "wavelength": w.flatten(),
            "flux": f.flatten(),
            "flux_error": fe.flatten()
        })
        return df
    elif output == "datacube":
        cube = {"wavelength": w, "flux": f, "error": fe}
        return cube
    else:
        raise ValueError(f"Unknown output format: {output}")

def x1dints(path, clipwl=None, kicknan=False, flux_unit="Jy", output="arrays", outlier=None, buffer=2):
    """
    Load JWST NIRSpec x1dints time-series spectrum from a FITS file.

    Parameters
    ----------
    path : str
        Path to the x1dints FITS file.
    clipwl : tuple of float, optional
        Wavelength range to clip, as (min, max) in microns.
    kicknan : bool, optional
        If True, remove NaNs across time. Default is False.
    flux_unit : str, optional
        Desired flux unit. Supports "Jy" or "W/m²/μm". Default is "Jy".
    output : str, optional
        Output format: "arrays", "dataframe", or "datacube". Default is "arrays".
    outlier : tuple of float, optional
        Wavelength range (min, max) to remove known outliers.
    buffer : int, optional
        Number of adjacent points to remove around outlier maximum. Default is 2.

    Returns
    -------
    tuple or pd.DataFrame or dict
        Depending on `output`:
        - "arrays": (wavelength, flux, flux_error, time)
        - "dataframe": pandas DataFrame
        - "datacube": dict with keys: wavelength, flux, error, (optional) time

    Raises
    ------
    ValueError
        If filename is not recognized as x1dints or if the output format is unknown.
    """

    if not ("x1dints" in path and "x1d" in path):
        raise ValueError("Filename should contain 'x1dints' since you're trying to use the x1dints.fits function.")

    hdul = fits.open(path)

    time = hdul[1].data.field('int_mid_BJD_TDB')
    time = (time - time[0]) * 24  # Convert BJD to hours from t=0

    n_times = len(time)
    #n_wpts = hdul[2].data['WAVELENGTH'].shape[0]

    wavelength = hdul[2].data['WAVELENGTH']
    n_wpts = len(wavelength)

    w = np.zeros((n_wpts, n_times))
    f = np.zeros_like(w)
    fe = np.zeros_like(w)

    for j in range(n_times):
        w[:, j] = hdul[j + 2].data['WAVELENGTH']
        f[:, j] = hdul[j + 2].data['FLUX']
        fe[:, j] = hdul[j + 2].data['FLUX_ERROR']

    if clipwl:
        mask = (w[:, 0] >= clipwl[0]) & (w[:, 0] <= clipwl[1])
        w, f, fe = w[mask], f[mask], fe[mask]

    if kicknan:
        w, f, fe, time = _kick_nan(w, f, fe, time, axis=0)

    if flux_unit != "Jy":
        f = _convert_flux_manually(f, w, flux_unit)
        fe = _convert_flux_manually(fe, w, flux_unit)

    if outlier:
        w, f, fe = _remove_outlier_range(w, f, fe, outlier, buffer)

    hdul.close()

    if output == "arrays":
        return w, f, fe if "time" not in locals() else (w, f, fe, time)
    elif output == "dataframe":
        df = pd.DataFrame({
            "wavelength": w.flatten(),
            "flux": f.flatten(),
            "flux_error": fe.flatten()
        })
        if "time" in locals():
            df["time"] = np.repeat(time, w.shape[0])
        return df
    elif output == "datacube":
        cube = {"wavelength": w, "flux": f, "error": fe}
        if "time" in locals():
            cube["time"] = time
        return cube
    else:
        raise ValueError(f"Unknown output format: {output}")