from __future__ import annotations

import json
import socketserver
import sys
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.docker_service import DockerService

IMG_UNUSED = "sha256:" + "a" * 64
IMG_RUNNING = "sha256:" + "b" * 64
IMG_STOPPED = "sha256:" + "c" * 64
CONTAINER_RUNNING = "d" * 64
CONTAINER_STOPPED = "e" * 64
NETWORK_UNUSED = "f" * 64
NETWORK_USED = "g" * 64
NETWORK_STOPPED = "h" * 64
NETWORK_SWARM = "i" * 64


def default_buildcache_records():
    return {
        "cache-parent": {
            "ID": "cache-parent",
            "Type": "regular",
            "Description": "base build layer",
            "InUse": False,
            "Size": 100,
            "Parents": [],
        },
        "cache-leaf": {
            "ID": "cache-leaf",
            "Type": "regular",
            "Description": "RUN apk add curl",
            "InUse": False,
            "Size": 400,
            "Parents": ["cache-parent"],
        },
        "cache-independent": {
            "ID": "cache-independent",
            "Type": "regular",
            "Description": "independent cache",
            "InUse": False,
            "Size": 50,
            "Parents": [],
        },
        "cache-used": {
            "ID": "cache-used",
            "Type": "regular",
            "Description": "active cache",
            "InUse": True,
            "Size": 100,
            "Parents": [],
        },
        "cache-unknown": {
            "ID": "cache-unknown",
            "Type": "regular",
            "Description": "unknown usage state",
            "Size": 25,
            "Parents": [],
        },
    }


