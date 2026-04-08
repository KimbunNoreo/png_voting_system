#!/usr/bin/env python
"""Minimal Django-style management entry point for SecureVote PNG."""

from __future__ import annotations

import json
import sys

from config import get_settings
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
