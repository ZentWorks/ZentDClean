from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def _release_file(internal_rel: str, public_rel: str) -> Path:
    internal = BASE / internal_rel
    if internal.is_file():
        return internal
    public = BASE / public_rel
    assert public.is_file(), f"Release file missing: {internal_rel} or {public_rel}"
    return public


def test_required_files_exist():
    for rel in [
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        "app/main.py",
        "app/docker_service.py",
        "app/templates/index.html",
        "app/static/app.js",
        "app/static/app.css",
        "app/static/favicon.ico",
        "app/static/manifest.webmanifest",
        "app/static/service-worker.js",
        "app/static/icons/icon-64.png",
        "app/static/icons/icon-192.png",
        "app/static/icons/icon-512.png",
        "app/static/icons/icon-maskable-192.png",
        "app/static/icons/icon-maskable-512.png",
        "app/static/icons/apple-touch-icon.png",
    ]:
        assert (BASE / rel).is_file()


def test_no_external_assets():
    html = (BASE / "app/templates/index.html").read_text()
    assert "https://" not in html
    assert "http://" not in html


def test_compose_builds_locally():
    compose = (BASE / "docker-compose.yml").read_text()
    assert "build: ." in compose
    assert "ghcr.io/" not in compose


def test_password_is_optional():
    main = (BASE / "app/main.py").read_text()
    assert 'AUTH_ENABLED = bool(PASSWORD)' in main


def test_default_port_is_8787():
    compose = (BASE / "docker-compose.yml").read_text()
    dockerfile = (BASE / "Dockerfile").read_text()
    assert '"8787:8787"' in compose
    assert "PORT=8787" in dockerfile
    assert "EXPOSE 8787" in dockerfile


def test_container_logs_hide_normal_uvicorn_info_and_access_lines():
    dockerfile = (BASE / "Dockerfile").read_text()
    assert "--log-level warning" in dockerfile
    assert "--no-access-log" in dockerfile


def test_compose_only_mounts_docker_socket():
    compose = (BASE / "docker-compose.yml").read_text()
    assert "/var/run/docker.sock:/var/run/docker.sock" in compose
    assert "/:/host" not in compose
    assert "HOST_STORAGE_PATH" not in compose
    assert "propagation:" not in compose
    assert "rslave" not in compose


def test_compose_has_basic_hardening():
    compose = (BASE / "docker-compose.yml").read_text()
    assert "read_only: true" in compose
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose
    assert "- ALL" in compose


def test_direct_engine_api_and_no_container_size_listing():
    requirements = (BASE / "requirements.txt").read_text().lower()
    service = (BASE / "app/docker_service.py").read_text()
    assert "docker==" not in requirements
    assert "import docker" not in service
    assert "UnixHTTPConnection" in service
    assert 'query={"all": "1", "size": "1"}' not in service
    assert 'query={"all": "1"}' in service


def test_runtime_versions_and_frozen_app_version():
    main = (BASE / "app/main.py").read_text()
    dockerfile = (BASE / "Dockerfile").read_text()
    requirements = (BASE / "requirements.txt").read_text()
    assert 'APP_VERSION = "0.1.2"' in main
    assert 'ASSET_REVISION = "7"' in main
    assert "FROM python:3.14.7-slim" in dockerfile
    assert "fastapi==0.141.1" in requirements
    assert "uvicorn[standard]==0.53.0" in requirements
    assert "jinja2==3.1.6" in requirements


def test_assets_are_versioned_and_pwa_metadata_declared():
    template = (BASE / "app/templates/index.html").read_text()
    assert "v{{ version }}" in template
    assert "?v={{ asset_revision }}" in template
    assert 'rel="icon"' in template
    assert 'rel="manifest"' in template
    assert 'rel="apple-touch-icon"' in template
    assert 'name="theme-color"' in template
    assert 'name="apple-mobile-web-app-capable"' in template
    assert 'data-asset-revision="{{ asset_revision }}"' in template
    assert "/static/icons/icon-64.png" in template


def test_manifest_has_required_install_icons_and_standalone_mode():
    import json

    manifest = json.loads((BASE / "app/static/manifest.webmanifest").read_text())
    assert manifest["name"] == "ZentDClean"
    assert manifest["start_url"] == "/"
    assert manifest["scope"] == "/"
    assert manifest["display"] == "standalone"
    icons = manifest["icons"]
    assert any(icon["sizes"] == "192x192" and icon["purpose"] == "any" for icon in icons)
    assert any(icon["sizes"] == "512x512" and icon["purpose"] == "any" for icon in icons)
    assert any(icon["sizes"] == "192x192" and icon["purpose"] == "maskable" for icon in icons)
    assert any(icon["sizes"] == "512x512" and icon["purpose"] == "maskable" for icon in icons)