class FakeDockerHandler(BaseHTTPRequestHandler):
    server_version = "FakeDocker/1.0"
    sys_version = ""

    def log_message(self, *_args):
        return

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _empty(self, status=204):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _containers(self):
        running_mounts = [{"Type": "volume", "Name": "used-volume"}]
        stopped_mounts = [{"Type": "volume", "Name": "stopped-volume"}]
        if self.server.extra_volume_ref:
            running_mounts.append({"Type": "volume", "Name": "unused-volume"})
        return [
            {
                "Id": CONTAINER_RUNNING,
                "Names": ["/running"],
                "Image": "used:latest",
                "ImageID": IMG_RUNNING,
                "State": "running",
                "Mounts": running_mounts,
                "NetworkSettings": {
                    "Networks": {
                        "used-net": {"NetworkID": NETWORK_USED},
                    }
                },
            },
            {
                "Id": CONTAINER_STOPPED,
                "Names": ["/stopped"],
                "Image": "stopped:latest",
                "ImageID": IMG_STOPPED,
                "State": "exited",
                "Mounts": stopped_mounts,
                "NetworkSettings": {
                    "Networks": {
                        "stopped-net": {"NetworkID": NETWORK_STOPPED},
                    }
                },
            },
        ]

    def do_GET(self):
        self.server.calls.append(("GET", self.path))
        parsed = urlsplit(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/_ping":
            body = b"OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/version":
            self._json(200, {"Version": "29.8.0", "ApiVersion": "1.55", "MinAPIVersion": "1.40"})
            return

        if path == "/v1.55/system/df":
            kind = (query.get("type") or [""])[0]
            if kind in self.server.fail_df_types:
                self._json(500, {"message": "failed to retrieve container list: rw layer snapshot not found for container broken123"})
                return
            if kind == "volume":
                self._json(200, {
                    "VolumesUsage": {
                        "ActiveCount": 2,
                        "TotalCount": 3,
                        "Reclaimable": 300,
                        "TotalSize": 600,
                        "Items": [
                            {"Name": "unused-volume", "Driver": "local", "UsageData": {"Size": 300, "RefCount": 0}},
                            {"Name": "used-volume", "Driver": "local", "UsageData": {"Size": 100, "RefCount": 1}},
                            {"Name": "stopped-volume", "Driver": "local", "UsageData": {"Size": 200, "RefCount": 1}},
                        ],
                    }
                })
                return
            if kind == "build-cache":
                items = list(self.server.buildcache_records.values())
                self._json(200, {
                    "BuildCacheUsage": {
                        "ActiveCount": sum(1 for item in items if item.get("InUse") is True),
                        "TotalCount": len(items),
                        "Reclaimable": sum(int(item.get("Size") or 0) for item in items if item.get("InUse") is False),
                        "TotalSize": sum(int(item.get("Size") or 0) for item in items),
                        "Items": items,
                    }
                })
                return
            # Image/container df must never be needed by the cleanup overview.
            if kind in {"image", "container"}:
                self._json(500, {"message": f"unexpected expensive df request for {kind}"})
                return
            self._json(400, {"message": "missing type"})
            return

        if path == "/v1.55/containers/json":
            if self.server.fail_containers:
                self._json(500, {"message": "container list unavailable"})
                return
            assert query.get("all") == ["1"]
            assert "size" not in query
            self._json(200, self._containers())
            return

        if path == "/v1.55/images/json":
            self._json(200, [
                {"Id": IMG_UNUSED, "RepoTags": ["unused:latest"], "Size": 100, "SharedSize": 20, "Containers": 0},
                {"Id": IMG_RUNNING, "RepoTags": ["used:latest"], "Size": 200, "SharedSize": 0, "Containers": 1},
                {"Id": IMG_STOPPED, "RepoTags": ["stopped:latest"], "Size": 300, "SharedSize": 0, "Containers": 1},
            ])
            return

        if path == "/v1.55/volumes":
            filters = json.loads((query.get("filters") or ["{}"])[0])
            assert filters.get("dangling") == ["true"]
            # Intentionally return referenced volumes as well. ZentDClean must
            # fail closed and independently cross-check every container mount.
            self._json(200, {
                "Volumes": [
                    {"Name": "unused-volume", "Driver": "local", "UsageData": {"Size": 300, "RefCount": 0}},
                    {"Name": "used-volume", "Driver": "local", "UsageData": {"Size": 100, "RefCount": 0}},
                    {"Name": "stopped-volume", "Driver": "local", "UsageData": {"Size": 200, "RefCount": 0}},
                    {"Name": "cluster-volume", "Driver": "local", "Scope": "global", "ClusterVolume": {"ID": "cluster-1"}, "UsageData": {"Size": 400, "RefCount": 0}},
                ],
                "Warnings": None,
            })
            return

        if path == "/v1.55/networks":
            filters = json.loads((query.get("filters") or ["{}"])[0])
            assert filters.get("dangling") == ["true"]
            # Intentionally return referenced networks as well. ZentDClean must
            # still cross-check all containers and inspect the candidate network.
            self._json(200, [
                {"Name": "bridge", "Id": "builtin", "Driver": "bridge", "Scope": "local"},
                {"Name": "unused-net", "Id": NETWORK_UNUSED, "Driver": "bridge", "Scope": "local"},
                {"Name": "used-net", "Id": NETWORK_USED, "Driver": "bridge", "Scope": "local"},
                {"Name": "stopped-net", "Id": NETWORK_STOPPED, "Driver": "bridge", "Scope": "local"},
                {"Name": "swarm-net", "Id": NETWORK_SWARM, "Driver": "overlay", "Scope": "swarm"},
            ])
            return

        if path.startswith("/v1.55/networks/"):
            uid = unquote(path.removeprefix("/v1.55/networks/"))
            if uid in self.server.fail_network_inspect:
                self._json(500, {"message": "network inspect failed"})
                return
            if uid == NETWORK_UNUSED:
                self._json(200, {"Id": uid, "Name": "unused-net", "Scope": "local", "Containers": {}, "Services": {}})
                return
            if uid == NETWORK_USED:
                self._json(200, {"Id": uid, "Name": "used-net", "Scope": "local", "Containers": {CONTAINER_RUNNING: {}}})
                return
            if uid == NETWORK_STOPPED:
                self._json(200, {"Id": uid, "Name": "stopped-net", "Scope": "local", "Containers": {CONTAINER_STOPPED: {}}})
                return
            self._json(404, {"message": "network not found"})
            return

        self._json(404, {"message": f"unknown GET {path}"})

    def do_DELETE(self):
        self.server.calls.append(("DELETE", self.path))
        path = unquote(urlsplit(self.path).path)
        allowed = {
            f"/v1.55/images/{IMG_UNUSED}",
            "/v1.55/volumes/unused-volume",
            f"/v1.55/containers/{CONTAINER_STOPPED}",
            f"/v1.55/networks/{NETWORK_UNUSED}",
        }
        if path in self.server.fail_delete_paths:
            self._json(409, {"message": self.server.fail_delete_paths[path]})
        elif path in allowed:
            self._empty()
        else:
            self._json(404, {"message": "not found"})

    def do_POST(self):
        self.server.calls.append(("POST", self.path))
        parsed = urlsplit(self.path)
        if parsed.path != "/v1.55/build/prune":
            self._json(404, {"message": "not found"})
            return

        query = parse_qs(parsed.query)
        filters = json.loads((query.get("filters") or ["{}"]) [0])
        self.server.build_prune_queries.append({"all": query.get("all"), "filters": filters})

        if self.server.fail_build_prune_message:
            self._json(500, {"message": self.server.fail_build_prune_message})
            return
        if query.get("all") != ["true"] or filters:
            self._json(400, {"message": "expected native all-unused build-cache prune"})
            return

        deleted = []
        reclaimed = 0
        for uid, item in list(self.server.buildcache_records.items()):
            if item.get("InUse") is False and uid not in self.server.keep_buildcache_ids:
                deleted.append(uid)
                reclaimed += int(item.get("Size") or 0)
                self.server.buildcache_records.pop(uid, None)
        self._json(200, {"CachesDeleted": deleted, "SpaceReclaimed": reclaimed})


class UnixHTTPServer(socketserver.UnixStreamServer):
    allow_reuse_address = True


def start_server(
    socket_path: Path,
    *,
    fail_df_types=(),
    fail_delete_paths=None,
    fail_containers=False,
    fail_network_inspect=(),
    fail_build_prune_message=None,
    keep_buildcache_ids=(),
):
    server = UnixHTTPServer(str(socket_path), FakeDockerHandler)
    server.calls = []
    server.fail_df_types = set(fail_df_types)
    server.fail_delete_paths = dict(fail_delete_paths or {})
    server.fail_containers = bool(fail_containers)
    server.fail_network_inspect = set(fail_network_inspect)
    server.extra_volume_ref = False
    server.buildcache_records = default_buildcache_records()
    server.build_prune_queries = []
    server.fail_build_prune_message = fail_build_prune_message
    server.keep_buildcache_ids = set(keep_buildcache_ids)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_real_unix_socket_transport_and_candidate_only_overview(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        assert service.ping() is True
        assert service.api_version == "1.55"
        assert service.server_api_version == "1.55"

        overview = service.overview()
        assert overview["images"] == {"count": 1, "reclaimable": 80, "reclaimable_complete": False, "available": True}
        assert overview["volumes"] == {"count": 1, "reclaimable": 300, "reclaimable_complete": True, "available": True}
        assert overview["buildcache"] == {"count": 3, "reclaimable": 550, "reclaimable_complete": True, "available": True}
        assert overview["containers"] == {"count": 1, "reclaimable": None, "reclaimable_complete": False, "available": True}
        assert overview["networks"] == {"count": 1, "reclaimable": None, "reclaimable_complete": True, "available": True}
        assert overview["reclaimable_total"] == 930
        assert overview["reclaimable_total_complete"] is False  # stopped-container bytes are intentionally unknown
        assert overview["partial"] is False
        assert all("total" not in overview[kind] for kind in ("images", "volumes", "containers", "buildcache", "networks"))
    finally:
        stop_server(server, thread)


def test_broken_container_snapshot_is_never_queried_for_overview(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_df_types={"container", "image"})
    try:
        service = DockerService(socket_path=str(socket_path))
        overview = service.overview()
        assert overview["partial"] is False
        assert overview["images"]["count"] == 1
        assert overview["containers"]["count"] == 1
        df_calls = [path for method, path in server.calls if method == "GET" and "/system/df" in path]
        assert all("type=container" not in path and "type=image" not in path for path in df_calls)
    finally:
        stop_server(server, thread)


def test_buildcache_df_failure_does_not_hide_other_safe_cleanup_lists(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_df_types={"build-cache", "volume"})
    try:
        service = DockerService(socket_path=str(socket_path))
        overview = service.overview()
        assert overview["partial"] is True
        assert overview["images"]["count"] == 1
        assert overview["volumes"]["count"] == 1
        assert overview["volumes"]["reclaimable"] == 300  # list endpoint still carries safe per-volume UsageData
        assert overview["containers"]["count"] == 1
        assert overview["networks"]["count"] == 1
        assert overview["buildcache"]["available"] is False
        assert overview["buildcache"]["count"] == 0
        assert "buildcache" in overview["warnings"]
    finally:
        stop_server(server, thread)


def test_candidates_never_request_container_size(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        data = service.candidates("containers")
        assert [x["uid"] for x in data["containers"]] == [CONTAINER_STOPPED]
        calls = [path for method, path in server.calls if method == "GET" and "/containers/json" in path]
        assert calls
        assert all("size=" not in path for path in calls)
        assert data["containers"][0]["size"] is None
    finally:
        stop_server(server, thread)


def test_every_cleanup_category_contains_only_provably_unused_resources(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        data = service.candidates("all")
        assert [item["uid"] for item in data["images"]] == [IMG_UNUSED]
        assert [item["uid"] for item in data["volumes"]] == ["unused-volume"]
        assert [item["uid"] for item in data["containers"]] == [CONTAINER_STOPPED]
        assert {item["uid"] for item in data["buildcache"]} == {"cache-parent", "cache-leaf", "cache-independent"}
        assert "cache-used" not in {item["uid"] for item in data["buildcache"]}
        assert "cache-unknown" not in {item["uid"] for item in data["buildcache"]}
        assert [item["uid"] for item in data["networks"]] == [NETWORK_UNUSED]

        # The fake dangling-volume response deliberately includes these active
        # references; our independent all-container check must still reject them.
        assert "used-volume" not in {item["uid"] for item in data["volumes"]}
        assert "stopped-volume" not in {item["uid"] for item in data["volumes"]}
        assert "cluster-volume" not in {item["uid"] for item in data["volumes"]}
        assert NETWORK_USED not in {item["uid"] for item in data["networks"]}
        assert NETWORK_STOPPED not in {item["uid"] for item in data["networks"]}
        assert NETWORK_SWARM not in {item["uid"] for item in data["networks"]}
    finally:
        stop_server(server, thread)


def test_container_list_failure_fails_closed_for_dependent_categories(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_containers=True)
    try:
        service = DockerService(socket_path=str(socket_path))
        data = service.candidates("all")
        assert data["images"] == []
        assert data["volumes"] == []
        assert data["networks"] == []
        assert data["containers"] == []
        assert {"images", "volumes", "networks", "containers"} <= set(service.category_errors)
        # Build cache is independent of the container list and may still be safely shown.
        assert {item["uid"] for item in data["buildcache"]} == {"cache-parent", "cache-leaf", "cache-independent"}
    finally:
        stop_server(server, thread)


def test_network_inspect_failure_is_fail_closed(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_network_inspect={NETWORK_UNUSED})
    try:
        service = DockerService(socket_path=str(socket_path))
        assert service.candidates("networks")["networks"] == []
    finally:
        stop_server(server, thread)


def test_cleanup_rechecks_current_usage_before_delete(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        assert [item["uid"] for item in service.candidates("volumes")["volumes"]] == ["unused-volume"]

        # Simulate a race: the volume becomes attached after the modal opened.
        server.extra_volume_ref = True
        result = service.cleanup("volumes", ["unused-volume"])
        assert result == [{
            "uid": "unused-volume",
            "name": "unused-volume",
            "status": "skipped",
            "error_code": "no_longer_unused",
        }]
        assert not any(method == "DELETE" and "/volumes/unused-volume" in path for method, path in server.calls)
    finally:
        stop_server(server, thread)


def test_selective_cleanup_uses_exact_engine_delete_and_never_active_ids(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        image_results = service.cleanup("images", [IMG_UNUSED, IMG_RUNNING])
        assert image_results[0]["uid"] == IMG_UNUSED
        assert image_results[0]["status"] == "deleted"
        assert image_results[0]["name"] == "unused:latest"
        assert image_results[1] == {
            "uid": IMG_RUNNING,
            "name": IMG_RUNNING,
            "status": "skipped",
            "error_code": "no_longer_unused",
        }
        assert service.cleanup("volumes", ["unused-volume"])[0]["status"] == "deleted"
        assert service.cleanup("containers", [CONTAINER_STOPPED])[0]["status"] == "deleted"
        assert service.cleanup("networks", [NETWORK_UNUSED])[0]["status"] == "deleted"

        calls = "\n".join(path for method, path in server.calls if method == "DELETE")
        assert f"/v1.55/images/{IMG_UNUSED.replace(':', '%3A')}" in calls
        image_delete = next(path for method, path in server.calls if method == "DELETE" and "/images/" in path)
        image_query = parse_qs(urlsplit(image_delete).query)
        assert image_query.get("force") == ["false"]
        assert image_query.get("noprune") == ["true"]
        assert IMG_RUNNING not in calls
        assert "/v1.55/volumes/unused-volume" in calls
        assert f"/v1.55/containers/{CONTAINER_STOPPED}" in calls
        assert f"/v1.55/networks/{NETWORK_UNUSED}" in calls
    finally:
        stop_server(server, thread)


def test_buildcache_cleanup_uses_one_native_all_unused_prune(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        ids = [item["uid"] for item in service.candidates("buildcache")["buildcache"]]
        result = service.cleanup("buildcache", ids)
        assert result
        assert all(item["status"] == "deleted" for item in result)
        assert server.build_prune_queries == [{"all": ["true"], "filters": {}}]
        assert set(server.buildcache_records) == {"cache-used", "cache-unknown"}
    finally:
        stop_server(server, thread)


def test_buildcache_prune_keeps_in_use_and_unknown_records(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path)
    try:
        service = DockerService(socket_path=str(socket_path))
        ids = [item["uid"] for item in service.candidates("buildcache")["buildcache"]]
        service.cleanup("buildcache", ids)
        assert server.buildcache_records["cache-used"]["InUse"] is True
        assert "InUse" not in server.buildcache_records["cache-unknown"]
    finally:
        stop_server(server, thread)


def test_buildcache_prune_reports_unused_record_that_docker_kept(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, keep_buildcache_ids={"cache-independent"})
    try:
        service = DockerService(socket_path=str(socket_path))
        ids = [item["uid"] for item in service.candidates("buildcache")["buildcache"]]
        result = service.cleanup("buildcache", ids)
        by_id = {item["uid"]: item for item in result}
        assert by_id["cache-independent"]["status"] == "error"
        assert by_id["cache-independent"]["error_code"] == "not_deleted"
        assert by_id["cache-parent"]["status"] == "deleted"
        assert by_id["cache-leaf"]["status"] == "deleted"
    finally:
        stop_server(server, thread)


def test_buildcache_prune_api_error_is_returned_for_each_preview_item(tmp_path):
    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_build_prune_message="builder prune failed")
    try:
        service = DockerService(socket_path=str(socket_path))
        ids = [item["uid"] for item in service.candidates("buildcache")["buildcache"]]
        result = service.cleanup("buildcache", ids)
        assert len(result) == len(ids)
        assert all(item["status"] == "error" for item in result)
        assert all(item["error_code"] == "docker_error" for item in result)
        assert all("builder prune failed" in item["error_detail"] for item in result)
        assert len(server.build_prune_queries) == 1
    finally:
        stop_server(server, thread)


def test_buildcache_large_preview_uses_one_prune_request():
    service = object.__new__(DockerService)
    service.category_errors = {}
    ids = [f"cache-{index:04d}" for index in range(609)]
    items = [{"kind": "buildcache", "uid": uid, "name": uid, "size": 1, "details": "regular"} for uid in ids]
    request_calls = []

    service.candidates = lambda kind: {"buildcache": items}
    service._buildcache_records = lambda: {}

    def fake_request(method, path, *, query=None, versioned=True, raw=False):
        request_calls.append((method, path, query))
        return {"CachesDeleted": list(ids), "SpaceReclaimed": len(ids)}

    service._request = fake_request
    result = service.cleanup("buildcache", ids)
    assert len(result) == 609
    assert all(item["status"] == "deleted" for item in result)
    assert request_calls == [("POST", "/build/prune", {"all": "true"})]


def test_cleanup_returns_exact_docker_failure_for_item(tmp_path):
    socket_path = tmp_path / "docker.sock"
    path = f"/v1.55/images/{IMG_UNUSED}"
    server, thread = start_server(socket_path, fail_delete_paths={path: "conflict: image has dependent child"})
    try:
        service = DockerService(socket_path=str(socket_path))
        result = service.cleanup("images", [IMG_UNUSED])
        assert result == [{
            "uid": IMG_UNUSED,
            "name": "unused:latest",
            "status": "error",
            "error_code": "docker_error",
            "error_detail": "conflict: image has dependent child",
        }]
    finally:
        stop_server(server, thread)


def test_fastapi_overview_keeps_docker_available_when_buildcache_df_is_partial(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import app.main as main

    socket_path = tmp_path / "docker.sock"
    server, thread = start_server(socket_path, fail_df_types={"build-cache"})
    try:
        monkeypatch.setenv("DOCKER_SOCKET", str(socket_path))
        monkeypatch.setattr(main, "AUTH_ENABLED", False)
        response = TestClient(main.app).get("/api/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["docker"]["available"] is True
        assert data["docker"]["partial"] is True
        assert data["images"]["reclaimable"] == 80
        assert data["images"]["reclaimable_complete"] is False
        assert data["containers"]["count"] == 1
        assert data["buildcache"]["available"] is False
    finally:
        stop_server(server, thread)
