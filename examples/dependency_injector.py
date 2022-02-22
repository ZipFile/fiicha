#!/usr/bin/env python

# Install dependencies:
#     pip install dependency-injector
# Run:
#     FEATURES="use_new_greeter" python -m examples.dependency_injector $(id -un)
#     FEATURES="-use_new_greeter" python -m examples.dependency_injector $(id -un)

import sys
from abc import ABCMeta
from typing import List

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Selector, Singleton

from fiicha import FeatureFlag, FeatureFlags, parse_feature_flags_string


class Greeter(metaclass=ABCMeta):
    def greet(self, name: str) -> None:
        ...


class OldGreeter(Greeter):
    def greet(self, name: str) -> None:
        print(f"Hello, {name}!")


class NewGreeter(Greeter):
    def greet(self, name: str) -> None:
        print(f"Ohayou {name}-chan! *kira*")


class MyFeatureFlags(FeatureFlags):
    use_new_greeter = FeatureFlag("Use new greeter implementation")
    # ^ Add more here.

    # Not reinventing the wheel. While it is possible to implement your own
    # provider to select one or another factory based on the boolean flag,
    # sometimes it is not worth the effort. `Selector` provider is good enough
    # for the job.
    def _di_selector(self, name: str) -> str:
        if getattr(self, name):
            return "enabled"
        return "disabled"


class Container(DeclarativeContainer):
    config = Configuration()
    # Parsing string like "a -b c" from config into dict like
    # `{"a": True, "b": False, "c": True}`.
    parsed_flags = Factory(
        parse_feature_flags_string,
        config.features,
        # Flags prefixed with "-" will be considered disabled.
        neg="-",
    )
    feature_flags = Singleton(
        MyFeatureFlags,
        parsed_flags,
        # If key "all" is present, all unspecified feature flags will be
        # enabled by default.
        default_key="all",
        # Since this is a singleton, guard ourselves from external changes.
        immutable=True,
    )
    greeter = Selector(
        # `Selector` provider accepts callable returning name of the provider
        # to use. In our case we have two providers named "enabled" and
        # "disabled" and the selector callable which supposed to return one of
        # two possible values. We cannot use `MyFeatureFlags._di_selector`
        # directly (`feature_flags` above is a provider too, not an instance of
        # `MyFeatureFlags`). Likely, dependency-injector provides its own way
        # to access instance attributes. Following notation will produce a
        # callable that will access `feature_flags` instance attribute
        # `_di_selector` and will attempt to call it with "use_new_greeter"
        # argument.
        feature_flags.provided._di_selector.call("use_new_greeter"),
        enabled=Factory(NewGreeter),
        disabled=Factory(OldGreeter),
    )


def main(argv: List[str]) -> None:
    container = Container()

    container.config.features.from_env("FEATURES", "")

    greeter = container.greeter()

    for name in argv[1:]:
        greeter.greet(name)


if __name__ == "__main__":
    main(sys.argv)
