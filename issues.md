# issues.md — cua-touch Issues

## Erledigte Issues

- [x] Python-Wrapper für cua-touch erstellen (cua_touch.py Client) — `runner/cua_touch.py` mit `CUATouchClient`, `wait_for_element`, `auto_detect_popup`
- [x] Error-Handling verbessern (Retry-Logic bei "No cached AX state") — `wait_for_element()` mit 3s polling (6 retries × 0.5s)
- [x] window_id Auto-Detection für Consent-Dialoge — `auto_detect_popup()` mit keyword + size heuristics

## Offene Issues

- [ ] MCP Server als standalone Python-Prozess (statt abhängig von CuaDriver.app binary)
- [ ] Flow-Optimizer: heypiggy-google-login → Promotion (braucht 9 weitere runs)
- [ ] docs/TOOL-ROLES.md in stealth-runner verlinken

## SOTA Status

- AGENTS.md ✅
- brain.md ✅
- commands.md ✅
- learn.md ✅
- anti-learn.md ✅
- successful.md ✅
- banned.md ✅
- fix.md ✅

Keine weiteren Docs nötig. Focus auf Code-Integration.

## Verwandte Repos

- [stealth-runner](https://github.com/SIN-CLIs/stealth-runner) — Orchestrator, flow-optimizer
- [skylight-cli](https://github.com/SIN-CLIs/skylight-cli) — Hauptfenster ACT layer