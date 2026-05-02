# cua-touch — macOS Accessibility-driven Computer-Use Agent

> AX tree snapshot, element click/type by index, window_id targeting for popup automation.
> Python CLI + MCP stdio server.

**cua-touch** ist das Popup-Action-Tool der Stealth-Quad.
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