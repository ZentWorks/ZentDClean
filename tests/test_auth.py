from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.main as main

client = TestClient(main.app)


def test_no_password_disables_login(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", False)
    response = client.get("/")
    assert response.status_code == 200
    assert 'data-auth-enabled="0"' in response.text
    assert 'data-logged-in="1"' in response.text
    session = client.get("/api/session")
    assert session.status_code == 200
    assert session.json()["csrf"]


def test_password_enables_login(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", True)
    monkeypatch.setattr(main, "PASSWORD", "secret-test-password")
    main.sessions.clear()
    main.login_failures.clear()

    assert client.get("/api/session").status_code == 401
    assert client.post("/api/login", json={"password": "wrong"}).status_code == 401
    success = client.post("/api/login", json={"password": "secret-test-password"})
    assert success.status_code == 200
    assert success.json()["csrf"]
    assert client.get("/api/session").status_code == 200


def test_login_prunes_expired_failures_for_other_clients(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", True)
    monkeypatch.setattr(main, "PASSWORD", "secret-test-password")
    main.sessions.clear()
    main.login_failures.clear()

    now = 10_000.0
    monkeypatch.setattr(main.time, "time", lambda: now)
    main.login_failures["stale-client"] = [now - main.LOGIN_WINDOW - 1]
    main.login_failures["active-client"] = [now - main.LOGIN_WINDOW - 2, now - 1]

    response = client.post("/api/login", json={"password": "wrong"})

    assert response.status_code == 401
    assert "stale-client" not in main.login_failures
    assert main.login_failures["active-client"] == [now - 1]


def test_https_cookie_hardening_can_be_enabled(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", True)
    monkeypatch.setattr(main, "PASSWORD", "secret-test-password")
    monkeypatch.setattr(main, "COOKIE_SECURE", True)
    main.sessions.clear()
    main.login_failures.clear()
    client.cookies.clear()

    response = client.post("/api/login", json={"password": "secret-test-password"})
    assert response.status_code == 200
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=strict" in cookie


def test_health_is_independent_from_docker():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_overview_stays_available_when_docker_is_down(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", False)

    class BrokenDocker:
        def __init__(self):
            raise main.DockerConnectionError("socket_missing", "missing in test")

    monkeypatch.setattr(main, "DockerService", BrokenDocker)
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "disk" not in data
    assert data["docker"]["available"] is False
    assert data["docker"]["error"] == "socket_missing"
    assert data["reclaimable_total"] == 0


def test_cleanup_request_limits_are_enforced(monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", False)
    too_long_id = "x" * 256
    response = client.post("/api/cleanup", json={"kind": "images", "ids": [too_long_id], "csrf": main.NO_AUTH_CSRF})
    assert response.status_code == 422


def test_security_headers_and_static_cache():
    page = client.get("/")
    assert page.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    assert page.headers["cache-control"] == "no-store"

    static = client.get("/static/app.css?v=1")
    assert static.status_code == 200
    assert "immutable" in static.headers["cache-control"]


def test_favicon_exists():
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/x-icon")


def test_pwa_endpoints_exist_and_are_not_stale_cached():
    manifest = client.get("/manifest.webmanifest")
    assert manifest.status_code == 200
    assert manifest.headers["content-type"].startswith("application/manifest+json")
    assert manifest.headers["cache-control"] == "no-store"

    worker = client.get("/service-worker.js")
    assert worker.status_code == 200
    assert worker.headers["content-type"].startswith("application/javascript")
    assert worker.headers["service-worker-allowed"] == "/"
    assert worker.headers["cache-control"] == "no-store"
