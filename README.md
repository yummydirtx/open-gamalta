# Open-Gamalta

Open source Python library for controlling Gamalta Bluetooth smart aquarium lights.

## Features

- **Full Protocol Support**: Power, color (RGBWC), brightness, modes, and lightning effects
- **Async-First**: Built on `asyncio` for modern Python applications
- **Clean API**: Simple, intuitive interface with type hints throughout
- **Auto-Discovery**: Automatically finds Gamalta devices
- **Extensible**: Modular architecture for easy customization

## Installation

```bash
# From source (development)
pip install -e .

# Or just install dependencies
pip install bleak
```

## Quick Start

```python
import asyncio
from gamalta import GamaltaClient, Mode

async def main():
    # Auto-discover and connect
    async with GamaltaClient() as light:
        # Basic control
        await light.power_on()
        await light.set_brightness(75)
        await light.set_color(255, 100, 0)  # Warm orange
        
        # Use a scene
        await light.set_mode(Mode.CORAL_REEF)

asyncio.run(main())
```

## Examples

Several examples are included in the `examples/` directory:

- **`cli.py`** - Interactive command-line controller for testing
- **`basic_control.py`** - Simple connection and control demo
- **`color_cycle.py`** - Rainbow color cycling
- **`discover.py`** - Device discovery and BLE service listing  
- **`lightning_demo.py`** - Lightning storm effect demo

### CLI Controller

```bash
python examples/cli.py
```

This provides an interactive interface for testing all light features:

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

gamalta> quit
Disconnected. Goodbye!
```

## API Reference

### GamaltaClient

The main interface for controlling lights.

```python
from gamalta import GamaltaClient

client = GamaltaClient()

# Connection
await client.connect()              # Auto-discover and connect
await client.connect(address="...")  # Connect to specific device
await client.disconnect()

# Power
await client.power_on()
await client.power_off()

# Color (RGBWC)
await client.set_color(r, g, b)
await client.set_color(r, g, b, warm_white=100, cool_white=50)

# Brightness
await client.set_brightness(75)  # 0-100%

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

See the `documentation/` directory for detailed protocol specifications:

- `GamaltaProtocolLightning.md` - Lightning effect commands
- `scenes_extension.md` - Modes and scene configuration
- `first_explorations.md` - Initial reverse engineering notes

## Troubleshooting

### Device Not Found

- Ensure the light is powered on
- **Close any mobile apps** connected to the light (it only supports one connection)
- Try toggling Bluetooth off/on on your computer

### Commands Ignored

- The handshake must complete within a few seconds of connecting
- Commands are ignored if the sequence number is duplicated

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! This is a reverse-engineered protocol, so additional findings and improvements are appreciated.
