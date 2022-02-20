from typing import Any, Mapping, Tuple

from .core import FeatureFlag

TITLE = "Feature Flags class."
DESCRIPTION = "Unknown feature flags are ignored."
ALL_FLAG_DESCRIPTION = "Enable all feature flags by default."


def by_item_name(pair: Tuple[str, Any]) -> str:
    """Get first element of the ``pair``."""
    return pair[0]


def make_napoleon_doc(feature_flags: Mapping[str, FeatureFlag]) -> str:
    """Generate Google-style docstring for the feature flags class."""

    out = [
        TITLE,
        "",
        DESCRIPTION,
        "",
        "Args:",
        f"    all: {ALL_FLAG_DESCRIPTION}",
    ]

    for name, feature_flag in sorted(feature_flags.items(), key=by_item_name):
        out.append(f"    {name}: {feature_flag.desciption}")

    out.append("")

    return "\n".join(out)


def make_sphinx_doc(feature_flags: Mapping[str, FeatureFlag]) -> str:
    """Generate Sphinx-style docstring for the feature flags class."""

    out = [
        TITLE,
        "",
        DESCRIPTION,
        "",
        f":param all: {ALL_FLAG_DESCRIPTION}",
    ]

    for name, feature_flag in sorted(feature_flags.items(), key=by_item_name):
        out.append(f":param {name}: {feature_flag.desciption}")

    out.append("")

    return "\n".join(out)
