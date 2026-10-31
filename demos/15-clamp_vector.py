import numpy as np
import tstudio.utils
import tstudio.vector_fields as vf
from _common import panels, save, strokes

# Single segments of a field whose vectors grow with the distance to the center.
field = vf.RotationField(np.zeros(2), normalize=False)
limits = {
    "no clamp": None,
    "max_length=0.05": (0.0, 0.05),
    "min_length=0.1, max_length=0.1": (0.1, 0.1),
}

fig, axes = panels(list(limits))
for ax, limit in zip(axes, limits.values()):
    transform = None
    if limit is not None:
        transform = lambda dx: tstudio.utils.clamp_vector(dx, *limit)
    strokes(ax, field, n_lines=1500, n_steps=1, step=0.2, transform=transform)
save(fig, __file__)
