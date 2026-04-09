const byId = (id) => document.getElementById(id);

const pretty = (value) => JSON.stringify(value, null, 2);
const REQUEST_HISTORY_LIMIT = 40;
const REQUEST_HISTORY = [];
let HISTORY_ENTRY_SEQ = 0;
let HISTORY_FAIL_ONLY = false;
let HISTORY_SERVICE_FILTER = "all";
let HISTORY_STATUS_FILTER = "all";
let HISTORY_SLOW_ONLY = false;
let HISTORY_SLOW_THRESHOLD_MS = 1000;
let LAST_SCENARIO_REPORT = null;
let IMPORTED_SCENARIO_REPORT = null;
let LAST_SCENARIO_DIFF_ROWS = [];
const ACTION_ENDPOINT_HINTS = {
  healthCheckButton: { service: "Gateway + Offline Sync", method: "GET", path: "/health" },
  verifyTokenButton: { service: "Gateway", method: "POST", path: "/api/v1/vote/verify-token" },
  castVoteButton: { service: "Gateway", method: "POST", path: "/api/v1/vote/cast-vote" },
  auditButton: { service: "Gateway", method: "GET", path: "/api/v1/vote/observer/audit" },
  tallyButton: { service: "Gateway", method: "GET", path: "/api/v1/vote/observer/tally/{election_id}" },
  complianceButton: { service: "Gateway", method: "GET", path: "/api/v1/vote/compliance/report" },
  evidenceButton: { service: "Gateway", method: "GET", path: "/api/v1/vote/compliance/offline-sync-evidence" },
  stageOfflineButton: { service: "Offline Sync", method: "POST", path: "/api/v1/offline-sync/stage" },
  queueOfflineButton: { service: "Offline Sync", method: "GET", path: "/api/v1/offline-sync/queue" },
  flushOfflineButton: { service: "Offline Sync", method: "POST", path: "/api/v1/offline-sync/flush" },
  operationsOfflineButton: { service: "Offline Sync", method: "GET", path: "/api/v1/offline-sync/operations" },
  statusOfflineButton: { service: "Offline Sync", method: "GET", path: "/api/v1/offline-sync/status" },
  exportOfflineButton: { service: "Offline Sync", method: "GET", path: "/api/v1/offline-sync/operations/export" },
  bundleOfflineButton: { service: "Offline Sync", method: "GET", path: "/api/v1/offline-sync/operations/evidence-bundle" },
  runScenarioButton: { service: "Mixed", method: "MULTI", path: "scenario chain" },
  replayScenarioButton: { service: "Mixed", method: "MULTI", path: "imported scenario replay" },
  exportScenarioButton: { service: "Local", method: "LOCAL", path: "download latest scenario report" },
  copyDiffButton: { service: "Local", method: "LOCAL", path: "copy mismatch summary" },
  downloadDiffButton: { service: "Local", method: "LOCAL", path: "download mismatch summary" },
};
let LAST_ENDPOINT_HINT_TEXT = "No endpoint selected yet.";

function setDiffBadge(text, state) {
  const badge = byId("diffBadge");
  if (!badge) return;
  badge.textContent = text;
  badge.classList.remove("neutral", "clean", "alert");
  badge.classList.add(state);
}

function focusDiffPanel() {
  const panel = byId("scenarioDiffPanel");
  if (!panel) return;
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
  panel.classList.add("focused");
  setTimeout(() => panel.classList.remove("focused"), 900);
}

function shouldIgnoreShortcut(event) {
  if (event.defaultPrevented) return true;
  if (event.ctrlKey || event.metaKey || event.altKey) return true;
  const target = event.target;
  if (!target) return false;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (target.isContentEditable) return true;
  return false;
}

function handleGlobalShortcut(event) {
  if (shouldIgnoreShortcut(event)) return;
  const key = event.key.toLowerCase();
  if (key === "?") {
    event.preventDefault();
    openHelpModal();
    return;
  }
  if (key === "r") {
    event.preventDefault();
    runDemoScenario();
    return;
  }
  if (key === "c") {
    event.preventDefault();
    copyDiffSummary();
    return;
  }
  if (key === "d") {
    event.preventDefault();
    downloadDiffSummary();
    return;
  }
  if (key === "h") {
    event.preventDefault();
    verifyHealth();
  }
}

function openHelpModal() {
  const modal = byId("helpModal");
  modal.classList.remove("hidden");
}

function closeHelpModal() {
  const modal = byId("helpModal");
  modal.classList.add("hidden");
}

function handleModalKeydown(event) {
  if (event.key === "Escape") {
    closeHelpModal();
  }
}

function handleModalBackdropClick(event) {
  const modal = byId("helpModal");
  if (event.target === modal) {
    closeHelpModal();
  }
}
const PERSISTED_FIELDS = [
  "gatewayBaseUrl",
  "offlineSyncBaseUrl",
  "verifyToken",
  "ballotId",
  "electionId",
  "deviceId",
  "candidate",
  "observerToken",
  "observerElectionId",
  "evidenceCaseId",
  "adminToken",
  "offlineTokenHash",
  "offlineCreatedAt",
  "offlineDeviceId",
  "offlineApprovers",
  "offlineCaseId",
  "scenarioProfile",
];

function setOutput(element, value, isError = false) {
  element.textContent = typeof value === "string" ? value : pretty(value);
  element.classList.toggle("error", isError);
  element.classList.toggle("success", !isError);
}

function formatEndpointHint(meta) {
  return `${meta.service} | ${meta.method} ${meta.path}`;
}

