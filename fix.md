# fix.md — Bekannte Bugs & Fixes

## 🔧 Fix: "No cached AX state"

**Problem**: `cua-touch call click ...` schlägt fehl mit "No cached AX state".
**Ursache**: Daemon läuft nicht oder `get_window_state` wurde nicht aufgerufen.
**Fix**:
```bash
cua-touch serve &    # Daemon starten
sleep 2              # Warten bis ready
cua-touch call get_window_state '{"pid":12345,"window_id":"W1"}'
# → erst dann click
```

## 🔧 Fix: Window not found

**Problem**: "Window not found" bei click call.
**Ursache**: Popup wurde geschlossen oder window_id ist invalide.
**Fix**:
```bash
# Neue window_id holen
cua-touch call list_windows '{}' | python3 -c "
import sys,json
for w in json.load(sys.stdin).get('windows',[]):
    if w.get('pid')==12345 and w.get('window_id')!='0':
        print(w['window_id'])
"
```

## 🔧 Fix: Element Index Invalid

**Problem**: Klick trifft falsches Element.
**Ursache**: Google-Layout hat sich geändert, alte Indices sind invalide.
**Fix**:
```bash
# State neu laden, indices verifizieren
cua-touch call get_window_state '{"pid":12345,"window_id":"W1"}' | python3 -c "
import sys,json
for e in json.load(sys.stdin).get('elements',[]):
    if e.get('role') in ('AXTextField','AXButton'):
        print(f'[{e[\"index\"]}] {e[\"role\"]}: {e.get(\"label\",\"\")}')
"
```

## 🔧 Fix: Daemon stirbt nach langer Idle

**Problem**: Nach 30min Idle antwortet der Daemon nicht mehr.
**Ursache**: Timeout im Daemon-Prozess.
**Fix**:
```bash
# Daemon neu starten
pkill -f cua-touch-serve 2>/dev/null
cua-touch serve &
sleep 2
```

## 🔧 Fix: Mehrere Popups — falsche window_id

**Problem**: Mehrere Popups offen, falsche ID erwischt.
**Ursache**: `list_windows` gibt mehrere IDs zurück, erste genommen.
**Fix**:
```bash
# Titel-basiert filtern
WID=$(cua-touch call list_windows '{}' | python3 -c "
import sys,json
for w in json.load(sys.stdin).get('windows',[]):
    t=(w.get('title','')).lower()
    if 'anmelden' in t or 'sign' in t or 'google' in t:
        print(w['window_id'])
")
```

## 🔧 Fix: MCP mode stuck (stdio)

**Problem**: MCP stdio mode antwortet nicht mehr.
**Ursache**: Non-ASCII in response oder JSON-Encoding-Problem.
**Fix**:
```bash
# HTTP mode statt stdio
cua-touch serve --http --port 8765
```