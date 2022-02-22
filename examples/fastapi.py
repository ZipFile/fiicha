# Install dependencies:
#    pip install fastapi uvicorn[standard]
# Run:
#    FEATURE_USE_NEW_GREETING=0 uvicorn examples.fastapi:app --reload
#    FEATURE_USE_NEW_GREETING=1 uvicorn examples.fastapi:app --reload
# Test:
#    curl "http://127.0.0.1:8000/?name=$(id -un)" -u test:
#    curl "http://127.0.0.1:8000/?name=$(id -un)" -u anon:

from contextvars import ContextVar
from typing import Awaitable, Callable, Dict

from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from fiicha import (
    FeatureFlag,
    FeatureFlags,
    FeatureFlagsContext,
    feature_flags_from_environ,
)


class MyFeatureFlags(FeatureFlags):
    use_new_greeting = FeatureFlag("Greet users better")
    # ^ Add more here.


ff = MyFeatureFlags(
    feature_flags_from_environ("FEATURE_"),
    immutable=True, # Prevent system-wide feature flags from changes.
)
ff_var = ContextVar("ff", default=ff)
ff_ctx = FeatureFlagsContext(
    ff_var,
    # Make context-local feature flags mutable to enable a/b testing or other
    # forms of conditional feature flag toggling (e.g. based on headers).
    immutable=False,
)
security = HTTPBasic()

# Workaround for FastAPI. You cannot use `ff_var.get` as an argument to
# `Depends` directly, since it calls `inspect.signature` under the hood which
# fails because `ContextVar.get` is a builtin (C) function without signature.
def get_feature_flags() -> MyFeatureFlags:
    return ff_var.get()


def ab_testing(
    credentials: HTTPBasicCredentials = Depends(security),
    # Fetch feature flags from the context variable set by
    # "feature_flags_scope_per_request" middleware.
    feature_flags: MyFeatureFlags = Depends(get_feature_flags),
) -> None:
    """Enables features for select users (a.k.a. A/B testing)."""

    # Enable new greeting for "50%" of users.
    feature_flags.use_new_greeting |= ord(credentials.username[0]) % 2 == 0

    # Make sure nothing changes feature flags afterward.
    feature_flags._freeze()


app = FastAPI(dependencies=[Depends(ab_testing)])


@app.middleware("http")
async def feature_flags_scope_per_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Use new feature flags copy for each request."""

    # Create new copy of the feature flags, as we'll be modifying them later
    # and do not want to change our system-wide feature flags.
    with ff_ctx as feature_flags:
        # FastAPI provides its own dependency injection mechanism, but just
        # in case you are using starlette directly or there any other pure
        # ASGI middlewares.
        request.scope["feature_flags"] = feature_flags

        return await call_next(request)


@app.get("/")
def greet(
    name: str = "anonymous",  # query param
    feature_flags: MyFeatureFlags = Depends(get_feature_flags),
) -> Dict[str, str]:
    if feature_flags.use_new_greeting:
        return {"message": f"Ohayou {name}-chan! *kira*"}
    return {"message": f"Hello, {name}!"}