function setEndpointHintText(text) {
  const hintElement = byId("endpointHintText");
  if (!hintElement) return;
  hintElement.textContent = text;
}

function updateEndpointHint(meta) {
  LAST_ENDPOINT_HINT_TEXT = formatEndpointHint(meta);
  setEndpointHintText(LAST_ENDPOINT_HINT_TEXT);
}

function appendOutputLine(element, line) {
  const current = element.textContent?.trim();
  element.textContent = current ? `${current}\n${line}` : line;
}

function downloadJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function downloadText(filename, content, mimeType = "text/plain;charset=utf-8") {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function applyActionEndpointHints() {
  for (const [id, meta] of Object.entries(ACTION_ENDPOINT_HINTS)) {
    const element = byId(id);
    if (!element) continue;
    const hint = `${meta.service} · ${meta.method} ${meta.path}`;
    element.title = hint;
    const label = (element.textContent || "").trim();
    element.setAttribute("aria-label", label ? `${label} (${hint})` : hint);
  }
}

function normalizeScenarioProfile(value) {
  return value === "smoke" ? "smoke" : "full";
}

function applyActionEndpointHintsV2() {
  for (const [id, meta] of Object.entries(ACTION_ENDPOINT_HINTS)) {
    const element = byId(id);
    if (!element) continue;
    const hint = formatEndpointHint(meta);
    element.title = hint;
    element.dataset.endpointHint = hint;
    const label = (element.textContent || "").trim();
    element.setAttribute("aria-label", label ? `${label} (${hint})` : hint);
    element.addEventListener("mouseenter", () => updateEndpointHint(meta));
    element.addEventListener("focus", () => updateEndpointHint(meta));
  }
}

async function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const helper = document.createElement("textarea");
  helper.value = text;
  helper.setAttribute("readonly", "readonly");
  helper.style.position = "fixed";
  helper.style.opacity = "0";
  document.body.appendChild(helper);
  helper.select();
  document.execCommand("copy");
  helper.remove();
}

async function copyCurrentEndpointHint() {
  const output = byId("scenarioOutput");
  if (!LAST_ENDPOINT_HINT_TEXT || LAST_ENDPOINT_HINT_TEXT === "No endpoint selected yet.") {
    appendOutputLine(output, "\nSelect an action button first to copy an endpoint hint.");
    return;
  }
  try {
    await copyToClipboard(LAST_ENDPOINT_HINT_TEXT);
    appendOutputLine(output, `\nCopied endpoint hint: ${LAST_ENDPOINT_HINT_TEXT}`);
  } catch (error) {
    appendOutputLine(output, `\nFailed to copy endpoint hint: ${String(error)}`);
  }
}

async function copyEndpointCatalog() {
  const output = byId("scenarioOutput");
  const catalog = Object.entries(ACTION_ENDPOINT_HINTS).map(([id, meta]) => ({
    action: id,
    service: meta.service,
    method: meta.method,
    path: meta.path,
  }));
  try {
    await copyToClipboard(JSON.stringify(catalog, null, 2));
    appendOutputLine(output, `\nCopied endpoint map (${catalog.length} actions).`);
  } catch (error) {
    appendOutputLine(output, `\nFailed to copy endpoint map: ${String(error)}`);
  }
}

function renderHistory() {
  const list = byId("requestHistory");
  const entries = REQUEST_HISTORY.filter(matchesHistoryFilters);
  const summary = byId("historySummary");
  if (summary) {
    summary.textContent = `Showing ${entries.length} of ${REQUEST_HISTORY.length} request(s).`;
  }
  const failedCount = entries.filter((entry) => !entry.ok).length;
  const slowCount = entries.filter((entry) => isSlowEntry(entry)).length;
  const metricVisible = byId("metricVisible");
  const metricFailed = byId("metricFailed");
  const metricSlow = byId("metricSlow");
  if (metricVisible) metricVisible.textContent = String(entries.length);
  if (metricFailed) metricFailed.textContent = String(failedCount);
  if (metricSlow) metricSlow.textContent = String(slowCount);
  if (!entries.length) {
    const emptyMessage = HISTORY_FAIL_ONLY
      ? "No failed requests in the selected filter."
      : "No requests in the selected filter.";
    list.innerHTML = `<li class="history-empty">${emptyMessage}</li>`;
    return;
  }
  list.innerHTML = entries.map((entry) => {
    const stamp = new Date(entry.time).toLocaleTimeString();
    const cssClass = entry.ok ? "ok" : "fail";
    const retryControl =
      !entry.ok && entry.replay
        ? `<button type="button" class="history-retry-btn" data-history-id="${entry.history_id}">Retry</button>`
        : '<span class="history-retry-placeholder">-</span>';
    return `
      <li class="history-entry ${cssClass}">
        <span>${stamp}</span>
        <span class="history-status">${entry.status}</span>
        <span class="history-service">${entry.service_label}</span>
        <span class="history-path">${entry.method} ${entry.path}</span>
        <span>${entry.duration}ms</span>${retryControl}
      </li>
    `;
  }).join("");
}

function matchesHistoryFilters(entry) {
  if (HISTORY_FAIL_ONLY && entry.ok) return false;
  if (HISTORY_SLOW_ONLY && !isSlowEntry(entry)) return false;
  if (!matchesStatusFilter(entry)) return false;
  if (HISTORY_SERVICE_FILTER === "all") return true;
  return entry.service_group === HISTORY_SERVICE_FILTER;
}

