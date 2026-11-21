import numpy as np
import flowfields.scalar_fields as sf
from _common import heatmap, panels, save

center = np.array([0.2, -0.1])
sigmas = [0.15, 0.4, 1.0]

fig, axes = panels([f"sigma={sigma}" for sigma in sigmas])
for ax, sigma in zip(axes, sigmas):
    heatmap(ax, sf.GaussianField(center, sigma=sigma))
save(fig, __file__)
