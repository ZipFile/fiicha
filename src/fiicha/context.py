from contextlib import ContextDecorator
from contextvars import ContextVar, Token
from typing import Any, Generic, List, Optional

from .core import FeatureFlags_T


class FeatureFlagsContext(ContextDecorator, Generic[FeatureFlags_T]):
    """A context manager wrapper around ``ContextVar[FeatureFlags]``.

    Args:
        var: Context variable with default flags set.
        immutable: Defines value of the immutable flag when copying feature
            flags. When unset, preserves existing value.
    """

    __slots__ = ("tokens", "var", "immutable")
    tokens: List["Token[FeatureFlags_T]"]
    var: ContextVar[FeatureFlags_T]
    immutable: Optional[bool]

    def __init__(
        self, var: ContextVar[FeatureFlags_T], immutable: Optional[bool] = None
    ) -> None:
        self.tokens = []
        self.var = var
        self.immutable = immutable

    def __enter__(self) -> FeatureFlags_T:
        """Set copy of the feature flags as the new context variable."""

        feature_flags = self.var.get()._copy(immutable=self.immutable)

        self.tokens.append(self.var.set(feature_flags))

        return feature_flags

    def __exit__(self, *exc: Any) -> None:
        """Restore previous value of the context variable."""

        self.var.reset(self.tokens.pop())

    def get_current(self) -> FeatureFlags_T:
        """Get feature flags from the current context."""

        return self.var.get()

    current = property(get_current)
