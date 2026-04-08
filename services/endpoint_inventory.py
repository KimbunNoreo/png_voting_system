"""Shared endpoint inventory for operator-facing runtimes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointDefinition:
    label: str
    method: str
    path: str

    def banner_line(self) -> str:
        return f"{self.label}: {self.method} {self.path}"

    def markdown_line(self) -> str:
        return f"- `{self.method} {self.path}`: {self.label}"


LOCAL_RUNTIME_ENDPOINTS: tuple[EndpointDefinition, ...] = (
    EndpointDefinition("Health", "GET", "/health"),
    EndpointDefinition("Verify token", "POST", "/api/v1/vote/verify-token"),
    EndpointDefinition("Cast vote", "POST", "/api/v1/vote/cast"),
    EndpointDefinition("Ballot", "GET", "/api/v1/vote/ballots/ballot-2026"),
    EndpointDefinition("Observer audit", "GET", "/api/v1/vote/observer/audit"),
    EndpointDefinition("Observer tally", "GET", "/api/v1/vote/observer/tally/election-2026"),
    EndpointDefinition("Compliance report", "GET", "/api/v1/vote/compliance/report"),
    EndpointDefinition("Offline sync evidence", "GET", "/api/v1/vote/compliance/offline-sync-evidence"),
)


OFFLINE_SYNC_RUNTIME_ENDPOINTS: tuple[EndpointDefinition, ...] = (
    EndpointDefinition("Health", "GET", "/health"),
    EndpointDefinition("Ready", "GET", "/ready"),
    EndpointDefinition("Stage", "POST", "/api/v1/offline-sync/stage"),
    EndpointDefinition("Queue", "GET", "/api/v1/offline-sync/queue"),
    EndpointDefinition("Flush", "POST", "/api/v1/offline-sync/flush"),
    EndpointDefinition("Approvals", "GET", "/api/v1/offline-sync/approvals"),
    EndpointDefinition("Operations", "GET", "/api/v1/offline-sync/operations"),
    EndpointDefinition("Operations Export", "GET", "/api/v1/offline-sync/operations/export"),
    EndpointDefinition("Operations Evidence Bundle", "GET", "/api/v1/offline-sync/operations/evidence-bundle"),
    EndpointDefinition("Status", "GET", "/api/v1/offline-sync/status"),
)


def render_inventory_lines(endpoints: tuple[EndpointDefinition, ...]) -> list[str]:
    return [endpoint.banner_line() for endpoint in endpoints]


def render_inventory_markdown(title: str, endpoints: tuple[EndpointDefinition, ...]) -> str:
    lines = [f"### {title}", ""]
    lines.extend(endpoint.markdown_line() for endpoint in endpoints)
    return "\n".join(lines)
