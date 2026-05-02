# anti-learn.md — ANTI-PATTERNS für cua-touch

## ❌ skylight-cli in Popup-Kontext

**FALSCH**: `skylight-cli list-elements --pid X` nach OAuth-Klick (Popup offen).
**PROBLEM**: skylight-cli cached NUR das Hauptfenster. Popup ist unsichtbar.
→ Leere Liste oder falsche Indices → falsches Element → Detection.

## ❌ Ohne Daemon operieren

**FALSCH**: `cua-touch call click ...` ohne `cua-touch serve &` davor.
**PROBLEM**: "No cached AX state" → alle Operationen schlagen fehl.
→ Immer Daemon starten, 2s warten, dann operationen.

## ❌ Cached element_index wiederverwenden

**FALSCH**: element_index 25 aus letztem OAuth merken → wiederverwenden.
**PROBLEM**: Google kann Layout ändern → Index zeigt auf falsches Element.
→ Immer `get_window_state` aufrufen, neuen Index finden.

## ❌ cua-touch im Hauptfenster

**FALSCH**: `cua-touch call click '{"pid":X,"window_id":0,...}'` für Hauptfenster-Buttons.
**PROBLEM**: Umständlich, window_id=0 ist Hauptfenster.
→ Für Hauptfenster: `skylight-cli click --pid X --element-index Y`

## ❌ Direkt click ohne get_window_state

**FALSCH**: `cua-touch call click '{"pid":X,"window_id":W,"element_index":25}'` ohne State.
**PROBLEM**: Kein Cache, Ax-Tree nicht geladen, könnte falsches Element treffen.
→ Immer: list_windows → get_window_state → click/type.

## ❌ Falschen action-Type nutzen

**FALSCH**: `action="hold"` für Button-Click.
**PROBLEM**: Manche Elemente unterstützen hold nicht.
→ `action="press"` für Standard-Buttons. `pressAndHold` nur für Slider/Dropdown.

## ❌ set_value ohne Value-Parameter

**FALSCH**: `cua-touch call set_value '{"pid":X,"window_id":W,"element_index":25}'`
**PROBLEM**: Leeres value → kein Text eingetippt.
→ Immer `value` parameter mitschicken.

## ❌ Timeout nicht handhaben

**FALSCH**: Kein Error-Handling bei cua-touch calls.
**PROBLEM**: Bei Fehler → kein Retry → Flow stuck.
→ Immer return-code prüfen, bei Fehler neu versuchen (max 3x).

## ❌ Alte window_id nutzen nach Page-Transition

**FALSCH**: window_id aus letztem OAuth wiederverwenden.
**PROBLEM**: Neues Popup = neue window_id. Alte ID → "Window not found".
→ Nach jedem neuen Popup: list_windows neu aufrufen.

## ❌ Blind klicken ohne Vision

**FALSCH**: `cua-touch call click ...` ohne jemals Vision zu nutzen.
**PROBLEM**: Bei Layout-Änderung → falsche Elemente.
→ Erst Vision-Pipeline (skylight + Omni), dann 10x success → Promotion → CLI-only.