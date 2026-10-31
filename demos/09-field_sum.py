import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf
from _common import panels, save, strokes

left = np.array([-0.5, 0.0])
right = np.array([0.5, 0.0])
fields = [vf.RotationField(left), vf.RotationField(right, direction=-1)]

weights = {
    "weights=None": None,
    "weights=[3.0, 1.0]": [3.0, 1.0],
    "GaussianField weights": [
        sf.GaussianField(left, sigma=0.4),
        sf.GaussianField(right, sigma=0.4),
    ],
}

fig, axes = panels(list(weights))
for ax, w in zip(axes, weights.values()):
    strokes(ax, vf.FieldSum(fields, weights=w), n_steps=60)
save(fig, __file__)
