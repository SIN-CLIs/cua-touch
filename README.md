# cua-touch — macOS Accessibility-driven Computer-Use Agent

[![CI](https://github.com/SIN-CLIs/cua-touch/actions/workflows/ci.yml/badge.svg)](https://github.com/SIN-CLIs/cua-touch/actions/workflows/ci.yml)

> AX tree snapshot, element click/type by index, window_id targeting for popup automation.
> Python CLI + MCP stdio server.

**cua-touch** ist das Popup-Action-Tool der Stealth Suite.
Es ist der einzige legitime Weg, Google OAuth, Consent-Dialoge und andere
Popup-Fenster zu bedienen. skylight-cli cached NUR das Hauptfenster.

## Install

```bash
# Binary (bereits installiert)
which cua-touch || which cua-driver

# Python wrapper
pip install -e .
```

## Quick Start

```bash
cua-touch serve &
sleep 2

# Alle Fenster
cua-touch call list_windows '{}'

# Popup bedienen
cua-touch call get_window_state '{"pid":12345,"window_id":"W1"}'
cua-touch call set_value '{"pid":12345,"window_id":"W1","element_index":25,"value":"email@gmail.com"}'
cua-touch call click '{"pid":12345,"window_id":"W1","element_index":35,"action":"press"}'
```

## License

MIT
---

## 🔗 Stealth Suite

Part of the **SIN-CLIs Stealth Suite** — 17 Komponenten für autonome Browser-Automation:

| Layer | Repo | Technologie |
|-------|------|-------------|
| 🧠 Orchestrator | [stealth-runner](https://github.com/SIN-CLIs/stealth-runner) | Python |
| 🧠 ROUTER | [stealth-axiom](https://github.com/SIN-CLIs/stealth-axiom) | Python |
| 🖱️ ACT (CUA-ONLY) | [cua-touch](https://github.com/SIN-CLIs/cua-touch) | Python + Swift |
| 🎭 HIDE | [playstealth-cli](https://github.com/SIN-CLIs/playstealth-cli) | Python |
| 👁️ SENSE | [unmask-cli](https://github.com/SIN-CLIs/unmask-cli) | TypeScript |
| 📹 VERIFY | [screen-follow](https://github.com/SIN-CLIs/screen-follow) | Swift |
| 🔍 SCAN | [macos-ax-cli](https://github.com/SIN-CLIs/macos-ax-cli) | Swift |
| 🐙 AX-INDEXER | [ax-graph](https://github.com/SIN-CLIs/ax-graph) | Swift |
| 🔒 CAPTCHA | [stealth-captcha](https://github.com/SIN-CLIs/stealth-captcha) | Python |
| 🧩 SKILLS | [stealth-skills](https://github.com/SIN-CLIs/stealth-skills) | TS/Python |
| 🧱 CORE | [stealth-core](https://github.com/SIN-CLIs/stealth-core) | Python |
| 🧠 MIND | [stealth-mind](https://github.com/SIN-CLIs/stealth-mind) | Python |
| 🛡️ GUARDIAN | [stealth-guardian](https://github.com/SIN-CLIs/stealth-guardian) | Python |
| 🔄 SYNC | [stealth-sync](https://github.com/SIN-CLIs/stealth-sync) | Python |
| ⚡ SESSION | [stealth-session](https://github.com/SIN-CLIs/stealth-session) | Python |
| 💀 LEGACY | [skylight-cli](https://github.com/SIN-CLIs/skylight-cli) | Swift |
| 🔬 SOTA | [stealth-sota](https://github.com/SIN-CLIs/stealth-sota) | Python |
| 💀 LEGACY | [computer-use-mcp](https://github.com/SIN-CLIs/computer-use-mcp) | TypeScript |


## 🔗 Stealth Suite

Part of the **SIN-CLIs Stealth Suite** — 16 Komponenten für autonome Browser-Automation:

| Layer | Repo | Technologie |
|-------|------|-------------|
| 🧠 Orchestrator | [stealth-runner](https://github.com/SIN-CLIs/stealth-runner) | Python |
| 🖱️ ACT (CUA-ONLY) | [cua-touch](https://github.com/SIN-CLIs/cua-touch) | Python + Swift |
| 🎭 HIDE | [playstealth-cli](https://github.com/SIN-CLIs/playstealth-cli) | Python |
| 👁️ SENSE | [unmask-cli](https://github.com/SIN-CLIs/unmask-cli) | TypeScript |
| 📹 VERIFY | [screen-follow](https://github.com/SIN-CLIs/screen-follow) | Swift |
| 🔍 SCAN | [macos-ax-cli](https://github.com/SIN-CLIs/macos-ax-cli) | Swift |
| 🐙 AX-INDEXER | [ax-graph](https://github.com/SIN-CLIs/ax-graph) | Swift |
| 🔒 CAPTCHA | [stealth-captcha](https://github.com/SIN-CLIs/stealth-captcha) | Python |
| 🧩 SKILLS | [stealth-skills](https://github.com/SIN-CLIs/stealth-skills) | TS/Python |
| 🧱 CORE | [stealth-core](https://github.com/SIN-CLIs/stealth-core) | Python |
| 🧠 MIND | [stealth-mind](https://github.com/SIN-CLIs/stealth-mind) | Python |
| 🛡️ GUARDIAN | [stealth-guardian](https://github.com/SIN-CLIs/stealth-guardian) | Python |
| 🔄 SYNC | [stealth-sync](https://github.com/SIN-CLIs/stealth-sync) | Python |
| ⚡ SESSION | [stealth-session](https://github.com/SIN-CLIs/stealth-session) | Python |
| 💀 LEGACY | [skylight-cli](https://github.com/SIN-CLIs/skylight-cli) | Swift |
| 💀 LEGACY | [computer-use-mcp](https://github.com/SIN-CLIs/computer-use-mcp) | TypeScript |

---
