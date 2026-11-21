import numpy as np
import pytest

import flowfields as ff


def p(x, y):
    return np.array([x, y], dtype=float)


class TestGaussianField:
    def test_peak_is_scale_at_center(self):
        f = ff.GaussianField(p(0.3, -0.2), sigma=0.5, scale=2.0)
        assert f(p(0.3, -0.2)) == pytest.approx(2.0)

    def test_one_sigma_away(self):
        f = ff.GaussianField(p(0.0, 0.0), sigma=0.5, scale=2.0)
        assert f(p(0.0, 0.5)) == pytest.approx(2.0 * np.exp(-0.5))

    def test_is_symmetric(self):
        f = ff.GaussianField(p(1.0, 1.0), sigma=0.7)
        assert f(p(1.4, 1.0)) == pytest.approx(f(p(1.0, 0.6)))


def test_constant_field():
    f = ff.ConstantField(0.7)
    assert f(p(0, 0)) == 0.7
    assert f(p(-5, 100)) == 0.7


class TestBoxField:
    def test_inside_border_and_outside(self):
        f = ff.BoxField(p(-1, -1), p(1, 0.5), inside_value=2.0, outside_value=-1.0)
        assert f(p(0, 0)) == 2.0
        assert f(p(1, 0.5)) == 2.0  # borders are inside
        assert f(p(-1, 0)) == 2.0
        assert f(p(1.01, 0)) == -1.0
        assert f(p(0, -1.01)) == -1.0

    def test_corners_in_any_order(self):
        a = ff.BoxField(p(-1, -1), p(1, 0.5))
        b = ff.BoxField(p(1, 0.5), p(-1, -1))
        for x in [p(0, 0), p(2, 0), p(0.9, 0.4), p(-1.5, -0.5)]:
            assert a(x) == b(x)


# A 2 x 3 matrix over the box (0, 0)-(2, 1): the first row is at y = 1
DATA = np.array([[0.0, 1.0, 2.0],
                 [4.0, 5.0, 8.0]])


class TestMatrixField:
    def test_corners_are_the_matrix_corners(self):
        f = ff.MatrixField(p(0, 0), p(2, 1), DATA)
        assert f(p(0, 1)) == pytest.approx(0.0)  # top left: first row
        assert f(p(2, 1)) == pytest.approx(2.0)  # top right
        assert f(p(0, 0)) == pytest.approx(4.0)  # bottom left: last row
        assert f(p(2, 0)) == pytest.approx(8.0)  # bottom right

    def test_bilinear_between_pixels(self):
        f = ff.MatrixField(p(0, 0), p(2, 1), DATA)
        assert f(p(0.5, 1)) == pytest.approx(0.5)  # between 0 and 1
        assert f(p(0, 0.5)) == pytest.approx(2.0)  # between 0 and 4
        assert f(p(0.5, 0.5)) == pytest.approx((0 + 1 + 4 + 5) / 4)

    def test_zero_outside(self):
        f = ff.MatrixField(p(0, 0), p(2, 1), DATA + 10)
        assert f(p(-0.1, 0.5)) == 0.0
        assert f(p(1, 1.1)) == 0.0

    def test_normalize_rescales_to_unit_range(self):
        f = ff.MatrixField(p(0, 0), p(2, 1), DATA, normalize=True)
        assert f(p(0, 1)) == pytest.approx(0.0)
        assert f(p(2, 0)) == pytest.approx(1.0)
        assert f(p(1, 0)) == pytest.approx(5.0 / 8.0)

    def test_corners_in_any_order(self):
        a = ff.MatrixField(p(0, 0), p(2, 1), DATA)
        b = ff.MatrixField(p(2, 1), p(0, 0), DATA)
        assert a(p(0.3, 0.8)) == pytest.approx(b(p(0.3, 0.8)))

    def test_plot_figure_writes_a_file(self, tmp_path):
        pytest.importorskip("matplotlib")
        import matplotlib
        matplotlib.use("Agg")
        f = ff.MatrixField(p(0, 0), p(2, 1), DATA, normalize=True)
        f.plot_figure(tmp_path / "plot.png")
        assert (tmp_path / "plot.png").stat().st_size > 0


class TestKernelProbabilisticMatrixField:
    def test_center_keeps_the_matrix_value(self):
        k = ff.KernelProbabilisticMatrixField(p(0, 0), p(2, 1), DATA, sigma=0.3)
        m = ff.MatrixField(p(0, 0), p(2, 1), DATA)
        assert k(p(1, 0.5)) == pytest.approx(m(p(1, 0.5)))

    def test_fades_with_a_gaussian(self):
        k = ff.KernelProbabilisticMatrixField(p(0, 0), p(2, 1), DATA, sigma=0.3)
        m = ff.MatrixField(p(0, 0), p(2, 1), DATA)
        x = p(1.6, 0.5)  # 0.6 = 2 sigma from the center
        assert k(x) == pytest.approx(np.exp(-2.0) * m(x))

    def test_zero_outside(self):
        k = ff.KernelProbabilisticMatrixField(p(0, 0), p(2, 1), DATA + 1)
        assert k(p(3, 0.5)) == 0.0
