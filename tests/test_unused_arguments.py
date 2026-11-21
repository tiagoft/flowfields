import warnings

import numpy as np
import pytest

import flowfields as ff

Z = np.zeros(2)
ONE = np.ones(2)
IMAGE = np.random.default_rng(0).uniform(size=(6, 6, 3))

# Each field with the arguments it needs
FIELDS = {
    "ScalarField": (ff.ScalarField, {}),
    "GaussianField": (ff.GaussianField, {"center": Z}),
    "ConstantField": (ff.ConstantField, {}),
    "BoxField": (ff.BoxField, {"min_corner": Z, "max_corner": ONE}),
    "MatrixField": (ff.MatrixField, {"min_corner": Z, "max_corner": ONE, "data": np.eye(3)}),
    "KernelProbabilisticMatrixField": (ff.KernelProbabilisticMatrixField,
                                       {"min_corner": Z, "max_corner": ONE, "data": np.eye(3)}),
    "FlowField": (ff.FlowField, {}),
    "RotationField": (ff.RotationField, {"center": Z}),
    "ExpansionField": (ff.ExpansionField, {"center": Z}),
    "NoiseField": (ff.NoiseField, {"rng": 0}),
    "FieldSum": (ff.FieldSum, {"fields": [ff.RotationField(Z)]}),
    "FieldMax": (ff.FieldMax, {"fields": [ff.RotationField(Z)]}),
    "FieldSelect": (ff.FieldSelect, {"fields": [ff.RotationField(Z)], "rng": 0}),
    "ColorField": (ff.ColorField, {}),
    "MatrixColorField": (ff.MatrixColorField,
                         {"min_corner": Z, "max_corner": ONE, "data": IMAGE, "n_colors": 2}),
}


@pytest.mark.parametrize("name", FIELDS)
def test_known_arguments_give_no_warning(name):
    cls, args = FIELDS[name]
    with warnings.catch_warnings():
        warnings.simplefilter("error", ff.UnusedArgumentWarning)
        cls(**args)


@pytest.mark.parametrize("name", FIELDS)
def test_unknown_arguments_warn_and_are_ignored(name):
    cls, args = FIELDS[name]
    with pytest.warns(ff.UnusedArgumentWarning, match=f"^{name} ignores the argument 'zzz'$") as record:
        cls(**args, zzz=1)
    # the warning points to the line that created the field
    assert record[0].filename == __file__


def test_several_arguments_are_listed():
    with pytest.warns(ff.UnusedArgumentWarning, match="the arguments 'sigma', 'foo'"):
        ff.RotationField(Z, sigma=2.0, foo=1)


def test_typos_get_a_suggestion():
    with pytest.warns(ff.UnusedArgumentWarning, match=r"'normalise' \(did you mean 'normalize'\?\)"):
        f = ff.RotationField(Z, normalise=False)
    assert f.normalize is True  # the typo did nothing
    with pytest.warns(ff.UnusedArgumentWarning, match=r"'weight' \(did you mean 'weights'\?\)"):
        ff.FieldSum([ff.RotationField(Z)], weight=[2.0])


def test_swapping_fields_with_the_warning_silenced():
    args = {"center": ONE, "direction": -1, "sigma": 0.5}
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any other warning still fails
        warnings.simplefilter("ignore", ff.UnusedArgumentWarning)
        for cls in (ff.RotationField, ff.ExpansionField, ff.GaussianField):
            cls(**args)


def test_is_a_user_warning():
    assert issubclass(ff.UnusedArgumentWarning, UserWarning)
