# Span MAIN 40 - Home Assistant Integration

[![HACS Action](https://github.com/Griswoldlabs/span-panel-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/Griswoldlabs/span-panel-ha/actions/workflows/validate.yml)
[![Hassfest](https://github.com/Griswoldlabs/span-panel-ha/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Griswoldlabs/span-panel-ha/actions/workflows/hassfest.yml)
[![GitHub Release](https://img.shields.io/github/v/release/Griswoldlabs/span-panel-ha)](https://github.com/Griswoldlabs/span-panel-ha/releases)
[![License: MIT](https://img.shields.io/github/license/Griswoldlabs/span-panel-ha)](LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

**The first Home Assistant integration for the Span MAIN 40 (Gen3) smart electrical panel.**

Communicates directly with the panel over your local network using **gRPC** — no cloud, no API keys, no dependencies on Span's servers. The Gen3 panel replaced the older REST API with a completely new gRPC-based trait system, and existing Span integrations don't support it. This one does.

## Why This Integration?

The Span MAIN 40 (Gen3) uses a fundamentally different protocol than older Span panels:

| | Older Span Panels | **MAIN 40 Gen3** |
|---|---|---|
| Protocol | REST API (HTTP) | **gRPC (protobuf)** |
| Port | 80/443 | **50065** |
| Authentication | Bearer token | **None required** |
| Data delivery | Polling | **Real-time streaming** |
| Existing HA support | Yes (SpanPanel/span) | **This integration only** |

If you have a Gen3 panel and tried the existing Span integration, it didn't work — because the REST API returns 502 on Gen3 hardware. This integration speaks the panel's native gRPC protocol.

## Features

- **Real-time power monitoring** for all circuits and main feed via gRPC streaming
- **Per-circuit sensors**: power (W), voltage (V), current (A)
- **Main feed sensors**: total power, voltage, current, frequency (Hz)
- **Breaker state detection**: binary sensors for each circuit (ON/OFF)
- **Dual-phase support**: correctly handles both 120V single-phase and 240V dual-phase circuits
- **Local-only**: direct gRPC connection to the panel, no cloud required
- **Zero configuration**: auto-discovers all circuits and their names from the panel
- **Config flow**: set up through the HA UI — just enter the panel IP

## Requirements

- Span MAIN 40 (Gen3) panel on your local network
- Home Assistant 2024.1 or later
- The panel must be reachable on port 50065 (gRPC)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots (top right) > **Custom repositories**
3. Add `https://github.com/Griswoldlabs/span-panel-ha` as an **Integration**
4. Search for "Span MAIN 40" and install
5. Restart Home Assistant
6. Go to **Settings > Integrations > Add Integration > "Span MAIN 40"**
7. Enter your panel's IP address

### Manual

1. Copy the `custom_components/span_panel/` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings > Integrations > Add Integration > "Span MAIN 40"**
4. Enter your panel's IP address

## Entities Created

For a panel with N circuits, the integration creates:

| Entity Type | Count | Description |
|-------------|-------|-------------|
| Main Feed Power | 1 | Total household power (W) |
| Main Feed Voltage | 1 | Split-phase voltage (V) |
| Main Feed Current | 1 | Total current draw (A) |
| Main Feed Frequency | 1 | Line frequency (Hz) |
| Circuit Power | N | Per-circuit power (W) |
| Circuit Voltage | N | Per-circuit voltage (V) |
| Circuit Current | N | Per-circuit current (A) |
| Circuit Breaker | N | Binary sensor — ON/OFF |

**Example**: A 25-circuit panel creates **104 entities** (4 main feed + 75 circuit sensors + 25 breaker binary sensors).

## How It Works

The integration uses the panel's native gRPC service to:

1. **Discover circuits** via `GetInstances` RPC (trait 26 = power metrics)
2. **Fetch circuit names** via `GetRevision` RPC (trait 16 = circuit labels)
3. **Stream real-time metrics** via `Subscribe` RPC for continuous updates
4. **Detect phase type** from actual metric data (field 11 = 120V, field 12 = 240V)
5. **Detect breaker state** via voltage threshold (>5V = ON, <5V = OFF)

All communication is local, on-network, with no cloud dependency.

## Network Requirements

The panel's gRPC service runs on port **50065** with no authentication. Ensure your Home Assistant instance can reach the panel on this port.

**If your panel is on a separate VLAN/subnet** (recommended for IoT devices), add a firewall rule allowing TCP traffic from your HA host to the panel on port 50065.

## Compatibility

| Panel Model | Supported | Notes |
|-------------|-----------|-------|
| Span MAIN 40 (Gen3) | **Yes** | Full support via gRPC |
| Span MAIN 32 (Gen2 and earlier) | No | Use [SpanPanel/span](https://github.com/SpanPanel/span) instead |
| Span MLO 48 | Unknown | May work if it uses the same gRPC protocol — testers welcome |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect | Verify the panel IP and that port 50065 is reachable: `nc -zv <panel-ip> 50065` |
| No circuit data | The panel needs a few seconds after connection to stream initial metrics |
| Wrong power readings | Power values should match the Span app; if doubled, update to latest version |
| Integration not found | Restart HA after installing; check `custom_components/span_panel/` exists |

## Roadmap

- [x] Real-time circuit monitoring (power, voltage, current)
- [x] Breaker state detection
- [x] Dual-phase (240V) circuit support
- [x] Config flow UI setup
- [ ] Energy dashboard integration (Riemann sum sensors)
- [ ] Circuit control (on/off) — pending gRPC command discovery
- [ ] MLO 48 compatibility testing

## Contributing

Contributions are welcome! If you have a Gen3 panel and can help test, please open an issue with your panel details. If you have an MLO 48, we'd especially love to hear from you.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Credits

Built by [GriswoldLabs](https://griswoldlabs.com) by reverse-engineering the Span MAIN 40 gRPC protocol. This project is not affiliated with or endorsed by Span.
