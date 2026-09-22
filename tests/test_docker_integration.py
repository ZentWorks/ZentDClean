from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

import pytest

from app.docker_service import DockerService


RUN_INTEGRATION = os.getenv("ZENTDCLEAN_RUN_DOCKER_INTEGRATION") == "1"
RUN_BUILDCACHE = os.getenv("ZENTDCLEAN_RUN_BUILDCACHE_INTEGRATION") == "1"
BASE_IMAGE = os.getenv("ZENTDCLEAN_INTEGRATION_IMAGE", "python:3.14.7-slim")
DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")

pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason="set ZENTDCLEAN_RUN_DOCKER_INTEGRATION=1 to run real Docker safety tests",
)


def _docker(*args: str, input_text: str | None = None, check: bool = True) -> str:
    result = subprocess.run(
        ["docker", *args],
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"docker {' '.join(args)} failed ({result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result.stdout.strip()


def _inspect_container(name: str) -> dict:
    return json.loads(_docker("inspect", name))[0]


def _http_ok(port: int, attempts: int = 30) -> bool:
    url = f"http://127.0.0.1:{port}/"
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def _candidate_ids(service: DockerService, kind: str) -> set[str]:
    return {str(item["uid"]) for item in service.candidates(kind)[kind]}


def _assert_active_container_unchanged(
    container_name: str,
    *,
    expected_id: str,
    expected_image_id: str,
    expected_volume: str,
    expected_network: str,
    expected_port_binding: list[dict[str, str]],
    host_port: int,
) -> None:
    current = _inspect_container(container_name)
    assert current["Id"] == expected_id
    assert current["Image"] == expected_image_id
    assert current["State"]["Running"] is True
    assert current["HostConfig"]["PortBindings"]["8080/tcp"] == expected_port_binding
    assert expected_network in current["NetworkSettings"]["Networks"]
    assert any(
        mount.get("Type") == "volume" and mount.get("Name") == expected_volume
        for mount in current.get("Mounts") or []
    )
    assert _http_ok(host_port), "published HTTP port stopped responding after cleanup"


def test_cleanup_cannot_damage_running_container_or_its_resources(tmp_path: Path):
    if shutil.which("docker") is None:
        pytest.skip("docker CLI is not installed")
    if not Path(DOCKER_SOCKET).is_socket():
        pytest.skip(f"Docker socket is unavailable: {DOCKER_SOCKET}")

    # The CI workflow pre-pulls this image so the integration test itself never
    # depends on a registry request halfway through the safety assertions.
    if subprocess.run(
        ["docker", "image", "inspect", BASE_IMAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode != 0:
        pytest.skip(f"integration base image is not available locally: {BASE_IMAGE}")

    token = uuid.uuid4().hex[:12]
    prefix = f"zentdclean-it-{token}"
    active_container = f"{prefix}-active"
    active_volume = f"{prefix}-active-vol"
    active_network = f"{prefix}-active-net"
    unused_volume = f"{prefix}-unused-vol"
    unused_network = f"{prefix}-unused-net"
    race_volume = f"{prefix}-race-vol"
    race_network = f"{prefix}-race-net"
    stopped_container = f"{prefix}-stopped"
    race_container = f"{prefix}-race-container"
    race_volume_holder = f"{prefix}-race-vol-holder"
    race_image_holder = f"{prefix}-race-image-holder"
    unused_image = f"{prefix}-unused-image:latest"
    race_image = f"{prefix}-race-image:latest"

    cleanup_containers = {
        active_container,
        stopped_container,
        race_container,
        race_volume_holder,
        race_image_holder,
    }
    cleanup_networks = {active_network, unused_network, race_network}
    cleanup_volumes = {active_volume, unused_volume, race_volume}
    cleanup_images = {unused_image, race_image}

    try:
        _docker("volume", "create", active_volume)
        _docker("network", "create", active_network)
        _docker("volume", "create", unused_volume)
        _docker("network", "create", unused_network)
        _docker("volume", "create", race_volume)
        _docker("network", "create", race_network)

        # Create two unique image IDs using only the already-local base image.
        # They let us test exact image deletion and the image race-condition
        # without touching any image that existed before this test.
        dockerfile = f"FROM {BASE_IMAGE}\nLABEL zentdclean.integration={token}\n"
        _docker("build", "--pull=false", "-t", unused_image, "-", input_text=dockerfile)
        dockerfile_race = f"FROM {BASE_IMAGE}\nLABEL zentdclean.integration.race={token}\n"
        _docker("build", "--pull=false", "-t", race_image, "-", input_text=dockerfile_race)

        _docker(
            "run", "-d",
            "--name", active_container,
            "--network", active_network,
            "-v", f"{active_volume}:/data",
            "-p", "127.0.0.1::8080",
            BASE_IMAGE,
            "python", "-m", "http.server", "8080", "--bind", "0.0.0.0",
        )
        _docker("create", "--name", stopped_container, BASE_IMAGE, "true")
        _docker("create", "--name", race_container, BASE_IMAGE, "sleep", "60")

        initial = _inspect_container(active_container)
        active_id = initial["Id"]
        active_image_id = initial["Image"]
        port_binding = initial["HostConfig"]["PortBindings"]["8080/tcp"]
        host_port = int(port_binding[0]["HostPort"])
        assert _http_ok(host_port), "fixture HTTP server never became reachable"

        service = DockerService(socket_path=DOCKER_SOCKET)

        # Running resources must not even appear as cleanup candidates.
        assert active_id not in _candidate_ids(service, "containers")
        assert active_image_id not in _candidate_ids(service, "images")
        assert active_volume not in _candidate_ids(service, "volumes")
        active_network_id = initial["NetworkSettings"]["Networks"][active_network]["NetworkID"]
        assert active_network_id not in _candidate_ids(service, "networks")

        # Even a stale or manually forged cleanup request containing active IDs
        # must fail closed instead of touching those resources.
        assert service.cleanup("containers", [active_id])[0]["status"] == "skipped"
        assert service.cleanup("images", [active_image_id])[0]["status"] == "skipped"
        assert service.cleanup("volumes", [active_volume])[0]["status"] == "skipped"
        assert service.cleanup("networks", [active_network_id])[0]["status"] == "skipped"
        _assert_active_container_unchanged(
            active_container,
            expected_id=active_id,
            expected_image_id=active_image_id,
            expected_volume=active_volume,
            expected_network=active_network,
            expected_port_binding=port_binding,
            host_port=host_port,
        )

        # Real deletion of resources created exclusively for this test.
        unused_image_id = _docker("image", "inspect", "--format", "{{.Id}}", unused_image)
        assert unused_image_id in _candidate_ids(service, "images")
        assert unused_volume in _candidate_ids(service, "volumes")
        unused_network_id = _docker("network", "inspect", "--format", "{{.Id}}", unused_network)
        assert unused_network_id in _candidate_ids(service, "networks")
        stopped_id = _docker("inspect", "--format", "{{.Id}}", stopped_container)
        assert stopped_id in _candidate_ids(service, "containers")

        assert service.cleanup("images", [unused_image_id])[0]["status"] == "deleted"
        assert service.cleanup("volumes", [unused_volume])[0]["status"] == "deleted"
        assert service.cleanup("networks", [unused_network_id])[0]["status"] == "deleted"
        assert service.cleanup("containers", [stopped_id])[0]["status"] == "deleted"
        cleanup_images.discard(unused_image)
        cleanup_volumes.discard(unused_volume)
        cleanup_networks.discard(unused_network)
        cleanup_containers.discard(stopped_container)

        _assert_active_container_unchanged(
            active_container,
            expected_id=active_id,
            expected_image_id=active_image_id,
            expected_volume=active_volume,
            expected_network=active_network,
            expected_port_binding=port_binding,
            host_port=host_port,
        )

        # Race: an unused image becomes referenced after the preview.
        race_image_id = _docker("image", "inspect", "--format", "{{.Id}}", race_image)
        assert race_image_id in _candidate_ids(service, "images")
        _docker("create", "--name", race_image_holder, race_image, "sleep", "60")
        image_race = service.cleanup("images", [race_image_id])[0]
        assert image_race["status"] == "skipped"
        assert image_race["error_code"] == "no_longer_unused"

        # Race: an unused volume becomes referenced by a newly created container.
        assert race_volume in _candidate_ids(service, "volumes")
        _docker("create", "--name", race_volume_holder, "-v", f"{race_volume}:/data", BASE_IMAGE, "true")
        volume_race = service.cleanup("volumes", [race_volume])[0]
        assert volume_race["status"] == "skipped"
        assert volume_race["error_code"] == "no_longer_unused"

        # Race: an unused network gets connected to the running container.
        race_network_id = _docker("network", "inspect", "--format", "{{.Id}}", race_network)
        assert race_network_id in _candidate_ids(service, "networks")
        _docker("network", "connect", race_network, active_container)
        network_race = service.cleanup("networks", [race_network_id])[0]
        assert network_race["status"] == "skipped"
        assert network_race["error_code"] == "no_longer_unused"
        _docker("network", "disconnect", race_network, active_container)

        # Race: a stopped cleanup candidate starts running before deletion.
        race_container_id = _docker("inspect", "--format", "{{.Id}}", race_container)
        assert race_container_id in _candidate_ids(service, "containers")
        _docker("start", race_container)
        container_race = service.cleanup("containers", [race_container_id])[0]
        assert container_race["status"] == "skipped"
        assert container_race["error_code"] == "no_longer_unused"

        _assert_active_container_unchanged(
            active_container,
            expected_id=active_id,
            expected_image_id=active_image_id,
            expected_volume=active_volume,
            expected_network=active_network,
            expected_port_binding=port_binding,
            host_port=host_port,
        )

        # Build-cache pruning is intentionally opt-in because Docker exposes it
        # as one global "all currently unused" GC operation. CI enables this on
        # its disposable runner; local integration runs do not wipe a developer's
        # unrelated cache unless explicitly requested.
        if RUN_BUILDCACHE:
            cache_candidates = service.candidates("buildcache")["buildcache"]
            if cache_candidates:
                cache_ids = [str(item["uid"]) for item in cache_candidates]
                cache_results = service.cleanup("buildcache", cache_ids)
                assert not any(
                    result.get("error_code") in {"docker_error", "verification_failed"}
                    for result in cache_results
                )
                _assert_active_container_unchanged(
                    active_container,
                    expected_id=active_id,
                    expected_image_id=active_image_id,
                    expected_volume=active_volume,
                    expected_network=active_network,
                    expected_port_binding=port_binding,
                    host_port=host_port,
                )

        # The exact same container must survive a restart with the same published
        # port mapping and attached persistent resources.
        _docker("restart", active_container)
        _assert_active_container_unchanged(
            active_container,
            expected_id=active_id,
            expected_image_id=active_image_id,
            expected_volume=active_volume,
            expected_network=active_network,
            expected_port_binding=port_binding,
            host_port=host_port,
        )

    finally:
        # Best-effort cleanup, limited strictly to names created by this test.
        for name in cleanup_containers:
            _docker("rm", "-f", name, check=False)
        for name in cleanup_networks:
            _docker("network", "rm", name, check=False)
        for name in cleanup_volumes:
            _docker("volume", "rm", name, check=False)
        for name in cleanup_images:
            _docker("image", "rm", "-f", name, check=False)
