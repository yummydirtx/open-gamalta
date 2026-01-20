<div align="center">

# Open-Gamalta

**Open source Python library for controlling Gamalta Bluetooth smart aquarium lights**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#features) · [Installation](#installation) · [Quick Start](#quick-start) · [Web Interface](#web-interface) · [API Reference](#api-reference)

</div>

---

## Features

| Feature | Description |
|---------|-------------|
| **Full Protocol Support** | Power, color (RGBWC), brightness, modes, and lightning effects |
| **Async-First** | Built on `asyncio` for modern Python applications |
| **Clean API** | Simple, intuitive interface with type hints throughout |
| **Auto-Discovery** | Automatically finds Gamalta devices via BLE scanning |
| **Web Interface** | React + FastAPI web control panel included |

## Requirements

- Python 3.10 or higher
- Bluetooth Low Energy (BLE) adapter
- Linux, macOS, or Windows

## Installation

```bash
# Clone the repository
git clone https://github.com/yummydirtx/open-gamalta.git
cd open-gamalta

# Install in development mode
pip install -e .

# Or install dependencies only
pip install bleak
```

## Quick Start

```python
import asyncio
from gamalta import GamaltaClient, Mode

async def main():
    async with GamaltaClient() as light:
        await light.power_on()
        await light.set_brightness(75)
        await light.set_color(255, 100, 0)  # Warm orange
        await light.set_mode(Mode.CORAL_REEF)

asyncio.run(main())
```

## Examples

The `examples/` directory contains ready-to-run demos:

| Example | Description |
|---------|-------------|
| `cli.py` | Interactive command-line controller |
| `basic_control.py` | Simple connection and control demo |
| `color_cycle.py` | Rainbow color cycling animation |
| `discover.py` | Device discovery and BLE service listing |
| `lightning_demo.py` | Lightning storm effect demo |

### CLI Controller

```bash
python examples/cli.py
```

```
gamalta> on
✓ Light ON

gamalta> rgb 255 100 0
✓ Color set to RGB(255, 100, 0)

gamalta> bright 80
✓ Brightness set to 80%

gamalta> coral
✓ Mode: Coral Reef (24h cycle)

gamalta> lightning
✓ Lightning preview triggered
```

## Web Interface

A full-featured web control panel is included with React frontend and FastAPI backend.

```bash
cd web
make install    # Install all dependencies
make backend    # Terminal 1: Start backend on :8080
make frontend   # Terminal 2: Start frontend on :5173
```

Open http://localhost:5173 in your browser.

See [`web/README.md`](web/README.md) for full documentation.

## API Reference

### GamaltaClient

The main interface for controlling lights.

```python
from gamalta import GamaltaClient

client = GamaltaClient()

# Connection
await client.connect()               # Auto-discover and connect
await client.connect(address="...")  # Connect to specific device
await client.disconnect()

# Power
await client.power_on()
await client.power_off()

# Color (RGBWC)
await client.set_color(r, g, b)
await client.set_color(r, g, b, warm_white=100, cool_white=50)

# Brightness (0-100%)
await client.set_brightness(75)

# Modes
await client.set_mode(Mode.MANUAL)
await client.set_mode(Mode.CORAL_REEF)
await client.set_mode(Mode.FISH_BLUE)
await client.set_mode(Mode.WATERWEED)

# Lightning
await client.preview_lightning()
await client.configure_lightning(config)
```

### Types

```python
from gamalta import Color, LightningConfig, Mode, Day
from datetime import time

# Color with validation
color = Color(255, 100, 0)
color = Color.red()
color = Color.white(warm=128, cool=255)

# Lightning schedule
config = LightningConfig(
    intensity=75,
    frequency=5,
    start_time=time(18, 0),
    end_time=time(22, 0),
    days=Day.MONDAY | Day.FRIDAY,
    enabled=True
)
```

## Protocol Documentation

The `documentation/` directory contains detailed protocol specifications:

- `GamaltaProtocolLightning.md` - Lightning effect commands
- `scenes_extension.md` - Modes and scene configuration
- `first_explorations.md` - Initial reverse engineering notes

## Troubleshooting

<details>
<summary><strong>Device Not Found</strong></summary>

- Ensure the light is powered on
- **Close any mobile apps** connected to the light (BLE supports only one connection)
- Toggle Bluetooth off/on on your computer
- Check that your BLE adapter is functioning

</details>

<details>
<summary><strong>Commands Ignored</strong></summary>

- The handshake must complete within a few seconds of connecting
- Commands are ignored if the sequence number is duplicated
- Ensure no other application is connected to the device

</details>

## Contributing

Contributions are welcome! This is a reverse-engineered protocol, so additional findings and improvements are appreciated.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
