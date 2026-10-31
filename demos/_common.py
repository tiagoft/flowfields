"""Drawing helpers shared by the demos, so each demo only shows its own class."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgb
from tstudio.utils import open_image

BACKGROUND = (0.961, 0.949, 0.922)
BLUE = (0.196, 0.322, 0.482)
RED = (0.796, 0.427, 0.318)

HERE = Path(__file__).parent
SQUARE = (-1, 1)
EIFFEL_X = (0, 512 / 340)  # keeps the aspect ratio of eiffel.jpeg
EIFFEL_Y = (0, 1)
EIFFEL_MIN = np.array([EIFFEL_X[0], EIFFEL_Y[0]])
EIFFEL_MAX = np.array([EIFFEL_X[1], EIFFEL_Y[1]])

np.random.seed(0)


def eiffel(mode="RGB"):
    """Loads eiffel.jpeg as floats in [0, 1]. Use mode="L" for grayscale."""
    return open_image(HERE / "eiffel.jpeg", mode)


def panels(titles, xlim=SQUARE, ylim=SQUARE):
    """Creates one row of axes, one for each title."""
    aspect = (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, axes = plt.subplots(
        1,
        len(titles),
        figsize=(4 * len(titles) * aspect, 4.4),
        layout="constrained",
        squeeze=False,
        facecolor=BACKGROUND,
    )
    for ax, title in zip(axes[0], titles):
        ax.set_facecolor(BACKGROUND)
        ax.set_title(title, fontsize=10)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xticks([])
        ax.set_yticks([])
    return fig, axes[0]


def heatmap(ax, scalar_field, resolution=200, vmin=0, vmax=1):
    """Paints the value of a scalar field at each point of the axes."""
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    xs = np.linspace(*xlim, resolution)
    ys = np.linspace(*ylim, resolution)
    values = [[scalar_field(np.array([x, y])) for x in xs] for y in ys]
    ax.imshow(values, extent=(*xlim, *ylim), origin="lower", aspect="auto",
              cmap="magma", vmin=vmin, vmax=vmax)


def arrows(ax, vector_field, n=12):
    """Draws the vector field as a grid of arrows."""
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    xs, ys = np.meshgrid(np.linspace(*xlim, n + 2)[1:-1], np.linspace(*ylim, n + 2)[1:-1])
    vectors = [vector_field(np.array(p)) for p in zip(xs.ravel(), ys.ravel())]
    us, vs = np.array(vectors).T
    ax.quiver(xs.ravel(), ys.ravel(), us, vs, color=RED, zorder=3)


def strokes(
    ax,
    vector_field,
    n_lines=800,
    n_steps=40,
    step=0.01,
    start=None,
    color=BLUE,
    alpha=0.6,
    linewidth=0.5,
    transform=None,
):
    """
    Follows the vector field from random starting points, drawing one line for
    each. ``start`` fixes the starting point, ``color`` and ``alpha`` can be
    functions of the starting point, and ``transform`` modifies each step.
    """
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    lines = []
    colors = []
    for _ in range(n_lines):
        if start is None:
            x = np.array([np.random.uniform(*xlim), np.random.uniform(*ylim)])
        else:
            x = np.array(start, dtype=float)
        c = color(x) if callable(color) else color
        a = alpha(x) if callable(alpha) else alpha
        colors.append((*to_rgb(c), a))

        line = [x]
        for _ in range(n_steps):
            dx = vector_field(x) * step
            if transform is not None:
                dx = transform(dx)
            x = x + dx
            line.append(x)
        lines.append(line)
    ax.add_collection(LineCollection(lines, colors=colors, linewidths=linewidth))


def save(fig, demo_file, suffix=""):
    """Saves the figure in demos/outputs, named after the demo script."""
    output = HERE / "outputs" / f"{Path(demo_file).stem}{suffix}.png"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=90)
    print(f"Saved {output}")
