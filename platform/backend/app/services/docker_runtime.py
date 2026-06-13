"""
DockerRuntimeService — wraps docker-py SDK 7.x.

Each public method has a direct counterpart in labs/_common.sh:
  ensure_network   ↔  ensure_network()
  remove_network   ↔  remove_network()
  pull_image       ↔  docker_pull()
  build_image      ↔  docker build -t …
  run_container    ↔  docker run -d …
  stop_container   ↔  docker rm -f …
  get_container_status  ↔  container_status()
  wait_for_port    ↔  wait_for_port()
  stream_logs      ↔  docker logs -f
"""
import asyncio
import socket
import time
from collections.abc import AsyncGenerator
from typing import Any, Optional

import docker
import docker.types
from docker.errors import BuildError, DockerException, NotFound
from docker.models.containers import Container
from docker.models.networks import Network


class DockerRuntimeService:
    def __init__(self) -> None:
        self._client: docker.DockerClient | None = None

    def _get_client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env(timeout=120)
        return self._client

    # ------------------------------------------------------------------ #
    # Health                                                               #
    # ------------------------------------------------------------------ #

    def ping(self) -> bool:
        try:
            return bool(self._get_client().ping())
        except DockerException:
            return False

    # ------------------------------------------------------------------ #
    # Network                                                              #
    # ------------------------------------------------------------------ #

    def ensure_network(self, name: str, subnet: str) -> None:
        """Idempotent bridge network creation — matches ensure_network() in _common.sh."""
        try:
            self._get_client().networks.get(name)
            return
        except NotFound:
            pass
        self._get_client().networks.create(
            name,
            driver="bridge",
            ipam=docker.types.IPAMConfig(
                pool_configs=[docker.types.IPAMPool(subnet=subnet)]
            ),
        )

    def remove_network(self, name: str) -> None:
        """Silent remove — matches remove_network() in _common.sh."""
        try:
            net: Network = self._get_client().networks.get(name)
            net.remove()
        except (NotFound, DockerException):
            pass

    # ------------------------------------------------------------------ #
    # Volumes                                                              #
    # ------------------------------------------------------------------ #

    def ensure_volume(self, name: str) -> None:
        try:
            self._get_client().volumes.get(name)
        except NotFound:
            self._get_client().volumes.create(name)

    def remove_volume(self, name: str) -> None:
        try:
            vol = self._get_client().volumes.get(name)
            vol.remove()
        except (NotFound, DockerException):
            pass

    # ------------------------------------------------------------------ #
    # Images                                                               #
    # ------------------------------------------------------------------ #

    def build_image(self, tag: str, context_path: str) -> None:
        """Blocking build from a Dockerfile directory. Raises BuildError on failure."""
        self._get_client().images.build(path=context_path, tag=tag, rm=True, forcerm=True)

    def pull_image(self, image: str) -> None:
        """Pull with local cache check — matches docker_pull() in _common.sh."""
        try:
            self._get_client().images.get(image)
            return  # already cached
        except NotFound:
            pass
        self._get_client().images.pull(image)

    # ------------------------------------------------------------------ #
    # Containers                                                           #
    # ------------------------------------------------------------------ #

    def _force_remove_container(self, name: str) -> None:
        """Matches ensure_container_gone() in _common.sh."""
        try:
            container: Container = self._get_client().containers.get(name)
            container.remove(force=True)
        except NotFound:
            pass

    def run_container(
        self,
        name: str,
        image: str,
        network: str,
        ip: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
        volumes: Optional[dict[str, dict[str, str]]] = None,
        privileged: bool = False,
        command: Optional[str] = None,
    ) -> str:
        """
        Start a detached container with restart=unless-stopped.
        Returns the short container ID.
        """
        self._force_remove_container(name)

        networking_config = None
        if ip:
            networking_config = self._get_client().api.create_networking_config({
                network: self._get_client().api.create_endpoint_config(ipv4_address=ip)
            })

        container: Container = self._get_client().containers.run(
            image=image,
            name=name,
            network=network,
            networking_config=networking_config,
            detach=True,
            restart_policy={"Name": "unless-stopped"},
            environment=environment or {},
            volumes=volumes or {},
            privileged=privileged,
            command=command,
        )
        if ip:
            # When networking_config is used, the container starts without network,
            # then the config wires it. Connect explicitly if needed.
            pass
        return container.short_id

    def stop_container(self, name: str) -> None:
        """Matches docker rm -f in lab stop handlers."""
        self._force_remove_container(name)

    def exec_in_container(self, name: str, command: str) -> tuple[int, bytes]:
        """Run a command inside a running container and return (exit_code, output)."""
        container: Container = self._get_client().containers.get(name)
        result = container.exec_run(command, demux=False)
        return result.exit_code, result.output or b""

    # ------------------------------------------------------------------ #
    # Status                                                               #
    # ------------------------------------------------------------------ #

    def get_container_status(self, name: str) -> str:
        """Returns 'running' | 'exited' | 'not_found' | other Docker state string."""
        try:
            container: Container = self._get_client().containers.get(name)
            return container.status
        except NotFound:
            return "not_found"

    def get_all_octorig_containers(self) -> list[dict[str, Any]]:
        """All containers whose name starts with 'octorig-' (CLI and platform alike)."""
        containers = self._get_client().containers.list(all=True, filters={"name": "octorig-"})
        result = []
        for c in containers:
            result.append({
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                "created": c.attrs.get("Created", ""),
            })
        return result

    # ------------------------------------------------------------------ #
    # Port polling                                                         #
    # ------------------------------------------------------------------ #

    def wait_for_port(self, host: str, port: int, timeout: int = 60) -> bool:
        """Poll until TCP port is open or timeout expires. Returns True on success."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection((host, port), timeout=2):
                    return True
            except OSError:
                time.sleep(1)
        return False

    # ------------------------------------------------------------------ #
    # Log streaming                                                        #
    # ------------------------------------------------------------------ #

    async def stream_logs(
        self,
        container_name: str,
        tail: int = 100,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator yielding log lines as strings.
        docker-py logs() is blocking — we run it in an executor.
        """
        loop = asyncio.get_event_loop()

        def _get_generator():
            try:
                container = self._get_client().containers.get(container_name)
                return container.logs(stream=True, follow=True, tail=tail)
            except NotFound:
                return None

        gen = await loop.run_in_executor(None, _get_generator)
        if gen is None:
            yield f"[octorig] container '{container_name}' not found\n"
            return

        def _next_chunk(g):
            try:
                return next(g)
            except StopIteration:
                return None

        while True:
            chunk = await loop.run_in_executor(None, _next_chunk, gen)
            if chunk is None:
                break
            yield chunk.decode("utf-8", errors="replace")


# Module-level singleton — imported by lab_service and api routers
docker_service = DockerRuntimeService()