function isSlowEntry(entry) {
  const threshold = Number(HISTORY_SLOW_THRESHOLD_MS);
  const duration = Number(entry.duration);
  if (!Number.isFinite(threshold) || threshold < 0) return false;
  if (!Number.isFinite(duration)) return false;
  return duration >= threshold;
}

function matchesStatusFilter(entry) {
  if (HISTORY_STATUS_FILTER === "all") return true;
  if (HISTORY_STATUS_FILTER === "success") return entry.ok;
  if (HISTORY_STATUS_FILTER === "network") return String(entry.status) === "NET";
  if (HISTORY_STATUS_FILTER === "client_error") return isHttpStatusInRange(entry.status, 400, 499);
  if (HISTORY_STATUS_FILTER === "server_error") return isHttpStatusInRange(entry.status, 500, 599);
  return true;
}

function isHttpStatusInRange(statusValue, low, high) {
  const numeric = Number(statusValue);
  if (!Number.isFinite(numeric)) return false;
  return numeric >= low && numeric <= high;
}

function exportHistoryJson() {
  const output = byId("scenarioOutput");
  const payload = {
    exported_at: nowIso(),
    fail_only: HISTORY_FAIL_ONLY,
    service_filter: HISTORY_SERVICE_FILTER,
    count: REQUEST_HISTORY.length,
    entries: REQUEST_HISTORY,
  };
  const suffix = `${HISTORY_SERVICE_FILTER}-${HISTORY_FAIL_ONLY ? "fail-only" : "all"}`;
  const filename = `securevote-request-history-${suffix}-${Date.now()}.json`;
  downloadJson(filename, payload);
  appendOutputLine(output, `\nExported request timeline: ${filename}`);
}

function csvEscape(value) {
  const text = String(value ?? "");
  if (/[",\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function exportHistoryCsv() {
  const output = byId("scenarioOutput");
  if (!REQUEST_HISTORY.length) {
    appendOutputLine(output, "\nNo request history available to export.");
    return;
  }
  const header = ["time", "status", "ok", "service_group", "service_label", "method", "path", "duration_ms"];
  const lines = [header.join(",")];
  for (const entry of REQUEST_HISTORY) {
    lines.push(
      [
        new Date(entry.time).toISOString(),
        entry.status,
        entry.ok,
        entry.service_group,
        entry.service_label,
        entry.method,
        entry.path,
        entry.duration,
      ]
        .map(csvEscape)
        .join(","),
    );
  }
  const suffix = `${HISTORY_SERVICE_FILTER}-${HISTORY_FAIL_ONLY ? "fail-only" : "all"}`;
  const filename = `securevote-request-history-${suffix}-${Date.now()}.csv`;
  downloadText(filename, `${lines.join("\n")}\n`, "text/csv;charset=utf-8");
  appendOutputLine(output, `\nExported request timeline CSV: ${filename}`);
}

async function copyFailedEndpoints() {
  const output = byId("scenarioOutput");
  const failed = REQUEST_HISTORY.filter((entry) => !entry.ok);
  if (!failed.length) {
    appendOutputLine(output, "\nNo failed request endpoints to copy.");
    return;
  }
  const unique = [...new Set(failed.map((entry) => `${entry.method} ${entry.path}`))];
  try {
    await copyToClipboard(unique.join("\n"));
    appendOutputLine(output, `\nCopied ${unique.length} failed endpoint(s).`);
  } catch (error) {
    appendOutputLine(output, `\nFailed to copy failed endpoints: ${String(error)}`);
  }
}

async function copyVisibleEndpoints() {
  const output = byId("scenarioOutput");
  const entries = REQUEST_HISTORY.filter(matchesHistoryFilters);
  if (!entries.length) {
    appendOutputLine(output, "\nNo visible endpoints to copy for the current filters.");
    return;
  }
  const unique = [...new Set(entries.map((entry) => `${entry.method} ${entry.path}`))];
  try {
    await copyToClipboard(unique.join("\n"));
    appendOutputLine(output, `\nCopied ${unique.length} visible endpoint(s).`);
  } catch (error) {
    appendOutputLine(output, `\nFailed to copy visible endpoints: ${String(error)}`);
  }
}

function toggleHistoryFailOnly(event) {
  HISTORY_FAIL_ONLY = Boolean(event.target?.checked);
  renderHistory();
}

function toggleHistoryServiceFilter(event) {
  const raw = String(event.target?.value || "all");
  const allowed = new Set(["all", "gateway", "offline", "mixed"]);
  HISTORY_SERVICE_FILTER = allowed.has(raw) ? raw : "all";
  renderHistory();
}

function toggleHistoryStatusFilter(event) {
  const raw = String(event.target?.value || "all");
  const allowed = new Set(["all", "success", "client_error", "server_error", "network"]);
  HISTORY_STATUS_FILTER = allowed.has(raw) ? raw : "all";
  renderHistory();
}

function toggleHistorySlowOnly(event) {
  HISTORY_SLOW_ONLY = Boolean(event.target?.checked);
  renderHistory();
}

function updateHistorySlowThreshold(event) {
  const numeric = Number(event.target?.value);
  if (Number.isFinite(numeric) && numeric >= 0) {
    HISTORY_SLOW_THRESHOLD_MS = numeric;
  }
  renderHistory();
}

function resetHistory() {
  REQUEST_HISTORY.length = 0;
  renderHistory();
}

async function retryLastFailedRequest() {
  const output = byId("scenarioOutput");
  const failed = REQUEST_HISTORY.find((entry) => !entry.ok && matchesHistoryFilters(entry) && entry.replay);
  if (!failed) {
    appendOutputLine(output, "\nNo failed request with replay data found in the active filter.");
    return;
  }
  await retryHistoryEntry(failed);
}

async function retryHistoryEntry(entry) {
  const output = byId("scenarioOutput");
  const replay = entry.replay;
  appendOutputLine(output, `\nRetrying failed request: ${replay.method} ${replay.path} (${entry.service_label})`);
  try {
    await requestJson(replay.base_url, replay.path, replay.options || {});
    appendOutputLine(output, "Retry result: success.");
  } catch (error) {
    appendOutputLine(output, `Retry result: failed - ${String(error)}`);
  }
}

function findHistoryEntryById(historyId) {
  return REQUEST_HISTORY.find((entry) => String(entry.history_id) === String(historyId)) || null;
}

async function handleHistoryListClick(event) {
  const button = event.target?.closest?.(".history-retry-btn");
  if (!button) return;
  const historyId = button.getAttribute("data-history-id");
  const entry = findHistoryEntryById(historyId);
  if (!entry || entry.ok || !entry.replay) {
    return;
  }
  button.disabled = true;
  try {
    await retryHistoryEntry(entry);
  } finally {
    button.disabled = false;
  }
}

function pushHistory(entry) {
  if (!entry.service_group) {
    entry.service_group = "mixed";
  }
  if (!entry.service_label) {
    entry.service_label = "Mixed/Local";
  }
  entry.history_id = ++HISTORY_ENTRY_SEQ;
  REQUEST_HISTORY.unshift(entry);
  if (REQUEST_HISTORY.length > REQUEST_HISTORY_LIMIT) {
    REQUEST_HISTORY.pop();
  }
  renderHistory();
}

function gatewayBaseUrl() {
  return byId("gatewayBaseUrl").value.trim().replace(/\/$/, "");
}

function offlineSyncBaseUrl() {
  return byId("offlineSyncBaseUrl").value.trim().replace(/\/$/, "");
}

function inferHistoryService(baseUrl, path) {
  const gatewayBase = gatewayBaseUrl();
  const offlineBase = offlineSyncBaseUrl();
  if (baseUrl === gatewayBase) {
    return { service_group: "gateway", service_label: "Gateway" };
  }
  if (baseUrl === offlineBase) {
    return { service_group: "offline", service_label: "Offline Sync" };
  }
  if (path === "/health") {
    return { service_group: "mixed", service_label: "Mixed/Health" };
  }
  return { service_group: "mixed", service_label: "Mixed/Local" };
}

async function requestJson(baseUrl, path, options = {}) {
  const startedAt = Date.now();
  const method = (options.method || "GET").toUpperCase();
  const serviceInfo = inferHistoryService(baseUrl, path);
  const requestHeaders = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const replay = {
    base_url: baseUrl,
    method,
    path,
    options: {
      method,
      headers: requestHeaders,
      ...(options.body !== undefined ? { body: options.body } : {}),
    },
  };
  let response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      headers: requestHeaders,
      ...options,
    });
  } catch (error) {
    pushHistory({
      time: startedAt,
      method,
      path,
      status: "NET",
      ok: false,
      ...serviceInfo,
      replay,
      duration: Date.now() - startedAt,
    });
    throw error;
  }

  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { raw: text };
  }

  if (!response.ok) {
    pushHistory({
      time: startedAt,
      method,
      path,
      status: response.status,
      ok: false,
      ...serviceInfo,
      replay,
      duration: Date.now() - startedAt,
    });
    throw new Error(pretty({ status: response.status, payload }));
  }

  pushHistory({
    time: startedAt,
    method,
    path,
    status: response.status,
    ok: true,
    ...serviceInfo,
    replay,
    duration: Date.now() - startedAt,
  });
  return payload;
}

