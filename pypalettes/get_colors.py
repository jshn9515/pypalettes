import csv
from difflib import get_close_matches
from importlib import resources

import matplotlib as mpl

from .colormap import ExtendColormap

PALETTES: list[str] = []


def load_palettes(palettes_path: str = 'palettes.csv'):
    """
    Load palettes from csv file.

    Parameters
    - palettes_path
        Path to the csv file with the palettes
    """

    global PALETTES

    palettes_file = resources.files('pypalettes').joinpath(palettes_path)
    with palettes_file.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'].endswith('_r'):
                continue
            PALETTES.append(row['name'])
            try:
                hex_list = eval(row['palette'])
                if not isinstance(hex_list, list) or not all(
                    isinstance(color, str) for color in hex_list
                ):
                    raise ValueError('palette must be a list of hex color strings.')
            except Exception as e:
                raise ValueError(f'Error parsing palette: {e}')

            cmap_discrete = ExtendColormap.from_colors(
                name=row['name'],
                cmap_type='discrete',
                colors=hex_list,
            )

            try:
                mpl.colormaps.register(cmap_discrete)
            except ValueError:
                pass


def get_suggestions(name: str):
    suggestions = get_close_matches(name, PALETTES, n=5, cutoff=0.01)
    suggestions = ', '.join(suggestions)
    raise ValueError(
        f"Palette with name '{name}' not found. Did you mean: {suggestions}?\n"
        f'See available palettes at https://python-graph-gallery.com/color-palette-finder/.'
    )
