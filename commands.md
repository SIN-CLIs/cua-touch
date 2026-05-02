# commands.md — cua-touch CLI-Befehle

## Daemon starten (einmalig pro Session)

```bash
# Background daemon
cua-touch serve &

# Oder mit HTTP (Port 8765)
cua-touch serve --http --port 8765

# Oder MCP stdio mode (für Python/Go/any language)
cua-touch mcp
```

## Alle Fenster auflisten (inkl. Popups)

```bash
cua-touch call list_windows '{}'
# → {"windows": [{"window_id": "W1", "pid": 12345, "title": "Google"}, ...]}
```

## Popup-State laden (cached pro window_id!)

```bash
cua-touch call get_window_state '{"pid":12345,"window_id":"W1"}'
# → {"elements": [{"element_index": 0, "role": "AXTextField", "label": "Email"}, ...]}
```

## Im Popup klicken

```bash
cua-touch call click '{"pid":12345,"window_id":"W1","element_index":25,"action":"press"}'
# action: "press" | "pressAndHold" | "doubleClick"
```

## Im Popup Text eintippen

```bash
cua-touch call set_value '{"pid":12345,"window_id":"W1","element_index":25,"value":"email@gmail.com"}'
```

## Taste drücken

```bash
cua-touch call press_key '{"pid":12345,"window_id":"W1","element_index":0,"key":"Return"}'
# key: Return, Tab, Escape, ArrowDown, etc.
```

## MCP Server (JSON-RPC 2.0)

```bash
# stdio mode
cua-touch mcp

# HTTP mode
cua-touch serve --http --port 8765
```

Python Client:
```python
import subprocess, json

def cua_call(method: str, params: dict) -> dict:
    result = subprocess.run(
        ["cua-touch", "call", method, json.dumps(params)],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

windows = cua_call("list_windows", {})
wid = windows["windows"][0]["window_id"]

cua_call("set_value", {
    "pid": 12345, "window_id": wid,
    "element_index": 25, "value": "email@gmail.com"
})

cua_call("click", {
    "pid": 12345, "window_id": wid,
    "element_index": 35, "action": "press"
})
```

## Kompletter Google OAuth Flow

```bash
PID=$(pgrep -f "Google Chrome.app/Contents/MacOS/Google Chrome$" | head -1)

# 1. Daemon
cua-touch serve &

# 2. Google-Login-Button (Hauptfenster → skylight!)
skylight-cli click --pid $PID --element-index 33
sleep 2

# 3. Popup WID finden
WID=$(cua-touch call list_windows '{}' | python3 -c "
import sys,json
for w in json.load(sys.stdin).get('windows',[]):
    if w.get('pid')==$PID:
        t=(w.get('title','')).lower()
        if 'anmelden' in t or 'sign' in t:
            print(w['window_id'])
")

# 4. Email
cua-touch call set_value "{\"pid\":$PID,\"window_id\":\"$WID\",\"element_index\":25,\"value\":\"email@gmail.com\"}"

# 5. Weiter
cua-touch call click "{\"pid\":$PID,\"window_id\":\"$WID\",\"element_index\":35,\"action\":\"press\"}"
sleep 2

# 6. Consent
cua-touch call click "{\"pid\":$PID,\"window_id\":\"$WID\",\"element_index\":65,\"action\":\"press\"}"
sleep 2

# 7. Finales Weiter → Dashboard
cua-touch call click "{\"pid\":$PID,\"window_id\":\"$WID\",\"element_index\":41,\"action\":\"press\"}"
```

## Flow-Optimizer Integration (stealth-runner)

```bash
# Production flow — CLI-only, kein Vision
python3 -m runner.flow_optimizer run heypiggy-google-login 31710

# Flow Status
python3 -m runner.flow_optimizer status heypiggy-google-login

# Nach erfolgreichem Run (CLI-only):
python3 -m runner.flow_optimizer track heypiggy-google-login true 4500 --steps 7/7
```

Flow-Optimizer tracked cua-touch calls automatisch. Nach 10x consecutive success →
cua-touch-steps werden als fixed artifact gespeichert. Kein Vision mehr nötig.