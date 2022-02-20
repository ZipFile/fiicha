from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
)


class FeatureFlag:
    """A descriptor object to mark attribute as a feature flag.

    Args:
        desciption: Human-readable description of the feature flag.
    """

    def __init__(self, description: str = "") -> None:
        self.desciption = description

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

        namespace["__feature_flags__"] = tuple(feature_flags)
        namespace["__slots__"] = tuple(feature_flags)  # TODO: merge slots
        namespace["__annotations__"] = annotations

        # https://github.com/python/mypy/issues/9282
        return super().__new__(cls, name, bases, namespace)  # type: ignore

    def _flags(cls: type) -> Iterable[str]:
        """Iterate through all defined feature flag names."""

        for xcls in cls.mro():
            if isinstance(xcls, FeatureFlagsMeta):
                yield from xcls.__feature_flags__  # TODO: avoid duplicates


class FeatureFlags(metaclass=FeatureFlagsMeta):
    def __init__(
        self,
        values: Optional[Mapping[str, bool]] = None,
        default: bool = False,
        default_key: str = "",
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
                setattr(self, name, values.get(name, default))
        else:
            for name in names:
                setattr(self, name, default)

    def _dict(self) -> Dict[str, bool]:
        """Get copy of the feature flags in a form of dictionary."""

        return {name: getattr(self, name) for name in self.__class__._flags()}

    def _copy(
        self: FeatureFlags_T, overrides: Optional[Mapping[str, bool]] = None
    ) -> FeatureFlags_T:
        """Get copy of the feature flags object.

        Args:
            overrides: Feature flag states to override.
        """

        values = self._dict()

        if overrides:
            values.update(overrides)

        return self.__class__(values)

    __copy__ = _copy

    def __or__(self: FeatureFlags_T, other: FeatureFlags_T) -> FeatureFlags_T:
        """Merge feature flags."""

        return self.__class__(
            {
                name: getattr(self, name) or getattr(other, name)
                for name in self.__class__._flags()
            }
        )

    def __ior__(self: FeatureFlags_T, other: FeatureFlags_T) -> FeatureFlags_T:
        """Merge feature flags in-place."""

        for name in self.__class__._flags():
            if getattr(other, name):
                setattr(self, name, True)

        return self

    def __repr__(self) -> str:
        """Return string representation of the feature flags object."""

        cls = self.__class__
        params = ", ".join(
            f"{name}={repr(getattr(self, name))}" for name in sorted(set(cls._flags()))
        )
        return f"{cls.__name__}({params})"
