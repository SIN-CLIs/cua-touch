# learn.md — KRITISCHE Learnings für cua-touch

## 🔑 IMMER Daemon zuerst (serve &)

**FALSCH**: Direkt `cua-touch call click ...` ohne Daemon.
**PROBLEM**: "No cached AX state" → alle Operationen schlagen fehl.
**RICHTIG**: `cua-touch serve &` → 2s warten → dann operationen.

## 🔑 list_windows → get_window_state → click/type

Immer in dieser Reihenfolge:
1. `list_windows` → window_id finden
2. `get_window_state` → AX-Tree in Cache laden
3. `click/type` → aus Cache bedienen

Nie direkt `click` ohne `get_window_state` davor.

## 🔑 Window-ID ist Session-spezifisch

Jedes OAuth-Popup bekommt eine neue window_id. Alte IDs sind invalide.
Nach OAuth: `list_windows` neu aufrufen, neue ID holen.

## 🔑 Element-Index ist POPUP-spezifisch

Der element_index 25 aus dem Hauptfenster ist NICHT der gleiche wie 25 im Popup.
skylight-cli element_index ≠ cua-touch element_index. NIE mischen!

## 🔑 Google OAuth: element_index ثابت (PID 31710 verifiziert)

- 25 = Email TextField
- 35 = "Weiter" Button
- 65 = "Fortfahren" Consent
- 41 = Finales "Weiter" → Dashboard

Diese Indices sind für das spezifische Popup-Layout. Bei Google-Layout-Update → neu scannen.

## 🔑 Timeout Handling

cua-touch calls haben kein automatic retry. Bei Fehler:
```bash
cua-touch call get_window_state '{"pid":12345,"window_id":"W1}'
# → Error oder leer? → nochmal versuchen
cua-touch call get_window_state '{"pid":12345,"window_id":"W1}'
```

Bei "No cached AX state": Daemon neu starten oder Page-Transition abwarten.

## 🔑 Integration mit Flow-Optimizer

Flow-Optimizer trackt jeden cua-touch call:
```bash
python3 -m runner.flow_optimizer run heypiggy-google-login 31710
# → cua-touch calls werden aus fixed artifact gelesen
# → Kein Vision nötig (production flow)
# → 10x schneller als Vision-Pipeline
```

## 🔑 AX-Tree ist live (nicht cached after click)

Nach einem `click` kann sich der AX-Tree ändern (neue Elemente erscheinen).
Für weitere Operationen: `get_window_state` nochmal aufrufen (liest aus Cache, nicht live).
Für live-State: Daemon neu starten oder Page-Transition abwarten.

## 🔑 PID muss vom Hauptfenster-Chrome sein

cua-touch nutzt die Chrome PID für popup-filtering.
Bei Playwright: CDP-Endpoint PID nutzen.
Bei playstealth: `playstealth launch` gibt PID zurück.

## 🔑 Flow-Optimizer: 10x consecutive = Promotion

Wenn `heypiggy-google-login` 10x hintereinander funktioniert (via flow-optimizer):
→ cua-touch steps werden als production artifact gespeichert
→ Ab jetzt: `python3 -m runner.flow_optimizer run heypiggy-google-login $PID`
→ Kein Vision, kein Screenshot, nur noch CLI calls