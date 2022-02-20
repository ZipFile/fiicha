from os import environ
from typing import Iterable, Mapping, Optional, Tuple


def parse_feature_flags_string(
    s: Optional[str], /, sep: Optional[str] = None, neg: str = "!"
) -> Mapping[str, bool]:
    """Parse feature flags string into mapping name -> value.

    >>> parse_feature_flag_string("a !b")
    {'a': True, 'b': False}
    """
    if not s:
        return {}

    return {flag.lstrip(neg): not flag.startswith(neg) for flag in s.split(sep)}


def parse_bool(s: str) -> Optional[bool]:
    """Parse string as boolean.

    Values ``1, ``true``, ``t``, ``yes``, ``y``, ``on`` are parsed as ``True``.
    Values ``0``, ``false``, ``f``, ``no``, ``n``, ``off`` and empty string
    are parsed as ``False``. If none maches, return ``None``. Matching is
    case-insensitive, whitespaces at the beginning and at the end are stripped
    before performing the match.
    """

    s = s.strip().lower()

    if s in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "f", "no", "n", "off", ""}:
        return False
    return None


def _feature_flags_from_environ(
    prefix: str,
    environ: Mapping[str, str],
) -> Iterable[Tuple[str, bool]]:
    """See :func:`feature_flags_from_environ`."""

    prefix_len = len(prefix)
    for key, value in environ.items():
        if key.startswith(prefix):
            parsed_value = parse_bool(value)
            if parsed_value is not None:
                yield key[prefix_len:].lower(), parsed_value


def feature_flags_from_environ(
    prefix: str,
    environ: Mapping[str, str] = environ,
) -> Mapping[str, bool]:
    """Extract feature flags mapping (name -> value) from env variables.

    Iterate through all environment variables matching given ``prefix``,
    try to parse them as bool. Resulting mapping keys are stripped from the
    ``prefix`` and transformed to lowercase. Values that does not look like a
    bool are ignored.

    Note:
        :func:`parse_bool` is used for parsing values.

    Args:
        prefix: Case sensitive Env variable prefix (e.g. ``MYPROJ_FEATURE_``).
        environ: Mapping with environment variables (defaults to ``os.environ``).
    """

    return dict(_feature_flags_from_environ(prefix, environ))
