from copy import copy
from typing import Mapping, get_type_hints

from fiicha.core import FeatureFlag, FeatureFlags


def make_fake_doc(m: Mapping[str, FeatureFlag]) -> str:
    return " ".join(sorted(m))


def test_ok() -> None:
    class TestFeatureFlags(FeatureFlags, make_doc=make_fake_doc):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    assert TestFeatureFlags.__doc__ == "test tset"
    assert TestFeatureFlags.__slots__ == ("test", "tset")
    assert get_type_hints(TestFeatureFlags) == {"test": bool, "tset": bool}

    ff = TestFeatureFlags({"test": True})

    assert ff.test
    assert not ff.tset
    assert repr(ff) == "TestFeatureFlags(test=True, tset=False)"


def test_ok_all() -> None:
    class TestFeatureFlags(FeatureFlags, make_doc=make_fake_doc):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff = TestFeatureFlags({"all": True, "test": False}, default_key="all")

    assert not ff.test
    assert ff.tset


def test_subclassing() -> None:
    class Test1FeatureFlags(FeatureFlags):
        __slots__ = ("x",)
        test = FeatureFlag("Enable test feature.")
        x: int

    class Test2FeatureFlags(Test1FeatureFlags):
        tset = FeatureFlag("Erutaef tset elbane.")

    assert get_type_hints(Test2FeatureFlags) == {"test": bool, "tset": bool, "x": int}

    ff = Test2FeatureFlags({"test": True})

    assert ff.test
    assert not ff.tset
    assert repr(ff) == "Test2FeatureFlags(test=True, tset=False)"


def test_ok_no_doc_generator() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff = TestFeatureFlags({"test": True})

    assert ff.__doc__ is None


def test_ok_no_doc_override() -> None:
    class TestFeatureFlags(FeatureFlags):
        """Existing docstring."""

        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff = TestFeatureFlags({"test": True})

    assert ff.__doc__ == "Existing docstring."


def test_no_metaclass() -> None:
    class TestFeatureFlags:
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff = TestFeatureFlags()
    ff.test = True

    assert ff.test
    assert not ff.tset


def test_copy() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff_a = TestFeatureFlags()
    ff_a.test = True

    ff_b = copy(ff_a)

    assert ff_b is not ff_a
    assert ff_b.test
    assert not ff_b.tset


def test_copy_override() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff_a = TestFeatureFlags({"test": True})
    ff_b = ff_a._copy({"test": False})

    assert not ff_b.test
    assert not ff_b.tset


def test_merge() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff_a = TestFeatureFlags({"test": True})
    ff_b = TestFeatureFlags({"tset": True})
    ff_c = ff_a | ff_b

    assert ff_c is not ff_a
    assert ff_c is not ff_b
    assert ff_c.test
    assert ff_c.tset


def test_merge_in_place() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    ff_a = ff = TestFeatureFlags({"test": True})
    ff_b = TestFeatureFlags({"tset": True})
    ff_a |= ff_b

    assert ff_a is ff
    assert ff_a.test
    assert ff_a.tset
