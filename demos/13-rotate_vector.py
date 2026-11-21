import numpy as np
import flowfields.utils
import flowfields.vector_fields as vf
from _common import panels, save, strokes

# Rotating every step of the same field: at 90 degrees, circles become rays.
field = vf.RotationField(np.zeros(2))
angles = [0, 45, 90]

fig, axes = panels([f"angle={angle} degrees" for angle in angles])
for ax, angle in zip(axes, angles):
    strokes(ax, field, transform=lambda dx: flowfields.utils.rotate_vector(dx, np.radians(angle)))
save(fig, __file__)
