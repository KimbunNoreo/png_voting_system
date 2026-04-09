#!/usr/bin/env python
"""Minimal Django-style management entry point for SecureVote PNG."""

from __future__ import annotations

import json
import sys

from config import get_settings
from services.endpoint_inventory import (
    LOCAL_RUNTIME_ENDPOINTS,
    OFFLINE_SYNC_RUNTIME_ENDPOINTS,
    render_inventory_lines,
    render_inventory_markdown,
)
from services.readiness import run_readiness_suite
from services.api_gateway.local_runtime import run_local_demo_server
from services.offline_sync_service.runtime import run_offline_sync_server


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    settings = get_settings()
    command = args[0] if args else "show-config"

    if command == "show-config":
        print(json.dumps({"app_name": settings.app_name, "debug": settings.debug}, indent=2))
        return 0
    if command == "check-phase1":
        if settings.staged_rollout.phase1_only:
            print("phase1-only")
            return 0
        print("phase-misconfigured")
        return 1
    if command == "readiness-check":
        profile = args[1] if len(args) > 1 else "core"
        try:
            result = run_readiness_suite(profile)
        except ValueError as exc:
            print(str(exc))
            return 2
        print(
            json.dumps(
                {
                    "profile": result.profile,
                    "tests_run": result.tests_run,
                    "failures": result.failures,
                    "errors": result.errors,
                    "successful": result.successful,
                },
                indent=2,
            )
        )
        return 0 if result.successful else 1
    if command == "list-endpoints":
        markdown = "--markdown" in args[1:]
        filtered_args = [arg for arg in args[1:] if arg != "--markdown"]
        target = filtered_args[0] if filtered_args else "all"
        if target not in {"all", "local", "offline-sync"}:
            print(f"unknown endpoint inventory target: {target}")
            return 2
        if markdown:
            sections: list[str] = []
            if target in {"all", "local"}:
                sections.append(render_inventory_markdown("Local Runtime", LOCAL_RUNTIME_ENDPOINTS))
            if target in {"all", "offline-sync"}:
                sections.append(render_inventory_markdown("Offline Sync Runtime", OFFLINE_SYNC_RUNTIME_ENDPOINTS))
            print("\n\n".join(sections))
            return 0
        if target in {"all", "local"}:
            print("[local-runtime]")
            for line in render_inventory_lines(LOCAL_RUNTIME_ENDPOINTS):
                print(line)
        if target == "all":
            print()
        if target in {"all", "offline-sync"}:
            print("[offline-sync-runtime]")
            for line in render_inventory_lines(OFFLINE_SYNC_RUNTIME_ENDPOINTS):
                print(line)
        return 0
    if command == "runserver":
        host = "127.0.0.1"
        port = 8000
        if len(args) > 1 and ":" in args[1]:
            host, raw_port = args[1].split(":", 1)
            port = int(raw_port)
        elif len(args) > 1:
            port = int(args[1])
        run_local_demo_server(host=host, port=port)
        return 0
    if command == "run-offline-sync":
        host = "127.0.0.1"
        port = 8100
        if len(args) > 1 and ":" in args[1]:
            host, raw_port = args[1].split(":", 1)
            port = int(raw_port)
        elif len(args) > 1:
            port = int(args[1])
        run_offline_sync_server(host=host, port=port)
        return 0

    print(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
