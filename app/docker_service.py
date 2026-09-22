from __future__ import annotations

import http.client
import json
import logging
import os
import socket
import stat
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar
from urllib.parse import quote, urlencode

logger = logging.getLogger("zentdclean.docker")

DEFAULT_DOCKER_SOCKET = "/var/run/docker.sock"
# Newest Engine API schema ZentDClean understands. The daemon version is
# negotiated down automatically, so older Docker hosts keep working.
PREFERRED_API_VERSION = (1, 56)

T = TypeVar("T")
_WARNING_LOG_TIMES: dict[str, float] = {}
_WARNING_LOG_INTERVAL = 60.0


def _log_api_warning(area: str, status: int, message: str) -> None:
    now = time.monotonic()
    key = f"{area}:{status}:{message}"
    last = _WARNING_LOG_TIMES.get(key, 0.0)
    if now - last >= _WARNING_LOG_INTERVAL:
        logger.warning("Docker API %s failed (%s): %s", area, status, message)
        _WARNING_LOG_TIMES[key] = now


class DockerConnectionError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail


class DockerAPIError(RuntimeError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass
class CleanupItem:
    kind: str
    uid: str
    name: str
    size: int | None
    details: str = ""
    # False means the byte value is a conservative lower bound, not an exact
    # reclaimable amount. This is relevant for images because shared layers
    # can become reclaimable only after multiple unused images are removed.
    size_complete: bool = True
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UnixHTTPConnection(http.client.HTTPConnection):
    """Minimal HTTP transport for Docker's local Unix socket."""

    def __init__(self, socket_path: str, timeout: float = 12.0) -> None:
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(self.socket_path)
        except Exception:
            sock.close()
            raise
        self.sock = sock


def _api_tuple(version: str) -> tuple[int, int]:
    try:
        major, minor, *_ = version.split(".")
        return int(major), int(minor)
    except (ValueError, AttributeError):
        return (1, 24)


def _api_string(version: tuple[int, int]) -> str:
    return f"{version[0]}.{version[1]}"


def _optional_size(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _socket_error(exc: BaseException) -> DockerConnectionError:
    detail = str(exc).strip()
    lowered = detail.lower()
    if isinstance(exc, PermissionError) or "permission denied" in lowered:
        return DockerConnectionError("permission_denied", detail)
    if isinstance(exc, FileNotFoundError) or "no such file" in lowered:
        return DockerConnectionError("socket_missing", detail)
    if isinstance(exc, ConnectionRefusedError) or "connection refused" in lowered:
        return DockerConnectionError("connection_refused", detail)
    if isinstance(exc, (TimeoutError, socket.timeout)) or "timed out" in lowered or "timeout" in lowered:
        return DockerConnectionError("timeout", detail)
    return DockerConnectionError("unavailable", detail)


class DockerService:
    def __init__(self, socket_path: str | None = None, timeout: float = 12.0) -> None:
        self.socket_path = socket_path or os.getenv("DOCKER_SOCKET", DEFAULT_DOCKER_SOCKET)
        self.timeout = timeout
        self.category_errors: dict[str, str] = {}
        self.stat_warnings: dict[str, str] = {}
        self._validate_socket()

        ping = self._request("GET", "/_ping", versioned=False, raw=True)
        if str(ping).strip().upper() != "OK":
            raise DockerConnectionError("unavailable", f"Unexpected /_ping response: {ping!r}")

        version = self._request("GET", "/version", versioned=False)
        if not isinstance(version, dict):
            raise DockerConnectionError("unavailable", "Docker /version returned no JSON object")

        server_version = _api_tuple(str(version.get("ApiVersion") or version.get("APIVersion") or ""))
        min_version = _api_tuple(str(version.get("MinAPIVersion") or "1.24"))
        selected = min(server_version, PREFERRED_API_VERSION)
        if selected < min_version:
            selected = server_version
        self.api_version = _api_string(selected)
        self.api_version_tuple = selected
        self.server_api_version = _api_string(server_version)
        self.engine_version = str(version.get("Version") or "")

    def _validate_socket(self) -> None:
        path = Path(self.socket_path)
        try:
            info = path.stat()
        except (OSError, PermissionError) as exc:
            raise _socket_error(exc) from exc
        if not stat.S_ISSOCK(info.st_mode):
            raise DockerConnectionError("not_a_socket", f"{self.socket_path} is not a Unix socket")

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        versioned: bool = True,
        raw: bool = False,
    ) -> Any:
        if versioned:
            path = f"/v{self.api_version}{path}"
        if query:
            path = f"{path}?{urlencode(query, doseq=True)}"

        connection = UnixHTTPConnection(self.socket_path, timeout=self.timeout)
        try:
            connection.request(method, path, headers={"Accept": "application/json", "Connection": "close"})
            response = connection.getresponse()
            body = response.read()
        except (OSError, PermissionError, TimeoutError, socket.timeout) as exc:
            raise _socket_error(exc) from exc
        finally:
            connection.close()

        text = body.decode("utf-8", errors="replace")
        if not 200 <= response.status < 300:
            message = text.strip() or response.reason
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and parsed.get("message"):
                    message = str(parsed["message"])
            except json.JSONDecodeError:
                pass
            raise DockerAPIError(response.status, message)

        if raw:
            return text
        if not body:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise DockerConnectionError("invalid_response", f"Invalid JSON from {path}") from exc

    def ping(self) -> bool:
        return str(self._request("GET", "/_ping", versioned=False, raw=True)).strip().upper() == "OK"

    def _best_effort(self, area: str, fn: Callable[[], T], default: T, *, stats: bool = False) -> T:
        try:
            return fn()
        except DockerConnectionError:
            raise
        except DockerAPIError as exc:
            _log_api_warning(area, exc.status, exc.message)
            target = self.stat_warnings if stats else self.category_errors
            target[area] = "docker_api_error"
            return default
        except Exception:
            logger.exception("Unexpected Docker %s error", area)
            target = self.stat_warnings if stats else self.category_errors
            target[area] = "unexpected_error"
            return default

    def _system_df(self, kind: str) -> dict[str, Any]:
        type_name = {
            "images": "image",
            "containers": "container",
            "volumes": "volume",
            "buildcache": "build-cache",
        }[kind]
        query: dict[str, Any] = {}
        if self.api_version_tuple >= (1, 42):
            query["type"] = type_name
        if self.api_version_tuple >= (1, 52):
            query["verbose"] = "1"
        data = self._request("GET", "/system/df", query=query or None)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _usage_section(df: dict[str, Any], kind: str) -> dict[str, Any]:
        names = {
            "images": ("ImagesUsage", "ImageUsage"),
            "containers": ("ContainersUsage", "ContainerUsage"),
            "volumes": ("VolumesUsage", "VolumeUsage"),
            "buildcache": ("BuildCacheUsage",),
        }[kind]
        for name in names:
            section = df.get(name)
            if isinstance(section, dict):
                return section
        return {}

    @classmethod
    def _df_items(cls, df: dict[str, Any], kind: str) -> list[dict[str, Any]]:
        section = cls._usage_section(df, kind)
        items = section.get("Items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        legacy_key = {
            "images": "Images",
            "containers": "Containers",
            "volumes": "Volumes",
            "buildcache": "BuildCache",
        }[kind]
        legacy = df.get(legacy_key)
        return [item for item in legacy or [] if isinstance(item, dict)]

    def _containers(self) -> list[dict[str, Any]]:
        # Never request size=1 here. A single broken RW snapshot can otherwise
        # make Docker fail the complete container list.
        data = self._request("GET", "/containers/json", query={"all": "1"})
        return [item for item in data or [] if isinstance(item, dict)]

    def _images(self) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"all": "1"}
        if self.api_version_tuple >= (1, 42):
            query["shared-size"] = "1"
        data = self._request("GET", "/images/json", query=query)
        return [item for item in data or [] if isinstance(item, dict)]

    def _volumes(self, *, dangling_only: bool = False) -> list[dict[str, Any]]:
        query = None
        if dangling_only:
            query = {"filters": json.dumps({"dangling": ["true"]}, separators=(",", ":"))}
        data = self._request("GET", "/volumes", query=query)
        if not isinstance(data, dict):
            return []
        return [item for item in data.get("Volumes") or [] if isinstance(item, dict)]

    def _networks(self, *, dangling_only: bool = False) -> list[dict[str, Any]]:
        query = None
        if dangling_only:
            query = {"filters": json.dumps({"dangling": ["true"]}, separators=(",", ":"))}
        data = self._request("GET", "/networks", query=query)
        return [item for item in data or [] if isinstance(item, dict)]

    def _network_inspect(self, uid: str) -> dict[str, Any]:
        data = self._request("GET", f"/networks/{quote(uid, safe='')}")
        return data if isinstance(data, dict) else {}

    def _usage(self, kinds: set[str]) -> dict[str, dict[str, Any]]:
        usage: dict[str, dict[str, Any]] = {}
        for kind in kinds & {"volumes", "buildcache"}:
            usage[kind] = self._best_effort(
                kind,
                lambda k=kind: self._system_df(k),
                {},
                stats=True,
            )
        return usage

    @staticmethod
    def _container_references(containers: list[dict[str, Any]]) -> dict[str, set[str]]:
        refs = {
            "image_ids": set(),
            "image_names": set(),
            "volumes": set(),
            "network_ids": set(),
            "network_names": set(),
        }
        for container in containers:
            image_id = container.get("ImageID")
            image_name = container.get("Image")
            if image_id:
                refs["image_ids"].add(str(image_id))
            if image_name:
                refs["image_names"].add(str(image_name))

            for mount in container.get("Mounts") or []:
                if not isinstance(mount, dict):
                    continue
                if str(mount.get("Type") or "").lower() != "volume":
                    continue
                name = mount.get("Name")
                if name:
                    refs["volumes"].add(str(name))

            network_settings = container.get("NetworkSettings") or {}
            networks = network_settings.get("Networks") if isinstance(network_settings, dict) else {}
            if isinstance(networks, dict):
                for name, settings in networks.items():
                    refs["network_names"].add(str(name))
                    if isinstance(settings, dict) and settings.get("NetworkID"):
                        refs["network_ids"].add(str(settings["NetworkID"]))
        return refs

    def candidates(self, kind: str | None = None) -> dict[str, list[dict[str, Any]]]:
        valid = {"images", "volumes", "containers", "buildcache", "networks"}
        kinds = valid if kind is None or kind == "all" else {kind}
        if not kinds <= valid:
            raise ValueError("Unknown cleanup type")

        self.category_errors = {}
        self.stat_warnings = {}
        usage = self._usage(kinds)
        result: dict[str, list[dict[str, Any]]] = {name: [] for name in valid}

        # Images, volumes and networks are only considered unused if Docker's
        # complete container list confirms that no container references them.
        containers_raw: list[dict[str, Any]] = []
        refs: dict[str, set[str]] = {
            "image_ids": set(), "image_names": set(), "volumes": set(),
            "network_ids": set(), "network_names": set(),
        }
        container_dependency_needed = bool(kinds & {"images", "volumes", "containers", "networks"})
        if container_dependency_needed:
            containers_raw = self._best_effort("containers", self._containers, [])
            if "containers" not in self.category_errors:
                refs = self._container_references(containers_raw)

        if "images" in kinds:
            if "containers" in self.category_errors:
                self.category_errors["images"] = "dependency_unavailable"
            else:
                images_raw = self._best_effort("images", self._images, [])
                if "images" not in self.category_errors:
                    items: list[CleanupItem] = []
                    for image in images_raw:
                        uid = str(image.get("Id") or image.get("ID") or "")
                        if not uid:
                            continue
                        tags = [str(tag) for tag in image.get("RepoTags") or [] if tag]
                        if uid in refs["image_ids"] or any(tag in refs["image_names"] for tag in tags):
                            continue
                        # API v1.51+ exposes a reliable container count as an
                        # additional fail-closed guard.
                        container_count = image.get("Containers")
                        if isinstance(container_count, int) and container_count > 0:
                            continue
                        # Image sizes are tricky: Docker's per-image Size is a
                        # virtual size, while SharedSize is shared with other
                        # images. Summing Size would overstate what can be
                        # reclaimed. Size-SharedSize is a safe lower bound, but
                        # can understate the final result when several unused
                        # images share layers with each other. Never present
                        # that lower bound as an exact value.
                        total_size = _optional_size(image.get("Size"))
                        shared = _optional_size(image.get("SharedSize"))
                        size: int | None = None
                        if total_size is not None and shared is not None and 0 <= shared <= total_size:
                            size = total_size - shared
                        name = ", ".join(tags) if tags else "<none>:<none>"
                        items.append(CleanupItem("images", uid, name, size, size_complete=False))
                    result["images"] = [i.to_dict() for i in sorted(items, key=lambda x: x.size or -1, reverse=True)]

        if "volumes" in kinds:
            if "containers" in self.category_errors:
                self.category_errors["volumes"] = "dependency_unavailable"
            else:
                # Docker documents dangling=true as "not referenced by any
                # container". We still cross-check all container Mounts below.
                volumes_raw = self._best_effort("volumes", lambda: self._volumes(dangling_only=True), [])
                if "volumes" not in self.category_errors:
                    df_items = {
                        str(item.get("Name")): item
                        for item in self._df_items(usage.get("volumes", {}), "volumes")
                        if item.get("Name")
                    }
                    items: list[CleanupItem] = []
                    for volume in volumes_raw:
                        name = str(volume.get("Name") or "")
                        scope = str(volume.get("Scope") or "local").lower()
                        # Cluster/non-local volumes are intentionally omitted.
                        # Their lifecycle may be controlled by Swarm or another
                        # orchestrator rather than a local container reference.
                        if (
                            not name
                            or name in refs["volumes"]
                            or scope not in {"", "local"}
                            or volume.get("ClusterVolume") is not None
                        ):
                            continue
                        df_item = df_items.get(name, {})
                        usage_data = df_item.get("UsageData") or volume.get("UsageData") or {}
                        ref_count = _optional_size(usage_data.get("RefCount"))
                        if ref_count is not None and ref_count > 0:
                            continue
                        size = _optional_size(usage_data.get("Size"))
                        driver = str(volume.get("Driver") or df_item.get("Driver") or "local")
                        items.append(CleanupItem("volumes", name, name, size, driver))
                    result["volumes"] = [i.to_dict() for i in sorted(items, key=lambda x: x.size or -1, reverse=True)]

        if "containers" in kinds and "containers" not in self.category_errors:
            removable_states = {"created", "exited", "dead"}
            items: list[CleanupItem] = []
            for container in containers_raw:
                state = str(container.get("State") or "").lower()
                if state not in removable_states:
                    continue
                uid = str(container.get("Id") or container.get("ID") or "")
                if not uid:
                    continue
                names = [str(name).lstrip("/") for name in container.get("Names") or [] if name]
                name = names[0] if names else uid[:12]
                # SizeRw is intentionally not requested. Broken snapshot
                # metadata must never take down the cleanup list.
                items.append(CleanupItem("containers", uid, name, None, state or "stopped"))
            result["containers"] = [i.to_dict() for i in sorted(items, key=lambda x: x.name.lower())]

        if "buildcache" in kinds:
            df = usage.get("buildcache", {})
            if not df and "buildcache" in self.stat_warnings:
                self.category_errors["buildcache"] = "stats_unavailable"
            else:
                records = self._df_items(df, "buildcache")
                items: list[CleanupItem] = []
                for entry in records:
                    # Fail closed: only an explicit Docker InUse=false may be
                    # presented as cleanup candidate. BuildKit cache is pruned
                    # as a set; individual records are preview-only.
                    if entry.get("InUse") is not False:
                        continue
                    uid = str(entry.get("ID") or entry.get("Id") or "")
                    if not uid:
                        continue
                    description = str(entry.get("Description") or entry.get("Type") or "Build cache")
                    details = str(entry.get("Type") or "")
                    items.append(CleanupItem(
                        "buildcache",
                        uid,
                        description,
                        _optional_size(entry.get("Size")),
                        details,
                    ))
                result["buildcache"] = [i.to_dict() for i in sorted(items, key=lambda x: x.size or -1, reverse=True)]

        if "networks" in kinds:
            if "containers" in self.category_errors:
                self.category_errors["networks"] = "dependency_unavailable"
            else:
                networks_raw = self._best_effort("networks", lambda: self._networks(dangling_only=True), [])
                if "networks" not in self.category_errors:
                    protected = {"bridge", "host", "none", "ingress", "docker_gwbridge"}
                    items: list[CleanupItem] = []
                    for network in networks_raw:
                        name = str(network.get("Name") or "")
                        uid = str(network.get("Id") or network.get("ID") or "")
                        scope = str(network.get("Scope") or "local").lower()
                        if (
                            not name
                            or not uid
                            or name in protected
                            or bool(network.get("Ingress"))
                            or scope not in {"", "local"}
                        ):
                            continue
                        if name in refs["network_names"] or uid in refs["network_ids"]:
                            continue
                        # GET /networks no longer includes attached-container
                        # details on modern APIs. Inspect each remaining custom
                        # network and fail closed if Docker cannot prove it empty.
                        try:
                            inspected = self._network_inspect(uid)
                        except DockerConnectionError:
                            raise
                        except DockerAPIError as exc:
                            _log_api_warning("network-inspect", exc.status, exc.message)
                            continue
                        attached = inspected.get("Containers")
                        services = inspected.get("Services")
                        if isinstance(attached, dict) and attached:
                            continue
                        if isinstance(services, dict) and services:
                            continue
                        if bool(inspected.get("Ingress")):
                            continue
                        items.append(CleanupItem("networks", uid, name, None, str(network.get("Driver") or "")))
                    result["networks"] = [i.to_dict() for i in sorted(items, key=lambda x: x.name.lower())]

        return result

    @staticmethod
    def _known_sum(items: list[dict[str, Any]]) -> tuple[int | None, bool]:
        if not items:
            return 0, True
        sizes = [item.get("size") for item in items]
        known = [int(size) for size in sizes if isinstance(size, int) and size >= 0]
        if not known:
            return None, False
        complete = len(known) == len(items) and all(item.get("size_complete", True) is not False for item in items)
        return sum(known), complete

    def overview(self) -> dict[str, Any]:
        # Only data needed for cleanup candidates is queried. We deliberately
        # do not mix overall Docker usage (active + inactive) into the cards.
        candidates = self.candidates()

        result: dict[str, Any] = {}
        reclaimable_total = 0
        total_complete = True

        for kind in ("images", "volumes", "containers", "buildcache", "networks"):
            items = candidates[kind]
            available = kind not in self.category_errors
            if kind == "networks":
                result[kind] = {
                    "count": len(items),
                    "reclaimable": None,
                    "reclaimable_complete": True,
                    "available": available,
                }
                continue

            reclaimable, complete = self._known_sum(items)
            if reclaimable is not None:
                reclaimable_total += reclaimable
            if items and not complete:
                total_complete = False

            result[kind] = {
                "count": len(items),
                "reclaimable": reclaimable,
                "reclaimable_complete": complete,
                "available": available,
            }

        # A missing category is a real partial-data condition. Unknown byte
        # sizes alone are represented by the trailing '+' and need no warning.
        partial = bool(self.category_errors)
        if self.category_errors:
            total_complete = False

        result["reclaimable_total"] = reclaimable_total
        result["reclaimable_total_complete"] = total_complete
        result["partial"] = partial
        result["warnings"] = sorted(self.category_errors)
        result["api_version"] = self.api_version
        result["server_api_version"] = self.server_api_version
        result["engine_version"] = self.engine_version
        return result

    @staticmethod
    def _cleanup_error_detail(message: str) -> str:
        cleaned = " ".join(str(message).replace("\x00", " ").split())
        return cleaned[:500]

    def _cleanup_result(
        self,
        uid: str,
        *,
        status: str,
        item: dict[str, Any] | None = None,
        error_code: str | None = None,
        error_detail: str | None = None,
    ) -> dict[str, str]:
        result = {
            "uid": uid,
            "name": str((item or {}).get("name") or uid),
            "status": status,
        }
        if error_code:
            result["error_code"] = error_code
        if error_detail:
            result["error_detail"] = self._cleanup_error_detail(error_detail)
        return result

    def _buildcache_records(self) -> dict[str, dict[str, Any]]:
        df = self._system_df("buildcache")
        return {
            str(entry.get("ID") or entry.get("Id")): entry
            for entry in self._df_items(df, "buildcache")
            if entry.get("ID") or entry.get("Id")
        }

    def _cleanup_buildcache(
        self,
        requested: list[str],
        current_by_id: dict[str, dict[str, Any]],
    ) -> list[dict[str, str]]:
        """Prune Docker's currently unused build cache as one native GC operation.

        BuildKit cache records are graph/GC records, not CRUD objects. Docker may
        report an ID filter as successful without actually removing an individual
        record. ZentDClean therefore uses the same native prune semantics as
        ``docker builder prune --all`` and treats the item list as a preview.
        Active/in-use records remain protected by BuildKit.
        """
        results: list[dict[str, str]] = []
        eligible = [uid for uid in requested if uid in current_by_id]

        for uid in requested:
            if uid not in current_by_id:
                results.append(self._cleanup_result(
                    uid,
                    status="skipped",
                    error_code="no_longer_unused",
                ))

        if not eligible:
            return results

        try:
            self._request("POST", "/build/prune", query={"all": "true"})
        except DockerAPIError as exc:
            logger.warning("Cleanup buildcache failed (%s): %s", exc.status, exc.message)
            detail = self._cleanup_error_detail(exc.message)
            for uid in eligible:
                results.append(self._cleanup_result(
                    uid,
                    status="error",
                    item=current_by_id.get(uid),
                    error_code="docker_error",
                    error_detail=detail,
                ))
            return results

        try:
            remaining = self._buildcache_records()
        except DockerAPIError as exc:
            detail = self._cleanup_error_detail(exc.message)
            for uid in eligible:
                results.append(self._cleanup_result(
                    uid,
                    status="error",
                    item=current_by_id.get(uid),
                    error_code="verification_failed",
                    error_detail=detail,
                ))
            return results

        for uid in eligible:
            item = current_by_id.get(uid)
            state = remaining.get(uid)
            if state is None:
                results.append(self._cleanup_result(uid, status="deleted", item=item))
            elif state.get("InUse") is not False:
                # The record became active while the confirmation dialog was
                # open. BuildKit correctly preserved it.
                results.append(self._cleanup_result(
                    uid,
                    status="skipped",
                    item=item,
                    error_code="no_longer_unused",
                ))
            else:
                results.append(self._cleanup_result(
                    uid,
                    status="error",
                    item=item,
                    error_code="not_deleted",
                    error_detail="Docker kept this unused build-cache record after pruning.",
                ))
        return results

    def cleanup(self, kind: str, ids: list[str]) -> list[dict[str, str]]:
        current = self.candidates(kind).get(kind)
        if current is None:
            raise ValueError("Unknown cleanup type")
        if kind in self.category_errors:
            raise DockerAPIError(503, f"{kind} data is unavailable")

        current_by_id = {str(item["uid"]): item for item in current}
        requested: list[str] = []
        seen: set[str] = set()
        for uid in ids:
            value = str(uid)
            if value and value not in seen:
                requested.append(value)
                seen.add(value)

        if kind == "buildcache":
            return self._cleanup_buildcache(requested, current_by_id)

        results: list[dict[str, str]] = []
        for uid in requested:
            item = current_by_id.get(uid)
            if item is None:
                # The object was unused when the modal opened but is no longer
                # in the freshly generated unused list. Never delete it.
                results.append(self._cleanup_result(
                    uid,
                    status="skipped",
                    error_code="no_longer_unused",
                ))
                continue

            try:
                escaped = quote(uid, safe="")
                if kind == "images":
                    # Delete only the image the user selected. noprune=true
                    # prevents Docker from opportunistically deleting parent
                    # images that were not shown/confirmed in the modal.
                    self._request("DELETE", f"/images/{escaped}", query={"force": "false", "noprune": "true"})
                elif kind == "volumes":
                    self._request("DELETE", f"/volumes/{escaped}", query={"force": "false"})
                elif kind == "containers":
                    self._request("DELETE", f"/containers/{escaped}", query={"v": "false", "force": "false"})
                elif kind == "networks":
                    self._request("DELETE", f"/networks/{escaped}")
                else:
                    raise ValueError("Unknown cleanup type")
                results.append(self._cleanup_result(uid, status="deleted", item=item))
            except DockerAPIError as exc:
                logger.warning("Cleanup %s %s failed (%s): %s", kind, uid[:32], exc.status, exc.message)
                results.append(self._cleanup_result(
                    uid,
                    status="error",
                    item=item,
                    error_code="docker_error",
                    error_detail=exc.message,
                ))
        return results
