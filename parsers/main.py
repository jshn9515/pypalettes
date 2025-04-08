import json

import pandas as pd
from generate_palettes import (
    get_manual_palettes,
    get_matplotlib_and_seaborn_palettes,
    get_paletteer_palettes,
)

with open('manual_palettes.json', 'r') as fp:
    palettes = json.load(fp)

paletteer = get_paletteer_palettes()
matplot_seaborn = get_matplotlib_and_seaborn_palettes()
manual_palettes = get_manual_palettes(palettes)

df = pd.concat([matplot_seaborn, paletteer, manual_palettes])
df.reset_index(drop=True, inplace=True)
df.drop_duplicates(subset='name', keep='first', inplace=True)
df.sort_values('name', inplace=True)

print(f'\n Total (unique) palettes found: {len(df)}')
df.to_csv('palettes.csv', index=False)
df.to_json('palettes.json', orient='records')
