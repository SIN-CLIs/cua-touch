# banned.md — Verbotene Patterns

## 🚫 BANNED TOOLS / PATTERNS

| Pattern | Warum | Alternative |
|---------|-------|-------------|
| `skylight-cli` in Popups | cached nur Hauptfenster | `cua-touch call ...` |
| `cua-touch` im Hauptfenster | umständlich, window_id=0 | `skylight-cli click --pid X --element-index Y` |
| Koordinaten raten | instabil, flexibel | element_index (AX-Accessibility) |
| Ohne Daemon operieren | "No cached AX state" | `cua-touch serve &` zuerst |
| Alte window_id wiederverwenden | invalid nach Close | `list_windows` neu |

## 🚫 FALSCHE TOOL-WAHL

```
Hauptfenster (heypiggy.com/dashboard)
  → skylight-cli click --pid X --element-index Y ✅
  → cua-touch call ... ❌ (umständlich)

Popup (Google OAuth, Consent)
  → cua-touch call ... ✅
  → skylight-cli list-elements --pid X ❌ (sieht nichts!)
```

## 🚫 RICHTIGE ALTERNATIVEN

```bash
# ✅ Daemon zuerst
cua-touch serve &

# ✅ Immer diese Reihenfolge
cua-touch call list_windows '{}'           # 1. Window-ID finden
cua-touch call get_window_state '...'      # 2. Cache laden
cua-touch call click '...'                 # 3. Execute

# ✅ Haubtfenster: skylight
skylight-cli click --pid 12345 --element-index 42

# ✅ Popup: cua-touch
cua-touch call click '{"pid":12345,"window_id":"W1","element_index":25,"action":"press"}'
```