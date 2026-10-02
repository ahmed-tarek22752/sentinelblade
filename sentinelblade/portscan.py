# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Permission-conscious TCP port scanning for authorized targets."""

from __future__ import annotations

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

SCAN_WARNING = "Only scan systems you own or have written permission to test."
COMMON_SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 68: "dhcp", 80: "http", 110: "pop3",
    123: "ntp", 135: "msrpc", 139: "netbios-ssn", 143: "imap",
    443: "https", 445: "microsoft-ds", 3306: "mysql", 3389: "rdp",
    5432: "postgresql", 5900: "vnc", 8080: "http-proxy",
}


def parse_port_range(value: str) -> tuple[int, int]:
    """Parse and validate an inclusive ``START-END`` port range."""
    try:
        start_text, end_text = value.split("-", maxsplit=1)
        start, end = int(start_text), int(end_text)
    except (ValueError, AttributeError) as error:
        raise ValueError("Port range must use START-END format, for example 1-1024.") from error
    if not (1 <= start <= end <= 65535):
        raise ValueError("Ports must satisfy 1 <= START <= END <= 65535.")
    return start, end


def scan_ports(
    host: str,
    port_range: str = "1-1024",
    *,
    timeout: float = 0.5,
    workers: int = 100,
    authorized: bool = False,
) -> dict[str, Any]:
    """Scan TCP ports on localhost or a target the user explicitly authorizes."""
    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero.")
    if workers < 1 or workers > 1024:
        raise ValueError("Workers must be between 1 and 1024.")
    start, end = parse_port_range(port_range)
    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as error:
        raise ValueError(f"Could not resolve host: {host}") from error
    if not addresses:
        raise ValueError(f"Could not resolve host: {host}")
    is_loopback = all(
        ipaddress.ip_address(address[4][0].split("%", 1)[0]).is_loopback
        for address in addresses
    )
    if not is_loopback and not authorized:
        raise PermissionError(f"{SCAN_WARNING} For non-local targets, add --authorized only when permitted.")

    def probe(port: int) -> int | None:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return port
        except (OSError, OverflowError):
            return None

    open_ports: list[int] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(probe, port) for port in range(start, end + 1)]
        for future in as_completed(futures):
            port = future.result()
            if port is not None:
                open_ports.append(port)
    open_ports.sort()
    return {
        "command": "ports",
        "host": host,
        "range": f"{start}-{end}",
        "warning": SCAN_WARNING,
        "open_ports": [
            {"port": port, "service": COMMON_SERVICES.get(port, "unknown")}
            for port in open_ports
        ],
    }