def test_service_worker_caches_only_static_assets_not_app_or_api_data():
    worker = (BASE / "app/static/service-worker.js").read_text()
    javascript = (BASE / "app/static/app.js").read_text()
    assert 'CACHE_NAME = `${CACHE_PREFIX}7`' in worker
    assert 'url.pathname.startsWith("/api/")' in worker
    assert 'url.pathname === "/"' in worker
    assert 'request.mode === "navigate"' in worker
    assert 'url.pathname.startsWith("/static/")' in worker
    assert 'navigator.serviceWorker.register' in javascript
    assert 'window.isSecureContext' in javascript


def test_host_storage_feature_is_fully_removed():
    files = [
        BASE / "app/main.py",
        BASE / "app/docker_service.py",
        BASE / "app/templates/index.html",
        BASE / "app/static/app.js",
        BASE / "app/static/app.css",
        BASE / "README.md",
        BASE / "docker-compose.yml",
    ]
    combined = "\n".join(path.read_text() for path in files)
    for forbidden in ["host_disk_usage", "HOST_STORAGE_PATH", "HOST_ROOT", "disk-card", "diskText", "diskFree", "diskBar"]:
        assert forbidden not in combined


def test_overview_ui_only_renders_cleanup_candidate_values():
    javascript = (BASE / "app/static/app.js").read_text()
    service = (BASE / "app/docker_service.py").read_text()
    assert "x.total" not in javascript
    assert 't("used")' not in javascript
    assert 't("unused")' in javascript
    assert '"total":' not in service.split("def overview", 1)[1].split("def _cleanup_error_detail", 1)[0]


def test_cleanup_ui_has_detailed_failures_and_buildcache_preview_mode():
    javascript = (BASE / "app/static/app.js").read_text()
    template = (BASE / "app/templates/index.html").read_text()
    main = (BASE / "app/main.py").read_text()
    assert 'id="cleanupResult"' in template
    assert 'id="bulkActions"' in template
    assert "error_detail" in javascript
    assert "error_code" in javascript
    assert 'const buildCachePreview = currentKind === "buildcache"' in javascript
    assert '$("#bulkActions").classList.toggle("hidden", buildCachePreview)' in javascript
    assert 'const batches = kind === "buildcache" ? [items] : chunk(items, 200)' in javascript
    assert 'uid: "__all_unused_buildcache__"' in javascript
    assert "_buildcacheIds" in javascript
    assert "keepKeys" in javascript
    assert "max_length=5000" in main


def test_unused_detection_is_fail_closed_in_every_resource_category():
    service = (BASE / "app/docker_service.py").read_text()
    assert 'entry.get("InUse") is not False' in service
    assert 'refs["volumes"]' in service
    assert 'refs["image_ids"]' in service
    assert 'refs["network_ids"]' in service
    assert "_network_inspect" in service
    assert "self._networks(dangling_only=True)" in service
    assert 'scope not in {"", "local"}' in service
    assert 'volume.get("ClusterVolume") is not None' in service
    assert 'removable_states = {"created", "exited", "dead"}' in service


def test_buildcache_cleanup_uses_native_all_unused_prune_without_id_filters():
    service = (BASE / "app/docker_service.py").read_text()
    cleanup = service.split("def _cleanup_buildcache", 1)[1].split("def cleanup", 1)[0]
    assert 'self._request("POST", "/build/prune", query={"all": "true"})' in cleanup
    assert '"id"' not in cleanup
    assert 'filters' not in cleanup
    assert "_buildcache_delete_order" not in service


def test_image_cleanup_never_prunes_unselected_parent_images():
    service = (BASE / "app/docker_service.py").read_text()
    assert '"noprune": "true"' in service
    assert '"noprune": "false"' not in service


def test_inexact_image_sizes_are_marked_as_lower_bounds_in_ui():
    service = (BASE / "app/docker_service.py").read_text()
    javascript = (BASE / "app/static/app.js").read_text()
    assert 'size_complete=False' in service
    assert 'item.size_complete !== false' in javascript
    assert 'complete === false ? "+"' in javascript


def test_pwa_icon_dimensions_and_png_signatures():
    import struct

    expected = {
        "app/static/icons/icon-64.png": (64, 64),
        "app/static/icons/icon-192.png": (192, 192),
        "app/static/icons/icon-512.png": (512, 512),
        "app/static/icons/icon-maskable-192.png": (192, 192),
        "app/static/icons/icon-maskable-512.png": (512, 512),
        "app/static/icons/apple-touch-icon.png": (180, 180),
    }
    for rel, dimensions in expected.items():
        data = (BASE / rel).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", data[16:24])
        assert (width, height) == dimensions


