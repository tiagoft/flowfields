import numpy as np
import pytest

import flowfields as ff


def p(x, y):
    return np.array([x, y], dtype=float)


C = p(0.37, 0.11)
POINTS = [p(1.0, 0.0), p(-0.5, 0.8), p(2.0, -3.0), p(0.4, 0.1)]


class TestRotationField:
    @pytest.mark.parametrize("x", POINTS)
    def test_perpendicular_to_the_radius(self, x):
        v = ff.RotationField(C)(x)
        assert np.dot(v, x - C) == pytest.approx(0.0, abs=1e-12)
        assert np.linalg.norm(v) == pytest.approx(1.0)

    def test_counter_clockwise_and_clockwise(self):
        x = p(1.0, 0.0)
        assert ff.RotationField(p(0, 0))(x) == pytest.approx([0.0, 1.0])
        assert ff.RotationField(p(0, 0), direction=-1)(x) == pytest.approx([0.0, -1.0])

    def test_length_is_the_distance_without_normalize(self):
        x = p(3.0, 4.0)
        v = ff.RotationField(p(0, 0), normalize=False)(x)
        assert v == pytest.approx([-4.0, 3.0])

    def test_center_gives_zero_not_nan(self):
        v = ff.RotationField(C)(C.copy())
        assert np.all(v == 0)


class TestExpansionField:
    @pytest.mark.parametrize("x", POINTS)
    def test_parallel_to_the_radius(self, x):
        v = ff.ExpansionField(C)(x)
        r = x - C
        assert v == pytest.approx(r / np.linalg.norm(r))

    def test_inward(self):
        x = p(2.0, 0.0)
        assert ff.ExpansionField(p(0, 0), direction=-1)(x) == pytest.approx([-1.0, 0.0])
        assert ff.ExpansionField(p(0, 0), direction=-1, normalize=False)(x) == pytest.approx([-2.0, 0.0])

    def test_center_gives_zero_not_nan(self):
        assert np.all(ff.ExpansionField(C)(C.copy()) == 0)


class TestNoiseField:
    @pytest.mark.parametrize("distribution", ["gaussian", "uniform"])
    def test_same_seed_same_draws(self, distribution):
        a = ff.NoiseField(distribution=distribution, rng=3)
        b = ff.NoiseField(distribution=distribution, rng=3)
        for _ in range(10):
            assert np.array_equal(a(C), b(C))

    def test_different_seeds_differ(self):
        assert not np.array_equal(ff.NoiseField(rng=1)(C), ff.NoiseField(rng=2)(C))

    def test_accepts_a_generator(self):
        rng = np.random.default_rng(0)
        assert ff.NoiseField(rng=rng).rng is rng

    def test_unit_length_by_default(self):
        f = ff.NoiseField(rng=0)
        for _ in range(20):
            assert np.linalg.norm(f(C)) == pytest.approx(1.0)

    def test_uniform_raw_stays_in_the_square(self):
        f = ff.NoiseField(distribution="uniform", normalize=False, rng=0)
        draws = np.array([f(C) for _ in range(500)])
        assert np.all(np.abs(draws) <= 1.0)

    def test_gaussian_raw_has_unit_variance(self):
        f = ff.NoiseField(normalize=False, rng=0)
        draws = np.array([f(C) for _ in range(5000)])
        assert draws.mean(axis=0) == pytest.approx([0, 0], abs=0.05)
        assert draws.var(axis=0) == pytest.approx([1, 1], rel=0.06)

    def test_unknown_distribution(self):
        with pytest.raises(ValueError):
            ff.NoiseField(distribution="foo")


ROT = ff.RotationField(p(0, 0), normalize=False)
EXP = ff.ExpansionField(p(1, 0), normalize=False)


class TestFieldSum:
    @pytest.mark.parametrize("x", POINTS)
    def test_fixed_weights(self, x):
        f = ff.FieldSum([ROT, EXP], weights=[1.0, 0.3], normalize=False)
        assert f(x) == pytest.approx(1.0 * ROT(x) + 0.3 * EXP(x))

    @pytest.mark.parametrize("x", POINTS)
    def test_scalar_field_weights(self, x):
        g = ff.GaussianField(p(0, 0), sigma=0.8)
        f = ff.FieldSum([ROT, EXP], weights=[g, ff.ConstantField(0.5)], normalize=False)
        assert f(x) == pytest.approx(g(x) * ROT(x) + 0.5 * EXP(x))

    def test_no_weights_is_the_plain_sum(self):
        x = p(0.2, 0.9)
        assert ff.FieldSum([ROT, EXP], normalize=False)(x) == pytest.approx(ROT(x) + EXP(x))

    def test_normalize(self):
        assert np.linalg.norm(ff.FieldSum([ROT, EXP])(p(0.2, 0.9))) == pytest.approx(1.0)

    def test_nested(self):
        inner = ff.FieldSum([ROT, EXP], weights=[1.0, 2.0], normalize=False)
        outer = ff.FieldSum([inner, ROT], weights=[0.5, 1.0], normalize=False)
        x = p(-0.3, 0.4)
        assert outer(x) == pytest.approx(0.5 * (ROT(x) + 2.0 * EXP(x)) + ROT(x))


