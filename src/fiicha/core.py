from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
)


class FeatureFlag:
    """A descriptor object to mark attribute as a feature flag.

    Args:
        description: Human-readable description of the feature flag.
    """

    def __init__(self, description: str = "") -> None:
        self.description = description

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, cls: Optional[type] = None) -> bool:
        return getattr(obj, f"_{self.name}", False)

    def __set__(self, obj: Any, value: bool) -> None:
        setattr(obj, f"_{self.name}", value)


FeatureFlags_T = TypeVar("FeatureFlags_T", bound="FeatureFlags")


class FeatureFlagsMeta(type):
    """Metaclass for the feature flags.

    Args:
        make_doc: If provided, used to generate docstring for the resulting class.
    """

    __feature_flags__: Tuple[str, ...]

    def __new__(
        cls: Type[type],
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        make_doc: Optional[Callable[[Mapping[str, FeatureFlag]], str]] = None,
        aliases: Optional[Mapping[str, str]] = None,
    ) -> type:
        feature_flags: Dict[str, FeatureFlag] = {}
        annotations: Dict[str, type] = namespace.pop("__annotations__", {})

        for ns_name, ns_attr in list(namespace.items()):
            if isinstance(ns_attr, FeatureFlag):
                feature_flags[ns_name] = ns_attr
                annotations[ns_name] = bool

                del namespace[ns_name]

        if not ("__doc__" in namespace or make_doc is None):
            namespace["__doc__"] = make_doc(feature_flags)

        if aliases:
            for name, alias in aliases.items():
                namespace[alias] = namespace[name]

        namespace["__feature_flags__"] = tuple(feature_flags)
        namespace["__slots__"] = (*namespace.get("__slots__", ()), *feature_flags)
        namespace["__annotations__"] = annotations

        # https://github.com/python/mypy/issues/9282
        return super().__new__(cls, name, bases, namespace)  # type: ignore

    def _flags(cls: type) -> Iterable[str]:
        """Iterate through all defined feature flag names."""

        for xcls in cls.mro():
            if isinstance(xcls, FeatureFlagsMeta):
                yield from xcls.__feature_flags__  # TODO: avoid duplicates


object_setattr = object.__setattr__


class FeatureFlags(
    metaclass=FeatureFlagsMeta,
    aliases={"_copy": "__copy__", "_set": "__setattr__"},
):
    __slots__: Tuple[str, ...] = ("_immutable",)
    _immutable: bool

    def __init__(
        self,
        values: Optional[Mapping[str, bool]] = None,
        default: bool = False,
        default_key: str = "",
        immutable: bool = False,
    ) -> None:
        """Initialize feature flags.

        Unknown feature flags are ignored.

        Args:
            values: Feature flag states.
            default: Default state for unset feature flags.
            default_key: Key from ``values`` with default value for unset flags.
        """

        names = set(self.__class__._flags())

        if values:
            if default_key:
                default = values.get(default_key, default)

            for name in names:
                object_setattr(self, name, values.get(name, default))
        else:
            for name in names:
                object_setattr(self, name, default)

        object_setattr(self, "_immutable", immutable)

    def _freeze(self) -> None:
        """Make this feature flags immutable."""

        object_setattr(self, "_immutable", True)

    def _set(self, name: str, value: bool) -> None:
        """Set feature flag value.

        Args:
            name: Feature flag name.
            value: Feature flag state.
        """

        if self._immutable:
            raise RuntimeError("this instance is immutable")

        object_setattr(self, name, value)

    def _dict(self) -> Dict[str, bool]:
        """Get copy of the feature flags in a form of dictionary."""

        return {name: getattr(self, name) for name in self.__class__._flags()}

    def _copy(
        self: FeatureFlags_T,
        overrides: Optional[Mapping[str, bool]] = None,
        immutable: Optional[bool] = None,
    ) -> FeatureFlags_T:
        """Get copy of the feature flags object.

        Args:
            overrides: Feature flag states to override.
            immutable: Set immutable flag for new copy. If unset, value is
                carried over from the current object.
        """

        values = self._dict()

        if overrides:
            values.update(overrides)

        return self.__class__(
            values,
            immutable=self._immutable if immutable is None else immutable,
        )

    def __or__(self: FeatureFlags_T, other: FeatureFlags_T) -> FeatureFlags_T:
        """Merge feature flags."""

        return self.__class__(
            {
                name: getattr(self, name) or getattr(other, name)
                for name in self.__class__._flags()
            },
            immutable=self._immutable,
        )

    def __ior__(self: FeatureFlags_T, other: FeatureFlags_T) -> FeatureFlags_T:
        """Merge feature flags in-place."""

        if self._immutable:
            return self.__or__(other)

        for name in self.__class__._flags():
            if getattr(other, name):
                object_setattr(self, name, True)

        return self

    def __delattr__(self, name: str) -> NoReturn:
        raise TypeError("feature flags are not deletable")

    def __repr__(self) -> str:
        """Return string representation of the feature flags object."""

        cls = self.__class__
        params = ", ".join(
            f"{name}={repr(getattr(self, name))}" for name in sorted(set(cls._flags()))
        )
        return f"{cls.__name__}({params})"
