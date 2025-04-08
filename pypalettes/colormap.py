import itertools
from typing import Any, Self, Sequence, overload

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


class ExtendColormap(mcolors.Colormap):
    """
    A wrapper around matplotlib colormaps to add chaining operations like
    truncation, reversal, resampling, alpha adjustment, and composition.
    """

    def __init__(self, cmap: mcolors.Colormap, cmap_type: str):
        self.cmap = cmap
        self.name = self.cmap.name
        self.N = self.cmap.N
        self.cmap_type = cmap_type

    @classmethod
    def from_colors(
        cls,
        name: str,
        cmap_type: str,
        colors: npt.ArrayLike,
        N: int | None = None,
    ) -> Self:
        """Create a new colormap from a list of colors."""
        if cmap_type == 'discrete':
            cmap = ListedColormap(name=name, colors=colors, N=N)
        elif cmap_type == 'continuous':
            if N is None:
                N = 256
            cmap = LinearSegmentedColormap.from_list(name=name, colors=colors, N=N)
        else:
            raise ValueError("cmap_type argument must be 'continuous' or 'discrete'.")
        return cls(cmap, cmap_type=cmap_type)

    @overload
    def __call__(
        self,
        X: Sequence[float] | np.ndarray,
        alpha: npt.ArrayLike | None = ...,
        bytes: bool = ...,
    ) -> np.ndarray: ...
    @overload
    def __call__(
        self, X: float, alpha: float | None = ..., bytes: bool = ...
    ) -> tuple[float, float, float, float]: ...
    @overload
    def __call__(
        self, X: npt.ArrayLike, alpha: npt.ArrayLike | None = ..., bytes: bool = ...
    ) -> tuple[float, float, float, float] | np.ndarray: ...

    def __call__(self, X, alpha=None, bytes=False):
        """Call the underlying colormap with a scalar or array input."""
        return self.cmap(X, alpha, bytes)

    def __repr__(self):
        return f'ExtendColormap({self.name}, cmap_type={self.cmap_type})'

    def __getattr__(self, name: str):
        """Delegate attribute access to the underlying colormap."""
        return getattr(self.cmap, name)

    def __iter__(self):
        """Iterate over the colors in the colormap."""
        colors = [self(x) for x in np.linspace(0, 1, self.N)]
        return itertools.cycle(colors)

    def _create_cmap(self, name: str, colors: npt.ArrayLike, N: int):
        if self.cmap_type == 'discrete':
            cmap = ListedColormap(name=name, colors=colors, N=N)
        else:
            cmap = LinearSegmentedColormap.from_list(name=name, colors=colors, N=N)
        return ExtendColormap(cmap, cmap_type=self.cmap_type)

    @property
    def palette(self) -> Any:
        """Return the colors of the colormap as an array."""
        if self.cmap_type == 'discrete':
            return self.colors
        else:
            return self.cmap(np.linspace(0, 1, self.N))

    def reversed(self, inplace: bool = False):
        """Return a new SmartColormap with the reversed colormap."""
        if inplace:
            self.cmap = self.cmap.reversed()
            self.name = self.cmap.name
            return self
        else:
            return ExtendColormap(self.cmap.reversed(), cmap_type=self.cmap_type)

    def resampled(self, lutsize: int, inplace: bool = False):
        """Return a new SmartColormap with N colors using matplotlib's native resampled method."""
        if inplace:
            self.cmap = self.cmap.resampled(lutsize)
            self.N = self.cmap.N
            return self
        else:
            return ExtendColormap(
                self.cmap.resampled(lutsize), cmap_type=self.cmap_type
            )

    def truncate(self, start: float = 0.0, end: float = 1.0):
        """Truncate the colormap to a subrange [start, end] and return a new Colormap."""
        x = np.linspace(start, end, self.N)
        name = f'{self.name}_trunc_{start:.2f}_{end:.2f}'
        colors = self.cmap(x)
        return self._create_cmap(name, colors, self.N)

    def with_alpha(self, alpha: float = 1.0):
        """Set a uniform alpha value for all colors in the colormap."""
        colors = self.cmap(np.linspace(0, 1, 256))
        colors[:, -1] = alpha
        name = f'{self.name}_alpha_{alpha:.2f}'
        return self._create_cmap(name, colors, self.N)

    def __add__(self, other: 'ExtendColormap'):
        """Concatenate this colormap with another SmartColormap."""
        cmap1 = self(np.linspace(0, 1, self.N))
        cmap2 = other(np.linspace(0, 1, other.N))
        colors = np.vstack([cmap1, cmap2])
        name = f'{self.name}_plus_{other.name}'
        return self._create_cmap(name, colors, self.N + other.N)

    def __mul__(self, factor: int):
        """Repeat the colormap smoothly by using modulo to create periodicity."""
        norm_vals = np.linspace(0, 1, self.N * factor)
        mod_vals = np.mod(norm_vals * factor, 1.0)
        colors = self.cmap(mod_vals)
        name = f'{self.name}_times_{factor}'
        return self._create_cmap(name, colors, self.N * factor)

    def plot(self):
        a = np.outer(np.ones(10), np.arange(0, 1, 0.001))
        fig = plt.figure('cmap')
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(a, aspect='auto', cmap=self, origin='lower')
        ax.text(
            x=0.5,
            y=0.5,
            s=self.name,
            verticalalignment='center',
            horizontalalignment='center',
            fontsize=18,
            transform=ax.transAxes,
        )
        ax.axis('off')
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        plt.show()
