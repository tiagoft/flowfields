import numpy as np
from flowfields.color_fields import MatrixColorField
from _common import EIFFEL_MAX, EIFFEL_MIN, EIFFEL_X, EIFFEL_Y, RNG, eiffel, panels, save

data = eiffel()
options = {
    "n_colors=4": dict(n_colors=4, temperature=0.1),
    "n_colors=16": dict(n_colors=16, temperature=0.1),
    "n_colors=16, temperature=1": dict(n_colors=16, temperature=1.0),
}

fig, axes = panels(list(options), EIFFEL_X, EIFFEL_Y)
for ax, kwargs in zip(axes, options.values()):
    color_field = MatrixColorField(EIFFEL_MIN, EIFFEL_MAX, data, kernel_size=0.05, rng=RNG, **kwargs)
    points = RNG.uniform(EIFFEL_MIN, EIFFEL_MAX, size=(30000, 2))
    colors = [color_field(point) for point in points]
    # MatrixColorField has y=0 at the top of the image, so y is flipped to draw.
    ax.scatter(points[:, 0], EIFFEL_MAX[1] - points[:, 1], color=colors, s=3)
save(fig, __file__)
