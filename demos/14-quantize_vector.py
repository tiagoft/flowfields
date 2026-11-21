import numpy as np
import flowfields.utils
import flowfields.vector_fields as vf
from _common import panels, save, strokes

# Each step can only point to one of n_levels directions.
field = vf.RotationField(np.zeros(2))
levels = [3, 4, 8]

fig, axes = panels([f"n_levels={n}" for n in levels])
for ax, n in zip(axes, levels):
    strokes(ax, field, n_lines=300, n_steps=80, transform=lambda dx: flowfields.utils.quantize_vector(dx, n))
save(fig, __file__)
