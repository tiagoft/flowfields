import numpy as np
import pytest

import flowfields as ff
from flowfields.utils import kmeans


def p(x, y):
    return np.array([x, y], dtype=float)


class TestKmeans:
    def test_one_cluster_is_the_mean(self):
        data = np.random.default_rng(0).uniform(size=(30, 3))
        centers, labels = kmeans(data, 1, rng=0)
        assert centers[0] == pytest.approx(data.mean(axis=0))
        assert np.all(labels == 0)

    def test_finds_repeated_points(self):
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0.5], [0.2, 0.2, 0.9]], dtype=float)
        data = np.random.default_rng(1).permutation(np.repeat(points, [5, 7, 4, 6], axis=0))
        centers, labels = kmeans(data, 4, rng=2)
        assert np.allclose(sorted(centers.tolist()), sorted(points.tolist()))
        assert np.allclose(centers[labels], data)

    def test_separated_blobs(self):
        rng = np.random.default_rng(3)
        means = np.array([[0, 0], [10, 0], [0, 10], [10, 10]], dtype=float)
        data = np.concatenate([m + 0.1 * rng.normal(size=(20, 2)) for m in means])
        centers, labels = kmeans(data, 4, rng=0)
        for m in means:
            assert np.min(np.linalg.norm(centers - m, axis=1)) < 0.1
        # each blob of 20 points ends up in a single cluster
        for b in range(4):
            assert len(set(labels[20 * b:20 * (b + 1)])) == 1

    def test_labels_are_the_nearest_centers(self):
        data = np.random.default_rng(4).uniform(size=(200, 3))
        centers, labels = kmeans(data, 5, rng=0)
        distances = np.linalg.norm(data[:, None, :] - centers[None, :, :], axis=2)
        assert np.array_equal(labels, np.argmin(distances, axis=1))

    def test_same_seed_same_result(self):
        data = np.random.default_rng(5).uniform(size=(300, 3))
        a, b = kmeans(data, 6, rng=9), kmeans(data, 6, rng=9)
        assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])

    def test_fewer_distinct_points_than_clusters(self):
        data = np.array([[0, 0, 0]] * 10 + [[1, 1, 1]] * 10, dtype=float)
        centers, labels = kmeans(data, 4, rng=0)
        assert np.all(np.isfinite(centers))
        assert {tuple(np.round(c, 9)) for c in centers} == {(0, 0, 0), (1, 1, 1)}

    @pytest.mark.parametrize("k", [0, 21])
    def test_invalid_number_of_clusters(self, k):
        with pytest.raises(ValueError):
            kmeans(np.zeros((20, 3)), k)


RED, BLUE = [0.9, 0.1, 0.1], [0.1, 0.2, 0.9]
# 20 rows x 40 columns: red on the left half, blue on the right
IMAGE = np.zeros((20, 40, 3))
IMAGE[:, :20] = RED
IMAGE[:, 20:] = BLUE


def two_colors(**kwargs):
    return ff.MatrixColorField(p(0, 0), p(2, 1), IMAGE, n_colors=2, kernel_size=0.2, **kwargs)


class TestMatrixColorField:
    def test_palette_is_the_image_colors(self):
        assert np.allclose(sorted(two_colors().palette.tolist()), sorted([RED, BLUE]))

    def test_cold_draws_the_local_color(self):
        f = two_colors(temperature=0.01, rng=0)
        for _ in range(20):
            assert f(p(0.2, 0.5)) == pytest.approx(RED)
            assert f(p(1.8, 0.5)) == pytest.approx(BLUE)

    def test_probabilities(self):
        f = two_colors(temperature=0.5)
        red = int(np.argmin(np.linalg.norm(f.palette - RED, axis=1)))
        probs = f.get_probs(p(0.2, 0.5))
        assert probs.sum() == pytest.approx(1.0)
        assert probs[red] > 0.8
        # On the border the 9 x 9 window has 5 red columns and 4 blue ones,
        # so z = [5/9, 4/9] and p_red = 1 / (1 + exp(-(1/9) / temperature))
        border = f.get_probs(p(1.0, 0.5))
        assert border[red] == pytest.approx(1 / (1 + np.exp(-(1 / 9) / 0.5)))

    def test_very_low_temperature_gives_no_nan(self):
        f = two_colors(temperature=1e-9)
        assert np.all(np.isfinite(f.get_probs(p(0.5, 0.5))))

    def test_outside_uses_the_nearest_point(self):
        f = two_colors()
        assert f.get_probs(p(-5, 0.5)) == pytest.approx(f.get_probs(p(0, 0.5)))

    def test_same_seed_same_draws(self):
        a, b = two_colors(rng=4), two_colors(rng=4)
        for x in [p(0.9, 0.5), p(1.1, 0.2)] * 10:
            assert np.array_equal(a(x), b(x))
