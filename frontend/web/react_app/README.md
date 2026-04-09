# SecureVote PNG Simple Frontend

This is a lightweight single-page frontend for the current Phase 1 local runtimes.

## What It Covers

- voter token verification and vote casting against the local gateway runtime
- observer audit, tally, compliance, and offline sync evidence review
- admin offline sync staging, flushing, signed export, and evidence bundle retrieval
- one-click demo scenario with profile modes:
  - `Smoke Check`: health + token + cast + offline stage/flush
  - `Full Evidence Run`: smoke checks + compliance report + evidence bundle
- one-click JSON export of the latest scenario run (`Export Scenario Report`)
- scenario import/replay support:
  - import a previously exported JSON report
  - auto-apply baseline profile/token/election values
  - replay the imported scenario and compare current vs baseline summary
  - visual side-by-side diff table with match/diff status per key field
- one-click diff summary copy (`Copy Diff Summary`) to capture mismatches as JSON
- one-click diff summary download (`Download Diff JSON`) for clipboard-restricted environments
- clickable diff badge (`No Data`/`Clean`/`N Diff`) that jumps to and highlights the diff panel
- keyboard shortcuts:
  - `r`: run scenario
  - `c`: copy diff summary
  - `d`: download diff summary
  - `h`: check health
- built-in help modal:
  - open with `Help` button or `?`
  - close with `Close`, `Esc`, or backdrop click
- endpoint target labels and button styling:
  - `Gateway` actions are visually marked in green
  - `Offline Sync` actions are visually marked in blue
  - `Mixed` markers identify cross-runtime flows
- endpoint hint tools:
  - hover or focus action buttons to preview `service | method path`
  - `Copy Current` copies the currently selected endpoint hint
  - `Copy Endpoint Map` copies all action endpoints as JSON
  - endpoint hints are also applied to accessibility labels
- tabbed workflow navigation for voter, observer, and offline sync operations
- live request timeline with status and latency
- request timeline tools:
  - service filter (`All`, `Gateway`, `Offline Sync`, `Mixed/Local`)
  - status filter (`All`, `Success`, `4xx`, `5xx`, `Network`)
  - latency filter (`Slow >= N ms` + `Slow Only`)
  - `Fail Only` filter for quick error triage
  - `Retry Last Failed` replays the newest failed request in the active timeline filter
  - per-row `Retry` button on failed timeline entries for targeted replay
  - `Copy Failed Endpoints` to quickly share unique failed routes
  - `Copy Visible Endpoints` to copy endpoints from the currently filtered timeline view
  - `Export JSON` to download raw timeline entries for debugging/audit notes
  - `Export CSV` for spreadsheet-style analysis
- persisted field values (base URLs, tokens, and IDs) in browser local storage

## How To Use

1. Start the local gateway runtime:

```bash
python manage.py runserver 127.0.0.1:8000
```

2. Start the standalone offline sync runtime:

```bash
python manage.py run-offline-sync 127.0.0.1:8100
```

3. Serve this folder with any static file server. For example:

```bash
python -m http.server 4173
```

4. Open:

```text
http://127.0.0.1:4173/frontend/web/react_app/
```

## Notes

- The UI assumes the local demo token conventions already implemented in the backend:
  - voter tokens start with `demo-`
  - observer tokens start with `observer-`
  - admin tokens start with `admin-`
- This frontend is intentionally simple and runtime-oriented. It is a usable control surface for the currently implemented local services, not a production citizen-facing portal.
