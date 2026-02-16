# Span MAIN 40 - Home Assistant Integration

A custom Home Assistant integration for the **Span MAIN 40 (Gen3)** smart electrical panel. Communicates directly with the panel over your local network using gRPC — no cloud, no API keys, no dependencies on Span's servers.

## Features

- **Real-time power monitoring** for all circuits and main feed (~3 second updates)
- **Per-circuit sensors**: power (W), voltage (V), current (A)
- **Main feed sensors**: total power, voltage, current, frequency (Hz)
- **Breaker state detection**: binary sensors for each circuit (ON/OFF)
- **Dual-phase support**: correctly handles both 120V and 240V circuits
- **Local-only**: direct gRPC connection to the panel, no cloud required
- **Zero configuration**: auto-discovers all circuits and their names

## Requirements

- Span MAIN 40 (Gen3) panel on your local network
- Home Assistant 2024.1 or later
- The panel must be reachable on port 50065 (gRPC, no authentication required)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Span MAIN 40" and install
3. Restart Home Assistant
4. Go to Settings > Integrations > Add Integration > "Span MAIN 40"
5. Enter your panel's IP address

### Manual

1. Copy the `custom_components/span_panel/` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings > Integrations > Add Integration > "Span MAIN 40"
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
| Circuit Breaker | N | Binary sensor - ON/OFF |

## How It Works

The Span MAIN 40 (Gen3) replaced the older REST API with a gRPC-based trait system on port 50065. This integration:

1. **Discovers circuits** via `GetInstances` RPC (trait 26 = power metrics)
2. **Fetches circuit names** via `GetRevision` RPC (trait 16 = circuit names)
3. **Streams real-time metrics** via `Subscribe` RPC for continuous updates
4. **Detects phase type** from actual metric data (field 11 = 120V, field 12 = 240V)
5. **Detects breaker state** via voltage threshold (>5V = ON)

## Network Requirements

The panel's gRPC service runs on port **50065** with no authentication. Ensure your Home Assistant instance can reach the panel on this port. If your panel is on a separate VLAN/subnet, you'll need appropriate firewall rules.

## Troubleshooting

- **Can't connect**: Verify the panel IP is correct and port 50065 is reachable (`nc -zv <panel-ip> 50065`)
- **No circuit data**: The panel needs a few seconds after connection to stream initial metrics
- **Wrong power readings**: Power values should match the Span mobile app; if they're doubled, update to the latest version

## License

MIT License

## Credits

Built by reverse-engineering the Span MAIN 40 gRPC protocol. This project is not affiliated with or endorsed by Span.