class TestFieldMax:
    def test_highest_fixed_weight_wins(self):
        f = ff.FieldMax([ROT, EXP], weights=[0.2, 0.9], normalize=False)
        x = p(0.2, 0.9)
        assert f(x) == pytest.approx(EXP(x))

    def test_scalar_weights_change_the_winner_across_space(self):
        weights = [ff.GaussianField(p(-1, 0), sigma=0.5), ff.GaussianField(p(1, 0), sigma=0.5)]
        f = ff.FieldMax([ROT, EXP], weights=weights, normalize=False)
        assert f(p(-1, 0.1)) == pytest.approx(ROT(p(-1, 0.1)))
        assert f(p(1, 0.1)) == pytest.approx(EXP(p(1, 0.1)))

    def test_no_weights_the_first_field_wins(self):
        x = p(0.2, 0.9)
        assert ff.FieldMax([ROT, EXP], normalize=False)(x) == pytest.approx(ROT(x))

    def test_ties_go_to_the_first_field(self):
        x = p(0.2, 0.9)
        assert ff.FieldMax([ROT, EXP], weights=[0.5, 0.5], normalize=False)(x) == pytest.approx(ROT(x))


class TestFieldSelect:
    def test_output_comes_from_the_fields(self):
        f = ff.FieldSelect([ff.RotationField(p(0, 0)), ff.ExpansionField(p(0, 0))],
                           change_id_prob=0.5, rng=0)
        x = p(0.3, 0.4)
        allowed = [ff.RotationField(p(0, 0))(x), ff.ExpansionField(p(0, 0))(x)]
        for _ in range(50):
            v = f(x)
            assert any(np.allclose(v, a) for a in allowed)

    def test_same_seed_same_sequence(self):
        def run(seed):
            f = ff.FieldSelect([ROT, EXP, ff.RotationField(p(1, 1))], change_id_prob=0.3,
                               lerp_len=3, select_n=2, rng=seed)
            return [f(x) for x in POINTS * 10]

        assert np.allclose(run(5), run(5))
        assert not np.allclose(run(5), run(6))

    def test_all_zero_weights_do_not_crash(self):
        f = ff.FieldSelect([ROT, EXP], weights=[0.0, 0.0], change_id_prob=1.0, rng=0)
        for x in POINTS:
            assert np.all(np.isfinite(f(x)))

    def test_zero_weight_fields_are_never_selected(self):
        f = ff.FieldSelect([ROT, EXP], weights=[0.0, 1.0], select_n=2, rng=0)
        for x in POINTS:
            assert f.select_index(x).tolist() == [1]

    def test_unit_length(self):
        f = ff.FieldSelect([ROT, EXP], change_id_prob=0.5, lerp_len=4, rng=1)
        for x in [p(-0.5, 0.8), p(2.0, -3.0), p(0.4, 0.1)] * 5:  # away from the centers
            assert np.linalg.norm(f(x)) == pytest.approx(1.0)

    def test_lerp_blends_between_fields(self):
        rot, exp = ff.RotationField(p(0, 0)), ff.ExpansionField(p(0, 0))
        f = ff.FieldSelect([rot, exp], change_id_prob=0.0, lerp_len=4, normalize=False, rng=0)
        # Start on the rotation, force a switch to the expansion and follow
        # the transition
        f.last_idx = [0]
        f.current_field = ff.FieldSum(fields=[rot])
        f.next_field = ff.FieldSum(fields=[exp])
        x = p(1.0, 0.0)
        steps = [f(x) for _ in range(6)]
        for t, v in zip([0.0, 0.25, 0.5, 0.75], steps):
            assert v == pytest.approx((1 - t) * rot(x) + t * exp(x))
        # the transition ends on the new field, with no step back to the old one
        assert steps[4] == pytest.approx(exp(x))
        assert steps[5] == pytest.approx(exp(x))

    def test_without_lerp_the_switch_is_immediate(self):
        rot, exp = ff.RotationField(p(0, 0)), ff.ExpansionField(p(0, 0))
        f = ff.FieldSelect([rot, exp], change_id_prob=0.0, normalize=False, rng=0)
        f.last_idx = [0]
        f.current_field = ff.FieldSum(fields=[rot])
        f.next_field = ff.FieldSum(fields=[exp])
        x = p(1.0, 0.0)
        assert f(x) == pytest.approx(exp(x))

    def test_zero_weight_field_is_not_active_at_the_start(self):
        rot, exp = ff.RotationField(p(0, 0)), ff.ExpansionField(p(0, 0))
        for seed in range(10):
            f = ff.FieldSelect([rot, exp], weights=[1.0, 0.0], change_id_prob=0.0, rng=seed)
            assert f(p(1.0, 0.0)) == pytest.approx(rot(p(1.0, 0.0)))

    def test_first_selection_uses_the_weights_at_the_first_point(self):
        weights = [ff.GaussianField(p(-1, 0), sigma=0.3), ff.GaussianField(p(1, 0), sigma=0.3)]
        for seed in range(10):
            f = ff.FieldSelect([ROT, EXP], weights=weights, change_id_prob=0.0, rng=seed)
            f(p(1, 0.1))  # far from the first Gaussian: its weight is ~1e-10
            assert f.last_idx == [1]
