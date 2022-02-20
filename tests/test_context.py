from contextvars import ContextVar

from fiicha.context import FeatureFlagsContext
from fiicha.core import FeatureFlag, FeatureFlags


def test_ctx() -> None:
    class TestFeatureFlags(FeatureFlags):
        test = FeatureFlag("Enable test feature.")
        tset = FeatureFlag("Erutaef tset elbane.")

    root = TestFeatureFlags()
    var: ContextVar[TestFeatureFlags] = ContextVar("test", default=root)
    ff_ctx = FeatureFlagsContext(var)

    assert root is ff_ctx.current

    with ff_ctx as first:
        assert first is not root
        assert first is ff_ctx.current

        first.test = True

        assert not root.test

        with ff_ctx as second:
            assert second is not root
            assert second is not first
            assert second is ff_ctx.current

            second.tset = True

            assert root._dict() == {"test": False, "tset": False}
            assert first._dict() == {"test": True, "tset": False}
            assert second._dict() == {"test": True, "tset": True}

        assert first is ff_ctx.current
        assert root._dict() == {"test": False, "tset": False}
        assert first._dict() == {"test": True, "tset": False}

    assert root is ff_ctx.current
    assert root._dict() == {"test": False, "tset": False}
