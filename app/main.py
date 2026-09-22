from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, StringConstraints

from .docker_service import DockerAPIError, DockerConnectionError, DockerService

BASE_DIR = Path(__file__).resolve().parent
PASSWORD = os.getenv("PASSWORD", "")
AUTH_ENABLED = bool(PASSWORD)
NO_AUTH_CSRF = secrets.token_urlsafe(32)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes", "on"}
SESSION_TTL = 12 * 60 * 60
APP_VERSION = "0.1.2"
ASSET_REVISION = "7"

logger = logging.getLogger("zentdclean")

app = FastAPI(title="ZentDClean", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

sessions: dict[str, dict[str, object]] = {}
login_failures: dict[str, list[float]] = {}
LOGIN_WINDOW = 60
LOGIN_MAX_FAILURES = 8

CleanupId = Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)]
CsrfToken = Annotated[str, StringConstraints(min_length=16, max_length=128)]
CleanupKind = Literal["images", "volumes", "containers", "buildcache", "networks"]


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class CleanupRequest(BaseModel):
    kind: CleanupKind
    ids: list[CleanupId] = Field(default_factory=list, max_length=5000)
    csrf: CsrfToken


def _prune_sessions(now: float | None = None) -> None:
    current = now if now is not None else time.time()
    expired = [sid for sid, data in sessions.items() if float(data.get("expires", 0)) < current]
    for sid in expired:
        sessions.pop(sid, None)


def _prune_login_failures(now: float | None = None) -> None:
    current = now if now is not None else time.time()
    for client, attempts in list(login_failures.items()):
        recent = [ts for ts in attempts if current - ts < LOGIN_WINDOW]
        if recent:
            login_failures[client] = recent
        else:
            login_failures.pop(client, None)


def _new_session() -> tuple[str, str]:
    _prune_sessions()
    sid = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    sessions[sid] = {"csrf": csrf, "expires": time.time() + SESSION_TTL}
    return sid, csrf


def _session(request: Request) -> dict[str, object] | None:
    sid = request.cookies.get("zentdclean_session")
    if not sid:
        return None
    data = sessions.get(sid)
    if not data:
        return None
    if float(data["expires"]) < time.time():
        sessions.pop(sid, None)
        return None
    data["expires"] = time.time() + SESSION_TTL
    return data


def _require_session(request: Request) -> dict[str, object]:
    if not AUTH_ENABLED:
        return {"csrf": NO_AUTH_CSRF}
    data = _session(request)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return data


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; worker-src 'self'; manifest-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico", media_type="image/x-icon")


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(
        BASE_DIR / "static" / "manifest.webmanifest",
        media_type="application/manifest+json",
    )


@app.get("/service-worker.js", include_in_schema=False)
def service_worker():
    response = FileResponse(
        BASE_DIR / "static" / "service-worker.js",
        media_type="application/javascript",
    )
    response.headers["Service-Worker-Allowed"] = "/"
    return response


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "logged_in": (not AUTH_ENABLED) or bool(_session(request)),
            "auth_enabled": AUTH_ENABLED,
            "version": APP_VERSION,
            "asset_revision": ASSET_REVISION,
        },
    )


@app.post("/api/login")
def login(payload: LoginRequest, request: Request):
    if not AUTH_ENABLED:
        raise HTTPException(status_code=404, detail="Login disabled")
    client = request.client.host if request.client else "unknown"
    now = time.time()
    _prune_login_failures(now)
    recent = [ts for ts in login_failures.get(client, []) if now - ts < LOGIN_WINDOW]
    if len(recent) >= LOGIN_MAX_FAILURES:
        raise HTTPException(status_code=429, detail="Too many login attempts")
    candidate = hashlib.sha256(payload.password.encode()).digest()
    expected = hashlib.sha256(PASSWORD.encode()).digest()
    if not hmac.compare_digest(candidate, expected):
        recent.append(now)
        login_failures[client] = recent
        raise HTTPException(status_code=401, detail="Invalid password")
    login_failures.pop(client, None)
    sid, csrf = _new_session()
    response = JSONResponse({"ok": True, "csrf": csrf})
    response.set_cookie(
        "zentdclean_session",
        sid,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        max_age=SESSION_TTL,
        path="/",
    )
    return response


