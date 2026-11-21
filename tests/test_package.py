import re
from importlib.metadata import version
from pathlib import Path

import flowfields as ff


def test_everything_in_all_exists():
    for name in ff.__all__:
        assert hasattr(ff, name), name


def test_fields_are_the_same_classes_as_in_the_submodules():
    assert ff.RotationField is ff.vector_fields.RotationField
    assert ff.GaussianField is ff.scalar_fields.GaussianField
    assert ff.MatrixColorField is ff.color_fields.MatrixColorField


def test_version_matches_the_installed_package():
    assert ff.__version__ == version("flowfields")


def test_version_matches_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    match = re.search(r'^version = "(.+)"$', pyproject.read_text(), re.MULTILINE)
    assert ff.__version__ == match.group(1)
