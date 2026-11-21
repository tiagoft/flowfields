import numpy as np
import pytest
from PIL import Image

from flowfields import utils


def p(x, y):
    return np.array([x, y], dtype=float)


VECTORS = [p(3, 4), p(-0.2, 0.7), p(-1, -1e-3), p(0.5, -2)]


def test_normalize_vector():
    assert utils.normalize_vector(p(3, 4)) == pytest.approx([0.6, 0.8])
    assert np.all(utils.normalize_vector(p(0, 0)) == 0)


@pytest.mark.parametrize("v", VECTORS)
def test_clamp_vector_keeps_the_direction(v):
    for lo, hi in [(0.5, 1.0), (2.0, 3.0), (10.0, 20.0)]:
        c = utils.clamp_vector(v, lo, hi)
        assert lo - 1e-12 <= np.linalg.norm(c) <= hi + 1e-12
        assert c == pytest.approx(utils.normalize_vector(v) * np.linalg.norm(c))


def test_clamp_vector_zero():
    assert np.all(utils.clamp_vector(p(0, 0), 1.0, 2.0) == 0)


def test_clamp_vector_inside_the_range_is_unchanged():
    assert utils.clamp_vector(p(3, 4), 1.0, 10.0) == pytest.approx([3, 4])


def test_lerp():
    a, b = p(1, 2), p(-3, 0.5)
    assert utils.lerp(a, b, 0.0) == pytest.approx(a)
    assert utils.lerp(a, b, 1.0) == pytest.approx(b)
    assert utils.lerp(a, b, 0.25) == pytest.approx([0.0, 1.625])


def test_clamp():
    assert utils.clamp(-3.0, -1.0, 2.0) == -1.0
    assert utils.clamp(0.5, -1.0, 2.0) == 0.5
    assert utils.clamp(7.0, -1.0, 2.0) == 2.0


@pytest.mark.parametrize("v", VECTORS)
def test_polar_round_trip(v):
    assert utils.polar_to_cartesian(*utils.cartesian_to_polar(v)) == pytest.approx(v)


def test_cartesian_to_polar():
    r, a = utils.cartesian_to_polar(p(0, 2))
    assert r == pytest.approx(2.0)
    assert a == pytest.approx(np.pi / 2)


@pytest.mark.parametrize("v", VECTORS)
def test_rotate_vector(v):
    assert utils.rotate_vector(v, np.pi / 2) == pytest.approx([-v[1], v[0]])
    assert utils.rotate_vector(v, 2 * np.pi) == pytest.approx(v)
    assert np.linalg.norm(utils.rotate_vector(v, 0.3)) == pytest.approx(np.linalg.norm(v))


@pytest.mark.parametrize("v", VECTORS)
@pytest.mark.parametrize("n", [3, 4, 8])
def test_quantize_vector(v, n):
    q = utils.quantize_vector(v, n)
    assert np.linalg.norm(q) == pytest.approx(np.linalg.norm(v))
    steps = np.arctan2(q[1], q[0]) / (2 * np.pi / n)
    assert steps == pytest.approx(round(steps), abs=1e-9)


def test_quantize_vector_picks_the_nearest_direction():
    assert utils.quantize_vector(p(1, 0.3), 4) == pytest.approx([np.hypot(1, 0.3), 0])
    assert utils.quantize_vector(p(0.3, 1), 4) == pytest.approx([0, np.hypot(1, 0.3)])


def test_open_image(tmp_path):
    pixels = np.zeros((4, 6, 3), dtype=np.uint8)
    pixels[:, :3] = [255, 0, 0]
    Image.fromarray(pixels).save(tmp_path / "image.png")

    rgb = utils.open_image(tmp_path / "image.png")
    assert rgb.shape == (4, 6, 3)
    assert rgb[0, 0] == pytest.approx([1, 0, 0])
    assert rgb[0, 5] == pytest.approx([0, 0, 0])

    gray = utils.open_image(tmp_path / "image.png", mode="L")
    assert gray.shape == (4, 6)
    assert 0 < gray[0, 0] < 1