def test_mobile_layout_has_safe_area_and_small_screen_rules():
    css = (BASE / "app/static/app.css").read_text()
    assert "safe-area-inset-top" in css
    assert "safe-area-inset-bottom" in css
    assert "100dvh" in css
    assert "@media (max-width: 680px)" in css
    assert "@media (max-width: 430px)" in css
    assert "grid-template-columns: 1fr" in css


def test_browser_language_and_manual_language_persistence():
    javascript = (BASE / "app/static/app.js").read_text()
    template = (BASE / "app/templates/index.html").read_text()
    assert 'const LANGUAGE_STORAGE_KEY = "zentdclean_language"' in javascript
    assert 'const SUPPORTED_LANGUAGES = Object.freeze(Object.keys(translations))' in javascript
    assert 'navigator.languages[0]' in javascript
    assert 'navigator.language' in javascript
    assert 'return normalizeLanguage(primary) || "en";' in javascript
    assert 'localStorage.setItem(LANGUAGE_STORAGE_KEY, value)' in javascript
    assert 'let lang = storedLanguage() || browserLanguage();' in javascript
    assert "data-language-toggle" not in javascript
    assert "data-language-toggle" not in template
    assert template.count("data-language-select") == 2
    for code in ["de", "en", "fr", "nl", "es", "pt", "pl", "it", "cs"]:
        assert f"  {code}: {{" in javascript
        assert f'<option value="{code}">' in template


def test_every_translation_has_the_complete_key_set():
    import re

    javascript = (BASE / "app/static/app.js").read_text()
    block = javascript.split("const translations = {", 1)[1].split("\n};", 1)[0]
    language_blocks = re.findall(r"^  (de|en|fr|nl|es|pt|pl|it|cs): \{(.*?)(?=^  [a-z]{2}: \{|\Z)", block, re.M | re.S)
    assert len(language_blocks) == 9
    required = {
        "loginTitle", "password", "login", "logout", "cleanupTitle", "reclaimable", "cleanAll", "clean",
        "selectAll", "selectNone", "selected", "cancel", "delete", "nothingToClean", "unused", "items", "item",
        "unnamed", "loginFailed", "loadFailed", "categoryLoadFailed", "images", "volumes", "containers",
        "buildcache", "networks", "networkHint", "containerHint", "refresh", "dockerPermission", "dockerMissing",
        "dockerRefused", "dockerTimeout", "dockerUnavailable", "partialStats", "cleanupFailedHeading", "deleted",
        "failed", "noLongerUnused", "notDeleted", "requestFailed", "verificationFailed",
        "dockerReason", "language", "close",
    }
    for code, body in language_blocks:
        keys = set(re.findall(r"\b([A-Za-z][A-Za-z0-9]*):", body))
        assert required <= keys, f"Missing translations for {code}: {sorted(required - keys)}"


def test_github_readme_shows_project_logo():
    readme = _release_file(".github-release/README.md", "README.md").read_text()
    assert 'src="app/static/icons/icon-512.png"' in readme
    assert 'alt="ZentDClean logo"' in readme


def test_release_readme_documents_https_cookie_and_size_lower_bound():
    readme = _release_file(".github-release/README.md", "README.md").read_text()
    assert "`COOKIE_SECURE`" in readme
    assert "HTTPS" in readme
    assert "conservative minimum" in readme


def test_release_workflow_pins_third_party_actions_to_immutable_shas():
    workflow = _release_file(
        ".github-release/build-and-publish.yml",
        ".github/workflows/build-and-publish.yml",
    ).read_text()
    expected = {
        "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
        "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
        "docker/setup-qemu-action": "99012661954931238ded8c8b007157a8430204e1",
        "docker/setup-buildx-action": "f87e5991a6d7451dcb8d9637bfbc97413f497069",
        "docker/login-action": "dbcb813823bdd20940b903addbd779551569679f",
        "docker/build-push-action": "c3c9e263c25d99ce0380d002d59b67737d91b0dc",
    }
    for action, sha in expected.items():
        assert f"uses: {action}@{sha}" in workflow
    assert "persist-credentials: false" in workflow
    deploy_path = BASE / "deploy.sh"
    if deploy_path.is_file():
        deploy = deploy_path.read_text()
        for action, sha in expected.items():
            assert f"{action}@{sha}" in deploy


def test_docker_integration_helper_calls_supply_all_required_keywords():
    import ast

    path = BASE / "tests/test_docker_integration.py"
    tree = ast.parse(path.read_text())
    helper = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_assert_active_container_unchanged"
    )
    required_keywords = {arg.arg for arg in helper.args.kwonlyargs}
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_assert_active_container_unchanged"
    ]
    assert calls, "Docker integration safety helper is never exercised"
    for call in calls:
        supplied = {keyword.arg for keyword in call.keywords if keyword.arg is not None}
        assert required_keywords <= supplied, (
            "Docker integration helper call is missing required keyword arguments: "
            f"{sorted(required_keywords - supplied)}"
        )
