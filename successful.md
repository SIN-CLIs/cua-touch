# successful.md — Was funktioniert (2026-05-02)

## ✅ Google OAuth Login (PID 31710 verifiziert)

Komplett funktionierender Flow:
1. skylight: Google-Login-Button (element_index 33)
2. cua-touch: Popup window_id finden
3. cua-touch: Email eintippen (element_index 25)
4. cua-touch: "Weiter" (element_index 35)
5. cua-touch: "Fortfahren" Consent (element_index 65)
6. cua-touch: Finales "Weiter" (element_index 41) → Dashboard

**0 Passwort nötig** — bestehende Google-Cookies.

## ✅ AX-Accessibility Caching

Erster `get_window_state` Call: ~500ms (teuer).
Folgende Calls: <10ms (aus Cache).
Perfekt für Multi-Step-Popup-Flows.

## ✅ Flow-Optimizer Promotion

10x consecutive success → production artifact.
cua-touch steps werden als fixed JSON gespeichert.
Ab dann: `python3 -m runner.flow_optimizer run <flow> $PID`
→ Kein Vision, kein Screenshot, nur noch CLI calls.

## ✅ MCP Server Mode

JSON-RPC 2.0 über stdio oder HTTP.
Jede Sprache kann cua-touch bedienen: Python, Go, TypeScript, etc.
Perfekt für Integration in stealth-runner, unmask-cli, playstealth-cli.

## ✅ Popup-Detection

`list_windows` filtert nach PID → findet alle Popups eines Chrome-Prozesses.
Titel-basiertes Filtern (case-insensitive): "anmelden", "sign", "google", "consent".

## ✅ Element-Index Stabilität

AX-Role + AX-Label Kombination ist stabiler als CSS-Selector oder XPath.
Bei gleichen Popup-Layouts: gleiche Indices.

## ✅ Window-ID Lifecycle

Jedes Popup bekommt eigene window_id.
 Nach Close: ID invalid.
Nach neuem OAuth: neue ID.
Cleares Lifecycle, kein Cache-Mixup möglich.