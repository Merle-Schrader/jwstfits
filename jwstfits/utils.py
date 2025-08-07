from astropy.io import fits

def columns(path):
    """
    Print FITS file structure and column definitions for the first EXTRACT1D extension.

    Parameters
    ----------
    path : str
        Path to the FITS file.

    Notes
    -----
    - Mimics the behavior of `hdul.info()` but truncates duplicate EXTRACT1D entries for time-series data.
    - Also prints the column definitions of the first EXTRACT1D extension.
    """

    with fits.open(path) as hdul:
        extract1d_count = sum(1 for hdu in hdul if hdu.name.upper() == "EXTRACT1D")
        
        print(f"\nFITS File Structure (truncated if many EXTRACT1D extensions):\n")

        # Manually replicate hdul.info() behavior, but skip duplicate EXTRACT1D entries
        printed_extract1d = False
        for i, hdu in enumerate(hdul):
            name = hdu.name if hasattr(hdu, 'name') else 'UNKNOWN'
            hdu_type = type(hdu).__name__
            n_card = len(hdu.header)
            dims = hdu.shape if hasattr(hdu, 'shape') else ()
            fmt = getattr(hdu, 'columns', None)
            fmt_str = str(fmt.formats) if fmt else ""

            if name.upper() == "EXTRACT1D":
                if printed_extract1d:
                    continue  # Skip repeated extract1D entries
                printed_extract1d = True

            print(f"{i:<5} {name:<12} {i:<5} {hdu_type:<13} {n_card:<6} {dims!s:<15} {fmt_str}")

        if extract1d_count > 1:
            print(f"\n... (+{extract1d_count - 1} additional EXTRACT1D extensions omitted)")

        # Print column info from the first EXTRACT1D extension
        for hdu in hdul:
            if hdu.name.upper() == "EXTRACT1D":
                print(f"\nColumns in EXTRACT1D extension (index {hdul.index_of(hdu)}):")
                print(hdu.columns)
                break


def tree(path):
    """
    Display a tree-like structure of the FITS file contents.

    Parameters
    ----------
    path : str
        Path to the FITS file.

    Notes
    -----
    - Shows extension index, name, type, and the first few header keywords.
    - If there are multiple EXTRACT1D extensions, only the first is shown with a summary note of skipped ones.
    - Useful for quick exploration of file layout and header content.
    """

    hdul = fits.open(path)
    print(f"\nFITS File Tree Structure for: {path}")
    
    extract1d_seen = False
    extract1d_skipped = 0

    for i, hdu in enumerate(hdul):
        # Get the EXTNAME if available
        name = hdu.name if hasattr(hdu, 'name') else 'UNKNOWN'
        if name == 'UNKNOWN' and 'EXTNAME' in hdu.header:
            name = hdu.header['EXTNAME']

        if name == 'EXTRACT1D':
            if extract1d_seen:
                extract1d_skipped += 1
                continue  # Skip extra EXTRACT1D entries
            extract1d_seen = True

        hdu_type = type(hdu).__name__
        print(f"├── [{i}] {name} ({hdu_type})")
        if hasattr(hdu, 'header'):
            for key in list(hdu.header.keys())[:5]:
                print(f"│   ├── {key}: {hdu.header[key]}")
            if len(hdu.header) > 5:
                print(f"│   └── ... (+{len(hdu.header)-5} more)")

    if extract1d_skipped > 0:
        print(f"│   └── ({extract1d_skipped+1} total EXTRACT1D extensions; {extract1d_skipped} not shown.)")
    
    hdul.close()

def head(path, n=5):
    """
    Print the full headers and a preview of data from a FITS file.

    Parameters
    ----------
    path : str
        Path to the FITS file.
    n : int, optional
        Number of data rows to preview from each table HDU (default is 5).

    Notes
    -----
    - Only shows the first EXTRACT1D extension if duplicates exist.
    - Displays full headers using `repr` to preserve formatting.
    - If table data is present, prints a preview of the data array.
    """
    hdul = fits.open(path)
    print(f"\nFITS File Headers for: {path}")

    extract1d_seen = False
    extract1d_skipped = 0

    for i, hdu in enumerate(hdul):
        name = hdu.name if hasattr(hdu, 'name') else 'UNKNOWN'
        if name == 'UNKNOWN' and 'EXTNAME' in hdu.header:
            name = hdu.header['EXTNAME']

        if name == 'EXTRACT1D':
            if extract1d_seen:
                extract1d_skipped += 1
                continue
            extract1d_seen = True

        if hasattr(hdu, 'header'):
            print(f"\nHeader [{i}] ({name}):")
            print(repr(hdu.header))

        if hasattr(hdu, 'data') and hasattr(hdu.data, 'columns'):
            print(f"\nData [{i}] Preview:")
            print(hdu.data[:n])

    if extract1d_skipped > 0:
        print(f"\n ({extract1d_skipped+1} total EXTRACT1D extensions; {extract1d_skipped} not shown.)")

    hdul.close()
