import tstudio.scalar_fields as sf
from _common import EIFFEL_MAX, EIFFEL_MIN, EIFFEL_X, EIFFEL_Y, eiffel, heatmap, panels, save

# The matrix is multiplied by a Gaussian centered on the bounding box. Sigma is
# in the same units as the coordinates.
data = eiffel("L")
sigmas = [0.15, 0.4, 2.0]

fig, axes = panels([f"sigma={sigma}" for sigma in sigmas], EIFFEL_X, EIFFEL_Y)
for ax, sigma in zip(axes, sigmas):
    heatmap(ax, sf.KernelProbabilisticMatrixField(EIFFEL_MIN, EIFFEL_MAX, data, sigma=sigma))
save(fig, __file__)
