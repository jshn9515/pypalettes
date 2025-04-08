import warnings

import matplotlib as mpl
import matplotlib.colors as mcolor
import matplotlib.pyplot as plt
import numpy.typing as npt

from .colormap import ExtendColormap
from .get_colors import get_suggestions


def get_cmap(
    name: str, cmap_type: str = 'continuous', N: int | None = None
) -> ExtendColormap:
    """
    Load colormap from name.

    Args:
        name (atr): Name of the palette.
        cmap_type (str): Type of colormap: 'continuous' or 'discrete'.
        N (int, optional): Number of colors in the colormap. Default is None.
    """
    try:
        cmap = plt.get_cmap(name, N)
    except ValueError:
        get_suggestions(name)

    if isinstance(cmap, ExtendColormap):
        assert cmap.cmap_type == 'discrete'
        if cmap_type == 'continuous':
            cmap = ExtendColormap.from_colors(
                name=name,
                cmap_type='continuous',
                colors=cmap.colors,
                N=N,
            )
    elif isinstance(cmap, mcolor.ListedColormap):
        cmap = ExtendColormap(cmap, cmap_type='discrete')
    elif isinstance(cmap, mcolor.LinearSegmentedColormap):
        cmap = ExtendColormap(cmap, cmap_type='continuous')
    else:
        raise TypeError(
            f"Colormap type '{type(cmap)}' is not a valid ExtendColormap or matplotlib colormap."
        )
    return cmap


def add_cmap(
    name: str,
    cmap_type: str,
    colors: npt.ArrayLike,
    N: int = 256,
    force: bool = True,
) -> ExtendColormap:
    """
    Create a matplotlib colormap from an iterable of colors.

    Args:
        name (str): Unique palette name.
        cmap_type (str): Type of colormap: 'continuous' or 'discrete'.
        colors (npt.ArrayLike): An iterable of valid matplotlib colors. More about valid colors: https://python-graph-gallery.com/python-colors/.
        N (int, optional): Number of colors in the colormap. Default is 256.
        force (bool, optional): If True, overwrites the registered colormap with the same name if it exists. Default is True.
    """
    cmap = ExtendColormap.from_colors(
        name=name,
        cmap_type=cmap_type,
        colors=colors,
        N=N,
    )

    warnings.filterwarnings(
        'ignore', category=UserWarning, message='.*that was already in the registry.*'
    )
    mpl.colormaps.register(cmap=cmap, force=force)
    return cmap
