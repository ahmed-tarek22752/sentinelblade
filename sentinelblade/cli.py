# SentinelBlade - Copyright (c) 2026 Ahmed Tarek Salah Thaqib - MIT License
"""Command-line interface for SentinelBlade."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from typing import Any, Sequence

from . import __author__, __version__
from .banner import color, print_banner
from .hasher import hash_file
from .monitor import check_baseline, create_baseline
from .passcheck import check_password
from .portscan import SCAN_WARNING, scan_ports
from .report import load_report, write_report

_RED = "\033[91m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"


def _add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", help="Export this command's results to a .json or .txt file.")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the SentinelBlade argument parser."""
    parser = argparse.ArgumentParser(prog="sentinelblade", description="SentinelBlade: Forge your defense.")
    parser.add_argument("--version", action="version", version=f"SentinelBlade {__version__} | Author: {__author__}")
    commands = parser.add_subparsers(dest="command", required=True)

    hash_parser = commands.add_parser("hash", help="Hash a file and optionally verify a digest.")
    hash_parser.add_argument("file", help="File to hash.")
    hash_parser.add_argument("--algorithm", choices=("sha256", "sha512", "md5"), default="sha256")
    hash_parser.add_argument("--verify", metavar="DIGEST", help="Compare the computed digest with DIGEST.")
    _add_output_argument(hash_parser)

    monitor_parser = commands.add_parser("monitor", help="Create or check a file integrity baseline.")
    monitor_commands = monitor_parser.add_subparsers(dest="monitor_action", required=True)
    for action in ("baseline", "check"):
        action_parser = monitor_commands.add_parser(action, help=f"Monitor {action} operation.")
        action_parser.add_argument("folder", help="Folder to monitor.")
        _add_output_argument(action_parser)

    ports_parser = commands.add_parser("ports", help="Scan TCP ports on localhost or an authorized host.")
    ports_parser.add_argument("host", help="Target hostname or IP address.")
    ports_parser.add_argument("--range", dest="port_range", default="1-1024", metavar="START-END")
    ports_parser.add_argument("--timeout", type=float, default=0.5, help="Per-connection timeout in seconds.")
    ports_parser.add_argument("--workers", type=int, default=100, help="Concurrent worker limit (1-1024).")
    ports_parser.add_argument("--authorized", action="store_true", help="I own or have written permission to test this non-local target.")
    _add_output_argument(ports_parser)

    passcheck_parser = commands.add_parser("passcheck", help="Check a password without displaying or retaining it.")
    _add_output_argument(passcheck_parser)

    report_parser = commands.add_parser("report", help="Convert a saved JSON result to a timestamped JSON or TXT report.")
    report_parser.add_argument("--input", required=True, help="JSON result file created by another command.")
    report_parser.add_argument("--output", required=True, help="Destination report (.json or .txt).")
    return parser


def _print_result(result: dict[str, Any]) -> None:
    """Print a concise human-readable representation of a command result."""
    command = result.get("command")
    if command == "hash":
        print(f"{result['algorithm'].upper()}  {result['digest']}  {result['path']}")
        if "verified" in result:
            label = "MATCH" if result["verified"] else "MISMATCH"
            code = _GREEN if result["verified"] else _RED
            print(color(label, code))
    elif command == "monitor baseline":
        print(f"Baseline saved: {result['baseline']} ({result['file_count']} files)")
    elif command == "monitor check":
        for category, label, code in (("new", "NEW", _GREEN), ("modified", "MODIFIED", _YELLOW), ("deleted", "DELETED", _RED)):
            for path in result[category]:
                print(f"{color(label, code)}  {path}")
        if result["clean"]:
            print(color("No changes detected.", _GREEN))
        elif not (result["new"] or result["modified"] or result["deleted"]):
            print("No changes detected.")
    elif command == "ports":
        print(color(SCAN_WARNING, _YELLOW))
        print(f"Scanning {result['host']} ({result['range']})")
        if result["open_ports"]:
            for item in result["open_ports"]:
                print(f"OPEN  {item['port']}/tcp  {item['service']}")
        else:
            print("No open ports found in the selected range.")
    elif command == "passcheck":
        print(f"Strength score: {result['score']}/100")
        print(f"Length: {result['length']} | Estimated entropy: {result['entropy_bits_estimate']} bits")
        for tip in result["tips"]:
            print(f"Tip: {tip}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


def _run_command(arguments: argparse.Namespace) -> dict[str, Any] | None:
    """Execute a parsed command and return its exportable result."""
    if arguments.command == "hash":
        return hash_file(arguments.file, arguments.algorithm, arguments.verify)
    if arguments.command == "monitor":
        if arguments.monitor_action == "baseline":
            return create_baseline(arguments.folder)
        return check_baseline(arguments.folder)
    if arguments.command == "ports":
        return scan_ports(
            arguments.host,
            arguments.port_range,
            timeout=arguments.timeout,
            workers=arguments.workers,
            authorized=arguments.authorized,
        )
    if arguments.command == "passcheck":
        if not sys.stdin.isatty():
            raise ValueError("passcheck requires an interactive terminal so password input stays hidden.")
        password = getpass.getpass("Password (input hidden): ")
        result = check_password(password)
        del password
        return result
    if arguments.command == "report":
        report_data = load_report(arguments.input)
        path = write_report(report_data, arguments.output)
        print(f"Report written: {path}")
        return None
    return None


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    values = list(sys.argv[1:] if argv is None else argv)
    if "--version" not in values:
        print_banner()
    parser = build_parser()
    arguments = parser.parse_args(values)
    try:
        result = _run_command(arguments)
        if result is not None:
            _print_result(result)
            output = getattr(arguments, "output", None)
            if output:
                path = write_report(result, output)
                print(f"Report written: {path}")
                result["report"] = str(path)
        return 0
    except (EOFError, OSError, PermissionError, ValueError) as error:
        print(color(f"Error: {error}", _RED), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
