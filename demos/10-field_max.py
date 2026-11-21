import numpy as np
import flowfields.scalar_fields as sf
import flowfields.vector_fields as vf
from _common import panels, save, strokes

# At each point only the field with the highest weight counts, so the plane is
# split in regions with sharp borders.
centers = [np.array([-0.5, -0.4]), np.array([0.5, -0.3]), np.array([0.0, 0.5])]
fields = [vf.RotationField(center) for center in centers]

weights = {
    "GaussianField weights": [sf.GaussianField(center, sigma=0.5) for center in centers],
    "BoxField weights": [
        sf.BoxField(np.array([-1.0, -1.0]), np.array([0.2, 0.2]), inside_value=2.0),
        sf.BoxField(np.array([-0.3, -0.8]), np.array([1.0, 0.7]), inside_value=1.0),
        sf.ConstantField(0.5),
    ],
}

fig, axes = panels(list(weights))
for ax, w in zip(axes, weights.values()):
    strokes(ax, vf.FieldMax(fields, weights=w), n_lines=1200)
save(fig, __file__)