@app.post("/api/logout")
def logout(request: Request):
    if not AUTH_ENABLED:
        return {"ok": True}
    sid = request.cookies.get("zentdclean_session")
    if sid:
        sessions.pop(sid, None)
    response = JSONResponse({"ok": True})
    response.delete_cookie("zentdclean_session", path="/")
    return response


@app.get("/api/session")
def session_info(request: Request):
    data = _require_session(request)
    return {"csrf": data["csrf"]}


def _empty_docker_overview() -> dict[str, object]:
    empty = {"count": 0, "reclaimable": None, "reclaimable_complete": False, "available": False}
    return {
        "images": dict(empty),
        "volumes": dict(empty),
        "containers": dict(empty),
        "buildcache": dict(empty),
        "networks": dict(empty),
        "reclaimable_total": 0,
        "reclaimable_total_complete": False,
        "partial": True,
        "warnings": [],
    }


@app.get("/api/overview")
def overview(request: Request):
    _require_session(request)
    try:
        service = DockerService()
        docker_data = service.overview()
        return {
            "docker": {
                "available": True,
                "partial": bool(docker_data.get("partial")),
                "error": None,
                "api_version": service.api_version,
                "engine_version": service.engine_version,
            },
            **docker_data,
        }
    except DockerConnectionError as exc:
        logger.warning("Docker unavailable (%s): %s", exc.code, exc.detail or "no details")
        return {
            "docker": {"available": False, "partial": False, "error": exc.code},
            **_empty_docker_overview(),
        }
    except Exception:
        logger.exception("Unexpected Docker overview error")
        return {
            "docker": {"available": False, "partial": False, "error": "unavailable"},
            **_empty_docker_overview(),
        }


@app.get("/api/candidates/{kind}")
def candidates(kind: str, request: Request):
    _require_session(request)
    if kind not in {"all", "images", "volumes", "containers", "buildcache", "networks"}:
        raise HTTPException(status_code=404, detail="Unknown cleanup type")
    try:
        service = DockerService()
        data = service.candidates(kind)
    except DockerConnectionError as exc:
        logger.warning("Docker unavailable while loading candidates (%s): %s", exc.code, exc.detail or "no details")
        raise HTTPException(status_code=503, detail="Docker is unavailable") from exc
    except Exception as exc:
        logger.exception("Candidate loading failed")
        raise HTTPException(status_code=503, detail="Docker data could not be loaded") from exc

    if kind == "all":
        return {**data, "_unavailable": sorted(service.category_errors)}
    if kind in service.category_errors:
        raise HTTPException(status_code=503, detail="This Docker category could not be loaded")
    return {kind: data[kind]}


@app.post("/api/cleanup")
def cleanup(payload: CleanupRequest, request: Request):
    data = _require_session(request)
    if not hmac.compare_digest(str(data["csrf"]), payload.csrf):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    try:
        result = DockerService().cleanup(payload.kind, payload.ids)
    except DockerConnectionError as exc:
        logger.warning("Docker unavailable during cleanup (%s): %s", exc.code, exc.detail or "no details")
        raise HTTPException(status_code=503, detail="Docker is unavailable") from exc
    except DockerAPIError as exc:
        logger.warning("Cleanup pre-check failed (%s): %s", exc.status, exc.message)
        raise HTTPException(status_code=503, detail="Cleanup could not be completed") from exc
    except Exception as exc:
        logger.exception("Unexpected cleanup error")
        raise HTTPException(status_code=503, detail="Cleanup could not be completed") from exc
    return {"results": result}
