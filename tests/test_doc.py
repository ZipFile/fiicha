from typing import Mapping

from pytest import fixture

from fiicha.core import FeatureFlag
from fiicha.doc import make_napoleon_doc, make_sphinx_doc


@fixture
def feature_flags() -> Mapping[str, FeatureFlag]:
    return {
        "test": FeatureFlag("Enable test feature."),
        "tset": FeatureFlag("Erutaef tset elbane."),
    }


def test_make_napoleon_doc(feature_flags: Mapping[str, FeatureFlag]) -> None:
    assert make_napoleon_doc(feature_flags) == (
        "Feature Flags class.\n\n"
        "Unknown feature flags are ignored.\n\n"
        "Args:\n"
        "    values: Feature flag states.\n"
        "    default: Default state for unset feature flags.\n"
        "    default_key: Key from ``values`` with default value for unset flags.\n\n"
        "Attributes:\n"
        "    test: Enable test feature.\n"
        "    tset: Erutaef tset elbane.\n"
    )


def test_make_sphinx_doc(feature_flags: Mapping[str, FeatureFlag]) -> None:
    assert make_sphinx_doc(feature_flags) == (
        "Feature Flags class.\n\n"
        "Unknown feature flags are ignored.\n\n"
        ":param values: Feature flag states.\n"
        ":param default: Default state for unset feature flags.\n"
        ":param default_key: Key from ``values`` with default value for unset flags.\n"
        ":var test: Enable test feature.\n"
        ":var tset: Erutaef tset elbane.\n"
    )
