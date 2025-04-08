from typing import cast

import bs4
import matplotlib.colors as mcolors
import pandas as pd
import requests
import seaborn as sns
from matplotlib import colormaps
from utils import split_string


def palette_to_hex(palette_name: str, n_colors: int = 10) -> list[str]:
    """Convert a palette name to a list of hex color values."""
    palette = sns.color_palette(palette_name, n_colors)
    hex_values = [mcolors.rgb2hex(color) for color in palette]
    return hex_values


def cmap_to_hex(cmap_name: str) -> list[str]:
    """Convert a colormap name to a list of hex color values."""
    cmap = colormaps[cmap_name]
    hex_values = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    return hex_values


def get_manual_palettes(palettes: dict) -> pd.DataFrame:
    """Convert a dictionary of palettes to a pandas DataFrame."""
    palette = {}
    for key, value in palettes.items():
        palette[key] = value
    df = pd.DataFrame.from_dict(palette, orient='index')
    return df


def get_matplotlib_and_seaborn_palettes():
    palette_names = ['deep', 'muted', 'bright', 'pastel', 'dark', 'colorblind']
    diverging_palettes = ['vlag', 'icefire', 'Spectral', 'coolwarm', 'RdBu']
    sequential_palettes = [
        'rocket',
        'mako',
        'flare',
        'crest',
        'viridis',
        'plasma',
        'inferno',
        'magma',
        'cividis',
    ]
    qualitative_palettes = [
        'tab10',
        'tab20',
        'Set1',
        'Set2',
        'Set3',
        'Paired',
        'Accent',
        'Dark2',
    ]
    all_palette_names = (
        palette_names + diverging_palettes + sequential_palettes + qualitative_palettes
    )

    seaborn_palettes = pd.DataFrame(
        {
            'name': all_palette_names,
            'palette': [palette_to_hex(name) for name in all_palette_names],
            'source': ['matplotlib/seaborn builtin'] * len(all_palette_names),
        }
    )

    all_cmap_names = list(colormaps)
    matplotlib_palettes = pd.DataFrame(
        {
            'name': all_cmap_names,
            'palette': [cmap_to_hex(name) for name in all_cmap_names],
            'source': ['matplotlib/seaborn builtin'] * len(all_cmap_names),
            'kind': ['unknown'] * len(all_cmap_names),
            'paletteer-kind': ['unknown'] * len(all_cmap_names),
        }
    )

    # combine the palettes
    df = pd.concat([seaborn_palettes, matplotlib_palettes])
    df.reset_index(drop=True, inplace=True)
    df.drop_duplicates(subset='name', keep='first', inplace=True)

    return df


def get_paletteer_palettes():
    # load the HTML file (from: https://pmassicotte.github.io/paletteer_gallery/)
    url = 'https://pmassicotte.github.io/paletteer_gallery/index.html'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')

    # initialize lists to store data and the soup
    names = []
    palettes = []
    sources = []
    kinds = []
    paletteer_kinds = []

    # find sections that separate discrete and continuous palettes
    sections = soup.find_all('section', class_='level2')

    for section in sections:
        assert isinstance(section, bs4.element.Tag)
        # get whether we're in the discrete or continuous section
        first_kind = cast(str, section['id'])
        first_kind = first_kind.split('-')[0]

        sub_sections = soup.find_all('section', class_='level3')

        # iterate over each sub_section found
        for sub_section in sub_sections:
            assert isinstance(sub_section, bs4.element.Tag)
            kind = sub_section['id']

            # get the name and source of the palette
            name_tags = sub_section.find_all('center')
            for name_tag in name_tags:
                name = name_tag.text.strip()
                source, name = split_string(name)
                source = f'The R package: {{{source}}}'
                names.append(name)
                sources.append(source)

            # get the hex values and kind of the palette
            palette_tags = sub_section.find_all('hr')
            for palette_tag in palette_tags:
                all_pars = palette_tag.find_previous_sibling('p')
                assert isinstance(all_pars, bs4.element.Tag)
                all_spans = all_pars.find_all('span')
                palette = [span.text for span in all_spans]
                palettes.append(palette)
                kinds.append(kind)
                paletteer_kind = f'{first_kind}-{kind}'
                paletteer_kind = (
                    paletteer_kind
                    if not paletteer_kind.endswith('-1')
                    else paletteer_kind[:-2]
                )
                paletteer_kinds.append(paletteer_kind)

        # create pandas df with palette properties
        df = pd.DataFrame(
            {
                'name': names,
                'palette': palettes,
                'source': sources,
                'kind': kinds,
                'paletteer-kind': paletteer_kinds,
            }
        )

        return df