function withQuery(path, params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && String(value).length > 0) {
      search.set(key, String(value));
    }
  }
  const encoded = search.toString();
  return encoded ? `${path}?${encoded}` : path;
}

function currentVotePayload() {
  return {
    token: byId("verifyToken").value.trim(),
    ballot_id: byId("ballotId").value.trim(),
    election_id: byId("electionId").value.trim(),
    device_id: byId("deviceId").value.trim(),
    selections: {
      president: byId("candidate").value,
    },
  };
}

function currentObserverToken() {
  return byId("observerToken").value.trim();
}

function currentAdminToken() {
  return byId("adminToken").value.trim();
}

function currentOfflineApprovers() {
  return byId("offlineApprovers").value
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

async function verifyHealth() {
  const output = byId("healthOutput");
  try {
    const gatewayHealth = await requestJson(gatewayBaseUrl(), "/health");
    const offlineHealth = await requestJson(offlineSyncBaseUrl(), "/health");
    setOutput(output, { gateway: gatewayHealth, offline_sync: offlineHealth });
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

function nowIso() {
  return new Date().toISOString();
}

function scenarioCaseId() {
  const stamp = Date.now();
  return `case-frontend-scenario-${stamp}`;
}

async function verifyToken() {
  const output = byId("voteOutput");
  try {
    const payload = await requestJson(gatewayBaseUrl(), "/api/v1/vote/verify-token", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${byId("verifyToken").value.trim()}`,
      },
      body: JSON.stringify({ token: byId("verifyToken").value.trim() }),
    });
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function castVote(event) {
  event.preventDefault();
  const output = byId("voteOutput");
  try {
    const votePayload = currentVotePayload();
    const payload = await requestJson(gatewayBaseUrl(), "/api/v1/vote/cast", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${votePayload.token}`,
        "X-Device-ID": votePayload.device_id,
      },
      body: JSON.stringify(votePayload),
    });
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function observerRequest(path, options = {}) {
  return requestJson(gatewayBaseUrl(), path, {
    headers: {
      Authorization: `Bearer ${currentObserverToken()}`,
      ...(options.headers || {}),
    },
    ...options,
  });
}

async function adminOfflineRequest(path, options = {}) {
  return requestJson(offlineSyncBaseUrl(), path, {
    headers: {
      Authorization: `Bearer ${currentAdminToken()}`,
      ...(options.headers || {}),
    },
    ...options,
  });
}

async function loadAudit() {
  const output = byId("observerOutput");
  try {
    setOutput(output, await observerRequest("/api/v1/vote/observer/audit"));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function loadTally() {
  const output = byId("observerOutput");
  try {
    const electionId = byId("observerElectionId").value.trim();
    setOutput(output, await observerRequest(`/api/v1/vote/observer/tally/${electionId}`));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function loadCompliance() {
  const output = byId("observerOutput");
  try {
    setOutput(output, await observerRequest("/api/v1/vote/compliance/report"));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function loadEvidence() {
  const output = byId("observerOutput");
  try {
    const payload = await observerRequest(
      withQuery("/api/v1/vote/compliance/offline-sync-evidence", {
        case_id: byId("evidenceCaseId").value.trim(),
      }),
    );
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

function currentOfflineRecord() {
  return {
    token_hash: byId("offlineTokenHash").value.trim(),
    created_at: byId("offlineCreatedAt").value.trim(),
  };
}

async function stageOffline() {
  const output = byId("offlineOutput");
  try {
    const payload = await adminOfflineRequest("/api/v1/offline-sync/stage", {
      method: "POST",
      body: JSON.stringify({ record: currentOfflineRecord() }),
    });
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function queueOffline() {
  const output = byId("offlineOutput");
  try {
    setOutput(output, await adminOfflineRequest("/api/v1/offline-sync/queue"));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function flushOffline() {
  const output = byId("offlineOutput");
  try {
    const record = currentOfflineRecord();
    const payload = await adminOfflineRequest("/api/v1/offline-sync/flush", {
      method: "POST",
      body: JSON.stringify({
        device_id: byId("offlineDeviceId").value.trim(),
        remote_records: [
          {
            token_hash: record.token_hash,
            created_at: "2026-04-08T00:01:00Z",
          },
        ],
        approvers: currentOfflineApprovers(),
      }),
    });
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function operationsOffline() {
  const output = byId("offlineOutput");
  try {
    setOutput(output, await adminOfflineRequest("/api/v1/offline-sync/operations"));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function statusOffline() {
  const output = byId("offlineOutput");
  try {
    setOutput(output, await adminOfflineRequest("/api/v1/offline-sync/status"));
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function exportOffline() {
  const output = byId("offlineOutput");
  try {
    setOutput(
      output,
      await adminOfflineRequest(
        withQuery("/api/v1/offline-sync/operations/export", {
          device_id: byId("offlineDeviceId").value.trim(),
        }),
      ),
    );
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

async function bundleOffline() {
  const output = byId("offlineOutput");
  try {
    const payload = await adminOfflineRequest(
      withQuery("/api/v1/offline-sync/operations/evidence-bundle", {
        case_id: byId("offlineCaseId").value.trim(),
        device_id: byId("offlineDeviceId").value.trim(),
      }),
    );
    setOutput(output, payload);
  } catch (error) {
    setOutput(output, String(error), true);
  }
}

function fillPreset(kind) {
  if (kind === "voter") {
    byId("verifyToken").value = "demo-voter-ui";
    byId("deviceId").value = "device-1";
  }
  if (kind === "observer") {
    byId("observerToken").value = "observer-auditor-ui";
  }
  if (kind === "admin") {
    byId("adminToken").value = "admin-operator-ui";
  }
}

async function runDemoScenario() {
  const button = byId("runScenarioButton");
  const output = byId("scenarioOutput");
  const runId = Date.now();
  const token = byId("verifyToken").value.trim();
  const electionId = byId("electionId").value.trim();
  const deviceId = byId("offlineDeviceId").value.trim() || "device-1";
  const tokenHash = `scenario-${runId}-token`;
  const caseId = scenarioCaseId();
  const createdAt = nowIso();
  const profile = byId("scenarioProfile").value;

  button.disabled = true;
  setOutput(output, `Scenario ${runId} started at ${createdAt}\nProfile: ${profile}`);

  try {
    appendOutputLine(output, "1. Checking runtime health...");
    const gatewayHealth = await requestJson(gatewayBaseUrl(), "/health");
    const offlineHealth = await requestJson(offlineSyncBaseUrl(), "/health");
    appendOutputLine(output, `   gateway=${gatewayHealth.status}, offline_sync=${offlineHealth.status}`);

    appendOutputLine(output, "2. Verifying voter token...");
    await requestJson(gatewayBaseUrl(), "/api/v1/vote/verify-token", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ token }),
    });
    appendOutputLine(output, "   token verification passed");

    appendOutputLine(output, "3. Casting vote...");
    const castPayload = await requestJson(gatewayBaseUrl(), "/api/v1/vote/cast", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "X-Device-ID": byId("deviceId").value.trim() || "device-1",
      },
      body: JSON.stringify(currentVotePayload()),
    });
    appendOutputLine(output, `   vote accepted with token_hash=${castPayload.vote.token_hash}`);

    appendOutputLine(output, "4. Staging offline sync record...");
    await adminOfflineRequest("/api/v1/offline-sync/stage", {
      method: "POST",
      body: JSON.stringify({ record: { token_hash: tokenHash, created_at: createdAt } }),
    });
    appendOutputLine(output, `   staged record token_hash=${tokenHash}`);

    appendOutputLine(output, "5. Flushing offline sync queue...");
    const flushPayload = await adminOfflineRequest("/api/v1/offline-sync/flush", {
      method: "POST",
      body: JSON.stringify({
        device_id: deviceId,
        remote_records: [{ token_hash: tokenHash, created_at: new Date(Date.now() + 1000).toISOString() }],
        approvers: currentOfflineApprovers(),
      }),
    });
    appendOutputLine(output, `   manifest_valid=${flushPayload.manifest_valid}`);

    let compliance = null;
    let evidence = null;
    if (profile === "full") {
      appendOutputLine(output, "6. Loading compliance report...");
      compliance = await observerRequest("/api/v1/vote/compliance/report");
      appendOutputLine(
        output,
        `   hash_chain_valid=${compliance.report.hash_chain_valid}, latest_event=${compliance.report.latest_event}`,
      );

      appendOutputLine(output, "7. Generating compliance evidence bundle...");
      evidence = await observerRequest(
        withQuery("/api/v1/vote/compliance/offline-sync-evidence", {
          case_id: caseId,
          device_id: deviceId,
        }),
      );
      appendOutputLine(output, `   evidence_case_id=${evidence.bundle.case_id}`);
    } else {
      appendOutputLine(output, "6. Smoke profile selected: compliance/evidence steps skipped.");
    }

    setOutput(
      output,
      `${output.textContent}\n\nScenario complete.\n${pretty({
        scenario_id: runId,
        profile,
        election_id: electionId,
        token,
        token_hash: castPayload.vote.token_hash,
        offline_token_hash: tokenHash,
        evidence_case_id: evidence ? caseId : null,
        compliance_checked: Boolean(compliance),
        completed_at: nowIso(),
      })}`,
    );
    LAST_SCENARIO_REPORT = {
      scenario_id: runId,
      profile,
      election_id: electionId,
      token,
      token_hash: castPayload.vote.token_hash,
      offline_token_hash: tokenHash,
      evidence_case_id: evidence ? caseId : null,
      compliance_checked: Boolean(compliance),
      completed_at: nowIso(),
      health: { gateway: "ok", offline_sync: "ok" },
    };
  } catch (error) {
    appendOutputLine(output, `ERROR: ${String(error)}`);
    output.classList.add("error");
    LAST_SCENARIO_REPORT = {
      scenario_id: runId,
      profile,
      failed: true,
      error: String(error),
      failed_at: nowIso(),
    };
  } finally {
    button.disabled = false;
  }
}

function exportScenarioReport() {
  const output = byId("scenarioOutput");
  if (!LAST_SCENARIO_REPORT) {
    setOutput(output, "No scenario report available yet. Run a scenario first.", true);
    return;
  }
  const scenarioId = LAST_SCENARIO_REPORT.scenario_id || "unknown";
  const filename = `securevote-scenario-${scenarioId}.json`;
  downloadJson(filename, LAST_SCENARIO_REPORT);
  appendOutputLine(output, `\nReport exported: ${filename}`);
}

function renderScenarioBaseline() {
  const baselineOutput = byId("scenarioBaseline");
  if (!IMPORTED_SCENARIO_REPORT) {
    setOutput(baselineOutput, "No imported scenario baseline loaded.");
    return;
  }
  setOutput(
    baselineOutput,
    {
      imported: true,
      scenario_id: IMPORTED_SCENARIO_REPORT.scenario_id || null,
      profile: IMPORTED_SCENARIO_REPORT.profile || null,
      election_id: IMPORTED_SCENARIO_REPORT.election_id || null,
      token: IMPORTED_SCENARIO_REPORT.token || null,
      token_hash: IMPORTED_SCENARIO_REPORT.token_hash || null,
      evidence_case_id: IMPORTED_SCENARIO_REPORT.evidence_case_id || null,
      completed_at: IMPORTED_SCENARIO_REPORT.completed_at || null,
      failed: Boolean(IMPORTED_SCENARIO_REPORT.failed),
    },
  );
}

function comparableScenarioSummary(report) {
  if (!report) return null;
  return {
    profile: report.profile ?? null,
    election_id: report.election_id ?? null,
    token: report.token ?? null,
    token_hash: report.token_hash ?? null,
    offline_token_hash: report.offline_token_hash ?? null,
    evidence_case_id: report.evidence_case_id ?? null,
    compliance_checked: Boolean(report.compliance_checked),
    failed: Boolean(report.failed),
  };
}

function renderScenarioDiff(baseline, replay) {
  const rows = byId("scenarioDiffRows");
  if (!baseline || !replay) {
    LAST_SCENARIO_DIFF_ROWS = [];
    setDiffBadge("No Data", "neutral");
    rows.innerHTML = '<div class="scenario-diff-empty">Run a replay to compare results.</div>';
    return;
  }
  const baselineSummary = comparableScenarioSummary(baseline);
  const replaySummary = comparableScenarioSummary(replay);
  const fields = [
    ["profile", "Profile"],
    ["election_id", "Election ID"],
    ["token", "Token"],
    ["token_hash", "Token Hash"],
    ["offline_token_hash", "Offline Token Hash"],
    ["evidence_case_id", "Evidence Case ID"],
    ["compliance_checked", "Compliance Checked"],
    ["failed", "Failed"],
  ];
  LAST_SCENARIO_DIFF_ROWS = fields.map(([field, label]) => {
    const baselineValue = baselineSummary[field];
    const replayValue = replaySummary[field];
    return {
      field,
      label,
      baseline: baselineValue,
      replay: replayValue,
      match: String(baselineValue) === String(replayValue),
    };
  });
  const mismatchCount = LAST_SCENARIO_DIFF_ROWS.filter((row) => !row.match).length;
  if (mismatchCount === 0) {
    setDiffBadge("Clean", "clean");
  } else {
    setDiffBadge(`${mismatchCount} Diff`, "alert");
  }
  rows.innerHTML = fields
    .map(([field, label]) => {
      const left = baselineSummary[field];
      const right = replaySummary[field];
      const match = String(left) === String(right);
      return `
        <div class="scenario-diff-cell">${label}</div>
        <div class="scenario-diff-cell">${left === null ? "-" : String(left)}</div>
        <div class="scenario-diff-cell">${right === null ? "-" : String(right)}</div>
        <div class="scenario-diff-cell status ${match ? "match" : "diff"}">${match ? "Match" : "Diff"}</div>
      `;
    })
    .join("");
}

async function copyDiffSummary() {
  const output = byId("scenarioOutput");
  if (!LAST_SCENARIO_DIFF_ROWS.length) {
    appendOutputLine(output, "\nNo diff data available yet. Replay an imported scenario first.");
    return;
  }
  const summary = buildDiffSummary();
  if (!summary) {
    appendOutputLine(output, "\nNo diff data available yet. Replay an imported scenario first.");
    return;
  }
  if (!summary.mismatches.length) {
    appendOutputLine(output, "\nDiff summary: no mismatches.");
    return;
  }
  const text = JSON.stringify(summary, null, 2);
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const helper = document.createElement("textarea");
      helper.value = text;
      helper.setAttribute("readonly", "readonly");
      helper.style.position = "fixed";
      helper.style.opacity = "0";
      document.body.appendChild(helper);
      helper.select();
      document.execCommand("copy");
      helper.remove();
    }
    appendOutputLine(output, `\nCopied diff summary with ${summary.mismatch_count} mismatch(es) to clipboard.`);
  } catch (error) {
    appendOutputLine(output, `\nFailed to copy diff summary: ${String(error)}`);
  }
}

function buildDiffSummary() {
  if (!LAST_SCENARIO_DIFF_ROWS.length) {
    return null;
  }
  const mismatches = LAST_SCENARIO_DIFF_ROWS.filter((row) => !row.match);
  return {
    generated_at: nowIso(),
    mismatch_count: mismatches.length,
    mismatches: mismatches.map((row) => ({
      field: row.field,
      label: row.label,
      baseline: row.baseline,
      replay: row.replay,
    })),
  };
}

function downloadDiffSummary() {
  const output = byId("scenarioOutput");
  const summary = buildDiffSummary();
  if (!summary) {
    appendOutputLine(output, "\nNo diff data available yet. Replay an imported scenario first.");
    return;
  }
  if (!summary.mismatches.length) {
    appendOutputLine(output, "\nDiff summary has no mismatches. Nothing downloaded.");
    setDiffBadge("Clean", "clean");
    return;
  }
  const filename = `securevote-diff-${Date.now()}.json`;
  downloadJson(filename, summary);
  appendOutputLine(output, `\nDownloaded diff summary: ${filename}`);
}

function applyScenarioBaselineToForm() {
  if (!IMPORTED_SCENARIO_REPORT) return;
  const profile = normalizeScenarioProfile(IMPORTED_SCENARIO_REPORT.profile);
  byId("scenarioProfile").value = profile;
  if (IMPORTED_SCENARIO_REPORT.token) {
    byId("verifyToken").value = IMPORTED_SCENARIO_REPORT.token;
  }
  if (IMPORTED_SCENARIO_REPORT.election_id) {
    byId("electionId").value = IMPORTED_SCENARIO_REPORT.election_id;
    byId("observerElectionId").value = IMPORTED_SCENARIO_REPORT.election_id;
  }
  if (IMPORTED_SCENARIO_REPORT.evidence_case_id) {
    byId("evidenceCaseId").value = IMPORTED_SCENARIO_REPORT.evidence_case_id;
    byId("offlineCaseId").value = IMPORTED_SCENARIO_REPORT.evidence_case_id;
  }
  for (const id of PERSISTED_FIELDS) {
    saveField(id);
  }
}

async function importScenarioFile(event) {
  const output = byId("scenarioOutput");
  const file = event.target.files && event.target.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== "object") {
      throw new Error("Imported file must contain a JSON object.");
    }
    IMPORTED_SCENARIO_REPORT = parsed;
    renderScenarioBaseline();
    applyScenarioBaselineToForm();
    appendOutputLine(output, `\nImported scenario baseline from ${file.name}.`);
  } catch (error) {
    IMPORTED_SCENARIO_REPORT = null;
    renderScenarioBaseline();
    setOutput(output, `Failed to import scenario file: ${String(error)}`, true);
  } finally {
    event.target.value = "";
  }
}

async function replayImportedScenario() {
  const output = byId("scenarioOutput");
  if (!IMPORTED_SCENARIO_REPORT) {
    setOutput(output, "No imported scenario baseline available. Import a JSON report first.", true);
    return;
  }
  applyScenarioBaselineToForm();
  appendOutputLine(output, "\nReplaying imported scenario baseline...");
  const previousScenarioId = IMPORTED_SCENARIO_REPORT.scenario_id || null;
  const previousTokenHash = IMPORTED_SCENARIO_REPORT.token_hash || null;
  const previousEvidenceCase = IMPORTED_SCENARIO_REPORT.evidence_case_id || null;
  await runDemoScenario();
  if (LAST_SCENARIO_REPORT) {
    renderScenarioDiff(IMPORTED_SCENARIO_REPORT, LAST_SCENARIO_REPORT);
    appendOutputLine(
      output,
      `Replay summary: previous=${previousScenarioId}, current=${LAST_SCENARIO_REPORT.scenario_id}, token_hash_match=${
        previousTokenHash === LAST_SCENARIO_REPORT.token_hash
      }, evidence_case_match=${previousEvidenceCase === LAST_SCENARIO_REPORT.evidence_case_id}`,
    );
  }
}

function activateTab(name) {
  for (const tab of document.querySelectorAll(".tab")) {
    tab.classList.toggle("is-active", tab.dataset.tab === name);
  }
  for (const section of document.querySelectorAll("[data-section]")) {
    section.classList.toggle("hidden", section.dataset.section !== name);
  }
}

function saveField(id) {
  const element = byId(id);
  if (!element) return;
  localStorage.setItem(`securevote-ui:${id}`, element.value);
}

function loadPersistedFields() {
  for (const id of PERSISTED_FIELDS) {
    const element = byId(id);
    if (!element) continue;
    const stored = localStorage.getItem(`securevote-ui:${id}`);
    if (stored !== null) {
      element.value = stored;
    }
  }
}

function wirePersistence() {
  for (const id of PERSISTED_FIELDS) {
    const element = byId(id);
    if (!element) continue;
    element.addEventListener("input", () => saveField(id));
    element.addEventListener("change", () => saveField(id));
  }
}

byId("healthCheckButton").addEventListener("click", verifyHealth);
byId("verifyTokenButton").addEventListener("click", verifyToken);
byId("voteForm").addEventListener("submit", castVote);
byId("auditButton").addEventListener("click", loadAudit);
byId("tallyButton").addEventListener("click", loadTally);
byId("complianceButton").addEventListener("click", loadCompliance);
byId("evidenceButton").addEventListener("click", loadEvidence);
byId("stageOfflineButton").addEventListener("click", stageOffline);
byId("queueOfflineButton").addEventListener("click", queueOffline);
byId("flushOfflineButton").addEventListener("click", flushOffline);
byId("operationsOfflineButton").addEventListener("click", operationsOffline);
byId("statusOfflineButton").addEventListener("click", statusOffline);
byId("exportOfflineButton").addEventListener("click", exportOffline);
byId("bundleOfflineButton").addEventListener("click", bundleOffline);
byId("runScenarioButton").addEventListener("click", runDemoScenario);
byId("exportScenarioButton").addEventListener("click", exportScenarioReport);
byId("replayScenarioButton").addEventListener("click", replayImportedScenario);
byId("copyDiffButton").addEventListener("click", copyDiffSummary);
byId("downloadDiffButton").addEventListener("click", downloadDiffSummary);
byId("copyEndpointHintButton").addEventListener("click", copyCurrentEndpointHint);
byId("copyEndpointCatalogButton").addEventListener("click", copyEndpointCatalog);
byId("diffBadge").addEventListener("click", focusDiffPanel);
byId("importScenarioFile").addEventListener("change", importScenarioFile);
byId("openHelpButton").addEventListener("click", openHelpModal);
byId("closeHelpButton").addEventListener("click", closeHelpModal);
byId("helpModal").addEventListener("click", handleModalBackdropClick);
document.addEventListener("keydown", handleGlobalShortcut);
document.addEventListener("keydown", handleModalKeydown);
byId("clearHistoryButton").addEventListener("click", resetHistory);
byId("retryLastFailedButton").addEventListener("click", retryLastFailedRequest);
byId("exportHistoryButton").addEventListener("click", exportHistoryJson);
byId("exportHistoryCsvButton").addEventListener("click", exportHistoryCsv);
byId("copyFailedEndpointsButton").addEventListener("click", copyFailedEndpoints);
byId("copyVisibleEndpointsButton").addEventListener("click", copyVisibleEndpoints);
byId("historyFailOnly").addEventListener("change", toggleHistoryFailOnly);
byId("historyServiceFilter").addEventListener("change", toggleHistoryServiceFilter);
byId("historyStatusFilter").addEventListener("change", toggleHistoryStatusFilter);
byId("historySlowOnly").addEventListener("change", toggleHistorySlowOnly);
byId("historyLatencyMs").addEventListener("input", updateHistorySlowThreshold);
byId("requestHistory").addEventListener("click", handleHistoryListClick);

for (const button of document.querySelectorAll("[data-fill]")) {
  button.addEventListener("click", () => fillPreset(button.dataset.fill));
}

for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
}

loadPersistedFields();
wirePersistence();
applyActionEndpointHintsV2();
setEndpointHintText(LAST_ENDPOINT_HINT_TEXT);
byId("historyServiceFilter").value = HISTORY_SERVICE_FILTER;
byId("historyStatusFilter").value = HISTORY_STATUS_FILTER;
byId("historySlowOnly").checked = HISTORY_SLOW_ONLY;
byId("historyLatencyMs").value = String(HISTORY_SLOW_THRESHOLD_MS);
activateTab("voter");
renderHistory();
renderScenarioBaseline();
renderScenarioDiff(null, null);
verifyHealth();
