#!/usr/bin/env python

# Install dependencies:
#     pip install dependency-injector
# Run:
#     FEATURES="use_new_greeter" python -m examples.dependency_injector $USER
#     FEATURES="-use_new_greeter" python -m examples.dependency_injector $USER

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

    def _di_selector(self, name: str) -> str:
        if getattr(self, name):
            return "enabled"
        return "disabled"


class Container(DeclarativeContainer):
    config = Configuration()
    _parsed_flags = Singleton(
        parse_feature_flags_string,
        config.features,
        neg="-",
    )
    feature_flags = Singleton(
        MyFeatureFlags,
        _parsed_flags,
        default_key="all",
    )
    greeter = Selector(
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
