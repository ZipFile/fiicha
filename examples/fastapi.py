# Install dependencies:
#    pip install fastapi uvicorn[standard]
# Run:
#    FEATURE_USE_NEW_GREETING=0 uvicorn examples.fastapi:app --reload
#    FEATURE_USE_NEW_GREETING=1 uvicorn examples.fastapi:app --reload
# Test:
#    curl "http://localhost:8000/?name=$USER" -u test:
#    curl "http://localhost:8000/?name=$USER" -u anon:

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


ff = MyFeatureFlags(feature_flags_from_environ("FEATURE_"))
ff_var = ContextVar("ff", default=ff)
ff_ctx = FeatureFlagsContext(ff_var)
security = HTTPBasic()


def ab_testing(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    """Enables features for select users (a.k.a. A/B testing)."""

    feature_flags = ff_var.get()

    # enable new greeting for "50%" of users
    feature_flags.use_new_greeting |= ord(credentials.username[0]) % 2 == 0


app = FastAPI(dependencies=[Depends(ab_testing)])


@app.middleware("http")
async def feature_flags_scope_per_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Use new feature flags copy for each request."""

    with ff_ctx as feature_flags:
        request.scope["feature_flags"] = feature_flags

        return await call_next(request)


@app.get("/")
def greet(name: str = "anonymous") -> Dict[str, str]:
    feature_flags = ff_var.get()

    if feature_flags.use_new_greeting:
        return {"message": f"Ohayou {name}-chan! *kira*"}
    return {"message": f"Hello, {name}!"}
