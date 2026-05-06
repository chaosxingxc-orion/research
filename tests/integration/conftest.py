"""Integration test fixtures: real agent-server subprocess.

Per RIA architecture v2 §5.5 + §0.4 — integration tests run against a real
local ``agent-server serve`` subprocess. Stubs are forbidden under the
``integration`` marker (G-RIA-20).

Per RIA Wave R-W1 Guard rail 2 — fixture probes a documented route inventory
before yielding (G-RIA-13). Mirrors hi-agent W36-A5 B13 silent-route-omission
defence on the consumer side.
"""

from __future__ import annotations

import contextlib
import os
import subprocess
import time
from collections.abc import Iterator
from typing import Final

import httpx
import pytest

# Documented route inventory probed before fixture yields.
# Mirrors hi-agent's `agent-server-northbound-contract-v1.md` known surface.
# 404 on any of these = silent route omission = fail.
REQUIRED_ROUTES: Final[tuple[tuple[str, str], ...]] = (
    ("GET", "/v1/manifest"),
    ("GET", "/v1/healthz"),
)

# Routes that are expected to exist but may legitimately return 404 on
# empty payload; the probe rejects only 405 (method-not-allowed) or
# 501 (not-implemented), both of which signal silent omission.
REACHABLE_ROUTES: Final[tuple[tuple[str, str], ...]] = (
    ("GET", "/v1/runs"),
)

DEFAULT_PORT: Final[int] = 18000
DEFAULT_POSTURE: Final[str] = "research"
READY_TIMEOUT_S: Final[float] = 30.0
PROBE_TIMEOUT_S: Final[float] = 5.0


def _start_agent_server(port: int, posture: str) -> subprocess.Popen[bytes]:
    """Spawn ``agent-server serve`` as a subprocess.

    Honours environment override ``AGENT_SERVER_BIN`` for the binary path.
    Sets ``HI_AGENT_POSTURE`` and ``AGENT_SERVER_PORT`` for the child.
    """
    bin_path = os.environ.get("AGENT_SERVER_BIN", "agent-server")
    env = dict(os.environ)
    env["HI_AGENT_POSTURE"] = posture
    env["AGENT_SERVER_PORT"] = str(port)
    cmd = [bin_path, "serve", "--port", str(port)]
    return subprocess.Popen(  # noqa: S603 - controlled binary, no shell
        cmd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def _wait_for_ready(base_url: str, timeout: float = READY_TIMEOUT_S) -> None:
    """Poll ``/v1/healthz`` until any non-5xx response or timeout."""
    deadline = time.monotonic() + timeout
    last_exc: Exception | None = None
    with httpx.Client(timeout=2.0) as client:
        while time.monotonic() < deadline:
            try:
                response = client.get(f"{base_url}/v1/healthz")
                if response.status_code < 500:
                    return
            except Exception as exc:  # noqa: BLE001 - readiness loop
                last_exc = exc
            time.sleep(0.25)
    raise RuntimeError(
        f"agent-server did not become ready at {base_url}/v1/healthz within {timeout}s; "
        f"last exception: {last_exc}",
    )


def _probe_route_presence(base_url: str) -> None:
    """G-RIA-13 contract: probe documented routes return non-404 / non-405 / non-501.

    A 404 on a REQUIRED route, or 405/501 on a REACHABLE route, indicates
    silent route omission - the platform booted but did not register the
    route. This is hi-agent W36-A5 B13's failure mode; we surface it on the
    consumer side at fixture time, not at first test traffic.
    """
    with httpx.Client(timeout=PROBE_TIMEOUT_S) as client:
        for method, path in REQUIRED_ROUTES:
            response = client.request(method, f"{base_url}{path}")
            if response.status_code == 404:
                raise RuntimeError(
                    f"Route presence probe failed: {method} {path} returned 404. "
                    f"Likely silent route omission (hi-agent B13 family).",
                )
        for method, path in REACHABLE_ROUTES:
            response = client.request(method, f"{base_url}{path}")
            if response.status_code in (405, 501):
                raise RuntimeError(
                    f"Route presence probe failed: {method} {path} returned "
                    f"{response.status_code}. Method-not-allowed / not-implemented "
                    f"on a documented route.",
                )


@pytest.fixture(scope="session")
def real_agent_server() -> Iterator[str]:
    """Spawn a real ``agent-server serve`` subprocess for the test session.

    Requires:
        - hi-agent installed and on PATH (or ``AGENT_SERVER_BIN`` env var)
        - port ``AGENT_SERVER_TEST_PORT`` (default 18000) available
        - posture configured via ``AGENT_SERVER_TEST_POSTURE`` (default 'research')

    The fixture probes the documented route inventory before yielding; tests
    that depend on this fixture can rely on the platform surface being
    actually-served, not just booted.

    Yields:
        Base URL string, e.g. ``'http://127.0.0.1:18000'``.
    """
    port = int(os.environ.get("AGENT_SERVER_TEST_PORT", str(DEFAULT_PORT)))
    posture = os.environ.get("AGENT_SERVER_TEST_POSTURE", DEFAULT_POSTURE)
    base_url = f"http://127.0.0.1:{port}"
    proc = _start_agent_server(port, posture)
    try:
        _wait_for_ready(base_url)
        _probe_route_presence(base_url)
        yield base_url
    finally:
        proc.terminate()
        with contextlib.suppress(subprocess.TimeoutExpired):
            proc.wait(timeout=10.0)
        if proc.returncode is None:
            proc.kill()
            proc.wait(timeout=5.0)
