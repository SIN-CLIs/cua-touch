# brain.md — Systemwissen cua-touch

## cua-driver ≠ cua-touch

`cua-driver` = Binary in `/Applications/CuaDriver.app` (existierendes Produkt).
`cua-touch` = Dieses Repo. Dokumentation, Python-Wrapper, MCP-Server.

Beide nutzen dieselbe AX-Accessibility-Architektur.

## AKTIVER CODE

- `/Applications/CuaDriver.app/Contents/MacOS/cua-driver` — Binary (v0.0.13)
- `runner/live_omni_monitor.py` in stealth-runner — cua-driver Integration
- `cli/heypiggy-login` in stealth-runner — Google OAuth Flow mit cua-driver

## Tool-Rollen-Trennung (KRITISCH!)

**cua-touch cached NUR Popups** (window_id targetiert).
**skylight-cli cached NUR das Hauptfenster** (PID targetiert).

NIEMALS mischen! skylight-cli list-elements im OAuth-Popup → leere Liste oder falsche Indices.

## AX-State Caching

cua-touch cached AX-State pro `window_id`. Das bedeutet:
- Erster `get_window_state` Call: teuer (~500ms)
- Folgende Calls: billig (aus Cache)
- Neuer Klick auf anderes Popup: neuer `window_id` → neuer Cache-Eintrag

**Regel**: Immer `list_windows` → `get_window_state` → `click/type` in dieser Reihenfolge.

## Window-ID Lifecycle

```
Hauptfenster öffnet Popup
  → list_windows zeigt window_id=W1, pid=<CHROME_PID>
  → get_window_state cached AX-Tree für W1
  → clicks/set_values nutzen cached state

Popup geschlossen
  → list_windows zeigt window_id nicht mehr
  → neuer OAuth-Request → neuer window_id (z.B. W2)

Hauptfenster Tab-Wechsel
  → Gleiche PID, gleiche window_id
  → AX-Tree kann sich ändern → get_window_state refresh
```

## Daemon-Modus (serve &)

cua-touch Daemon MUSS laufen vor allen Popup-Operationen:
```bash
cua-touch serve &
# Warte 2s bis ready
sleep 2
cua-touch call list_windows '{}'
```

Ohne Daemon: "No cached AX state" → alle Operationen schlagen fehl.

## Google OAuth Flow (verifiziert mit PID 31710)

1. skylight: Google-Login-Button klicken (Hauptfenster, element_index 33)
2. cua-touch: Popup window_id finden (list_windows, title enthält "anmelden")
3. cua-touch: Email eintippen (element_index 25, set_value)
4. cua-touch: "Weiter" (element_index 35, click, action=press)
5. cua-touch: "Fortfahren" Consent (element_index 65, click)
6. cua-touch: Finales "Weiter" (element_index 41) → Dashboard

Bei bestehenden Google-Cookies: **KEIN Passwort nötig!**

## Semgrep (in stealth-runner)

11 Regeln blockieren BANNED Patterns. cua-touch ist NICHT BANNED — es ist das einzige
legitime Popup-Tool. Aber: cua-touch in Hauptfenster = Anti-Pattern.