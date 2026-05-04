# PLAN-REFERENCE.md

Canonical Plan: [stealth-runner/MASTER-PLAN-2026-05-02.md](https://github.com/SIN-CLIs/stealth-runner/blob/main/MASTER-PLAN-2026-05-02.md)

Alle 7 Repos der Stealth Suite referenzieren diesen Plan.

```bash
# Canonical plan location
~/dev/stealth-runner/MASTER-PLAN-2026-05-02.md
```

---

## Stealth Suite Plan Architecture

```
MASTER-PLAN (stealth-runner)
├── stealth-runner    — Orchestrator + flow-optimizer + live-eye
├── stealth-skills    — Skill-Library (heypiggy, modules)
├── playstealth-cli   — Browser HIDE layer
├── skylight-cli      — Hauptfenster ACT layer
├── screen-follow     — VERIFY layer (video recording)
├── unmask-cli        — SENSE layer (CDP/DOM sniffing)
└── cua-touch         — Popup ACT layer (this repo)
```

## Related Plans

- `ROADMAP-10-DAY-2026-05-02.md` — 10-day sprint
- `PLAN-REFERENCE.md` — Dieses Dokument (in jedem Repo)