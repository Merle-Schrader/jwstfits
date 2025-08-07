from astropy.io import fits

def columns(path):
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
