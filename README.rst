======
Fiicha
======

Fiicha is minimalistic mypy-friendly feature flag implementation with no
external dependencies.

Installation
============

.. code-block:: sh

    pip install fiicha

For Development
---------------

Clone the repo, change current working dir to the root of the repo and execute:

.. code-block:: sh

    python -m venv env
    . env/bin/activate
    pip install -e .[test,lint]

Usage
=====

Basic
-----

Basic usage is simple:

1. Sublcass from ``FeatureFlags``
2. Add ``FeatureFlag`` attributes representing individual feature flags.

.. code-block:: python

    from fiicha import FeatureFlag, FeatureFlags

    class MyProjectFeatureFlags(FeatureFlags):
        release_x = FeatureFlag("Enable features from upcoming release X")
        use_new_algorithm = FeatureFlag("Use new algorithm for ...")

    ff = MyProjectFeatureFlags({"release_x": True})

    print(ff.release_x)  # True
    print(ff.use_new_algorithm)  # False


In addition, you kan specify a key defining default state of the feature flags:

.. code-block:: python

    ff = MyProjectFeatureFlags({"all": True, "release_x": False}, default_key="all")

    print(ff.release_x)  # False
    print(ff.use_new_algorithm)  # True

Classes subclassed from ``FeatureFlags`` has full type hint support, so
when you are accessing removed or otherwise non-existent feature flags, you
can detect it before running tests:

.. code-block:: python

    ff.xxx  # will trigger mypy's attr-defined error


Utils
-----

The package comes with few util functions to avoid building your own framework
for simple use cases.


Single-line Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fiicha import parse_feature_flags_string

    flags_string = "release_x !use_new_algorithm"  # stored in config
    ff = MyProjectFeatureFlags(parse_feature_flags_string(flags_string))

    print(ff.release_x)  # True
    print(ff.use_new_algorithm)  # False

Load Flags From Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import os
    from fiicha import feature_flags_from_environ

    os.environ["MYPROJ_FEATURE_RELEASE_X"] = "True"  # can also be 1, t, yes, on
    os.environ["MYPROJ_FEATURE_USE_NEW_ALGORITHM"] = "False"  # can also be 0, f, no, off or empty string

    ff = MyProjectFeatureFlags(feature_flags_from_environ("MYPROJ_FEATURE_"))

    print(ff.release_x)  # True
    print(ff.use_new_algorithm)  # False

Automatically Document Your Feature Flags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fiicha import make_napoleon_doc, make_sphinx_doc

    class GoogleStyleDocFeatureFlags(FeatureFlags, make_doc=make_napoleon_doc):
        a = FeatureFlag("Enable feature A")
        b = FeatureFlag("Enable feature B")

    class SphinxStyleDocFeatureFlags(FeatureFlags, make_doc=make_sphinx_doc):
        x = FeatureFlag("Enable feature X")
        y = FeatureFlag("Enable feature Y")

    print(GoogleStyleDocFeatureFlags.__doc__)
    print(SphinxStyleDocFeatureFlags.__doc__)

Context Variable Support
~~~~~~~~~~~~~~~~~~~~~~~~

You might want to do A/B testing or otherwise toggle feature flags for
individual users without affecting the rest of the system. For such cases,
there is ``FeatureFlagsContext`` - a wrapper around ``ContextVar``. It copies
current feature flags and sets them as new context variable on enter and
resets them back on exit. This way you will be able to achieve global feature
flags protection from changes made within context of a request or a task.

.. code-block:: python

    from contextvars import ContextVar
    from fiicha import FeatureFlag, FeatureFlags, FeatureFlagsContext

    class MyFeatureFlags(FeatureFlags):
        a = FeatureFlag("Enable feature A")
        b = FeatureFlag("Enable feature B")

    root = MyFeatureFlags()
    var: ContextVar[MyFeatureFlags] = ContextVar("test", default=root)
    ff_ctx = FeatureFlagsContext(var)

    with ff_ctx:
        ff = var.get()
        ff.a = True

        assert ff is not root  # is a copy

    assert not root.a  # not changed

Advanced
--------

See ``examples`` subfolder within the repo.
