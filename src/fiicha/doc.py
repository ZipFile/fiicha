from typing import Any, Mapping, Tuple

from .core import FeatureFlag

TITLE = "Feature Flags class."
DESCRIPTION = "Unknown feature flags are ignored."
INIT_ARGS = (
    ("values", "Feature flag states."),
    ("default", "Default state for unset feature flags."),
    ("default_key", "Key from ``values`` with default value for unset flags."),
)


def by_item_name(pair: Tuple[str, Any]) -> str:
    """Get first element of the ``pair``."""
    return pair[0]


def make_napoleon_doc(feature_flags: Mapping[str, FeatureFlag]) -> str:
    """Generate Google-style docstring for the feature flags class."""

    return "\n".join(
        [
            TITLE,
            "",
            DESCRIPTION,
            "",
            "Args:",
            *(f"    {name}: {description}" for name, description in INIT_ARGS),
            "",
            "Attributes:",
            *(
                f"    {name}: {feature_flag.description}"
                for name, feature_flag in sorted(
                    feature_flags.items(), key=by_item_name
                )
            ),
            "",
        ]
    )


def make_sphinx_doc(feature_flags: Mapping[str, FeatureFlag]) -> str:
    """Generate Sphinx-style docstring for the feature flags class."""

    return "\n".join(
        [
            TITLE,
            "",
            DESCRIPTION,
            "",
            *(f":param {name}: {description}" for name, description in INIT_ARGS),
            *(
                f":var {name}: {feature_flag.description}"
                for name, feature_flag in sorted(
                    feature_flags.items(), key=by_item_name
                )
            ),
            "",
        ]
    )
