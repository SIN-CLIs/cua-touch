---
content: |
# cua-touch - macOS Accessibility-driven Computer-Use Agent

> **AX-tree snapshot, element click/type by index, window_id targeting for popup automation.**
> Python CLI + MCP stdio server. The Popup-Action-Layer der Stealth Suite.

---

##  Was ist cua-touch?

```
cua-driver call list_windows '{}'
cua-driver call get_window_state '{"pid":12345,"window_id":W1}'
cua-driver call click '{"pid":12345,"window_id":W1,"element_index":25,"action":"press"}'
cua-driver call set_value '{"pid":12345,"window_id":W1,"element_index":25,"value":"email@gmail.com"}'
```

**Das einzige Tool das Popups bedienen kann.** skylight-cli cached NUR das Hauptfenster.
cua-touch targetiert Popup-Fenster via `window_id` - keine Koordinaten, keine Maus.

---

##  Stealth Suite - Tool-Rollen

| Tool | Kontext | Command |
|------|---------|---------|
| **playstealth** | Chrome starten | `playstealth launch --url ...` |
| **skylight-cli** | **Hauptfenster** | `skylight-cli click --pid X --element-index Y` |
| **cua-touch** | **Popups** | `cua-touch call click '{"window_id":W,...}'` |
| **screen-follow** | Video aufnehmen | `screen-follow record --video` |

**Regel**: skylight-cli in Popups → **FAILS**. cua-touch im Hauptfenster → **INEFFIZIENT**.
Immer das richtige Tool für den richtigen Kontext. Siehe `docs/TOOL-ROLES.md`.

---

##  Quick Start

```bash
# Daemon starten (einmalig pro Session)
cua-touch serve &

# Alle Fenster auflisten (inkl. Popups)
cua-touch call list_windows '{}'

# Popup-State laden (cached pro window_id!)
cua-touch call get_window_state '{"pid":12345,"window_id":W1}'

# Im Popup klicken
cua-touch call click '{"pid":12345,"window_id":W1,"element_index":25,"action":"press"}'

# Im Popup Text eintippen
cua-touch call set_value '{"pid":12345,"window_id":W1,"element_index":25,"value":"text"}'
```

---

##  Google OAuth Flow (cua-touch only!)

```bash
PID=$(pgrep -f "Google Chrome.app/Contents/MacOS/Google Chrome$" | head -1)

# Daemon
cua-touch serve &

# Google-Login-Button (Hauptfenster → skylight!)
skylight-cli click --pid $PID --element-index 33
sleep 2

# Popup window_id finden
WID=$(cua-touch call list_windows '{}' | python3 -c "
import sys,json
for w in json.load(sys.stdin).get('windows',[]):
    if w.get('pid')==$PID:
        t=(w.get('title','')).lower()
        if 'anmelden' in t or 'sign' in t or 'google' in t:
            print(w['window_id'])
")

# Email eintippen
cua-touch call set_value "{\"pid\":$PID,\"window_id\":$WID,\"element_index\":25,\"value\":\"email@gmail.com\"}"

# Weiter klicken
cua-touch call click "{\"pid\":$PID,\"window_id\":$WID,\"element_index\":35,\"action\":\"press\"}"
sleep 2

# Fortfahren (Consent)
cua-touch call click "{\"pid\":$PID,\"window_id\":$WID,\"element_index\":65,\"action\":\"press\"}"
sleep 2

# Finales Weiter → Dashboard
cua-touch call click "{\"pid\":$PID,\"window_id\":$WID,\"element_index\":41,\"action\":\"press\"}"
```

**Verifiziert**: PID 31710, 0 Passwort nötig (bestehende Google-Cookies).

---

## ️ MCP Server Mode

```bash
# MCP stdio server (für Python/Go/any language)
cua-touch mcp

# Oder HTTP server
cua-touch serve --http --port 8765
```

JSON-RPC 2.0 interface. Methods: `list_windows`, `get_window_state`, `click`, `set_value`, `press_key`.

---

##  BANNED Patterns

-  `skylight-cli` in Popup-Kontext
-  Koordinaten raten (`--x --y`)
-  Ohne Daemon (`cua-touch serve &`) Popup-Operationen
-  Element-Index aus skylight-cli für Popup nutzen

---

##  Related

- [stealth-runner](https://github.com/SIN-CLIs/stealth-runner) - Orchestrator
- [skylight-cli](https://github.com/SIN-CLIs/skylight-cli) - Hauptfenster ACT layer
- [playstealth-cli](https://github.com/SIN-CLIs/playstealth-cli) - Browser HIDE layer
- [docs/TOOL-ROLES.md](docs/TOOL-ROLES.md) - Complete tool-role separation