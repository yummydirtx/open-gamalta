#!/usr/bin/env python3
"""
Gamalta CLI Controller

Interactive command-line interface for testing and controlling Gamalta lights.

Usage:
    python -m examples.cli
    
Or if installed:
    python examples/cli.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient, Mode, Color, scan_for_devices


def print_help():
    """Print available commands."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                    GAMALTA CLI CONTROLLER                          ║
╠════════════════════════════════════════════════════════════════════╣
║  POWER                                                             ║
║    on                    - Turn light on                           ║
║    off                   - Turn light off                          ║
║                                                                    ║
║  COLOR                                                             ║
║    rgb <r> <g> <b>       - Set RGB color (0-255 each)              ║
║    color <name>          - Set preset: red, green, blue, white     ║
║    warm <level>          - Set warm white (0-255)                  ║
║    cool <level>          - Set cool white (0-255)                  ║
║                                                                    ║
║  BRIGHTNESS                                                        ║
║    bright <0-100>        - Set brightness percentage               ║
║    dim                   - Set to 25%                              ║
║    full                  - Set to 100%                             ║
║                                                                    ║
║  MODES                                                             ║
║    manual                - Static color mode                       ║
║    coral                 - Coral reef 24h cycle                    ║
║    fish                  - Fish blue 24h cycle                     ║
║    waterweed             - Plant growth mode                       ║
║                                                                    ║
║  EFFECTS                                                           ║
║    lightning             - Preview lightning flash                 ║
║                                                                    ║
║  OTHER                                                             ║
║    scan                  - Scan for devices                        ║
║    help                  - Show this help                          ║
║    quit / exit           - Disconnect and exit                     ║
╚════════════════════════════════════════════════════════════════════╝
""")


async def handle_command(client: GamaltaClient, cmd: str, args: list[str]) -> bool:
    """
    Handle a single command.
    
    Returns False if should exit, True otherwise.
    """
    try:
        # Power commands
        if cmd == "on":
            await client.power_on()
            print("✓ Light ON")
        
        elif cmd == "off":
            await client.power_off()
            print("✓ Light OFF")
        
        # Color commands
        elif cmd == "rgb":
            if len(args) < 3:
                print("Usage: rgb <r> <g> <b>")
                return True
            r, g, b = int(args[0]), int(args[1]), int(args[2])
            await client.set_color(r, g, b)
            print(f"✓ Color set to RGB({r}, {g}, {b})")
        
        elif cmd == "color":
            if not args:
                print("Usage: color <red|green|blue|white|off>")
                return True
            name = args[0].lower()
            colors = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "white": (255, 255, 255),
                "off": (0, 0, 0),
                "orange": (255, 165, 0),
                "purple": (128, 0, 128),
                "cyan": (0, 255, 255),
                "yellow": (255, 255, 0),
            }
            if name not in colors:
                print(f"Unknown color. Available: {', '.join(colors.keys())}")
                return True
            r, g, b = colors[name]
            await client.set_color(r, g, b)
            print(f"✓ Color set to {name}")
        
        elif cmd == "warm":
            if not args:
                print("Usage: warm <0-255>")
                return True
            level = int(args[0])
            await client.set_color(0, 0, 0, warm_white=level, cool_white=0)
            print(f"✓ Warm white set to {level}")
        
        elif cmd == "cool":
            if not args:
                print("Usage: cool <0-255>")
                return True
            level = int(args[0])
            await client.set_color(0, 0, 0, warm_white=0, cool_white=level)
            print(f"✓ Cool white set to {level}")
        
        # Brightness commands
        elif cmd in ("bright", "brightness"):
            if not args:
                print("Usage: bright <0-100>")
                return True
            percent = int(args[0])
            await client.set_brightness(percent)
            print(f"✓ Brightness set to {percent}%")
        
        elif cmd == "dim":
            await client.set_brightness(25)
            print("✓ Brightness set to 25%")
        
        elif cmd == "full":
            await client.set_brightness(100)
            print("✓ Brightness set to 100%")
        
        # Mode commands
        elif cmd == "manual":
            await client.set_mode(Mode.MANUAL)
            print("✓ Mode: Manual")
        
        elif cmd == "coral":
            await client.set_mode(Mode.CORAL_REEF)
            print("✓ Mode: Coral Reef (24h cycle)")
        
        elif cmd == "fish":
            await client.set_mode(Mode.FISH_BLUE)
            print("✓ Mode: Fish Blue (24h cycle)")
        
        elif cmd == "waterweed":
            await client.set_mode(Mode.WATERWEED)
            print("✓ Mode: Waterweed")
        
        # Effect commands
        elif cmd == "lightning":
            await client.preview_lightning()
            print("✓ Lightning preview triggered")
        
        # Utility commands
        elif cmd == "scan":
            print("Scanning for devices...")
            devices = await scan_for_devices(timeout=5.0)
            if devices:
                print(f"Found {len(devices)} device(s):")
                for d in devices:
                    print(f"  • {d.name} ({d.address})")
            else:
                print("No devices found")
        
        elif cmd == "help":
            print_help()
        
        elif cmd in ("quit", "exit", "q"):
            print("Disconnecting...")
            return False
        
        elif cmd == "":
            pass  # Empty command, ignore
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
        
        return True
    
    except ValueError as e:
        print(f"Invalid value: {e}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return True


async def main():
    """Main CLI loop."""
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              GAMALTA SMART LIGHT CLI CONTROLLER                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Create client
    client = GamaltaClient()
    
    # Connect
    print("Searching for Gamalta device...")
    try:
        await client.connect()
        print("✓ Connected!")
        print()
        print("Type 'help' for available commands, 'quit' to exit.")
        print()
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print()
        print("Troubleshooting:")
        print("  • Make sure the light is powered on")
        print("  • Close any mobile apps connected to the light")
        print("  • Try toggling Bluetooth off/on")
        return
    
    # Command loop
    try:
        while True:
            try:
                user_input = input("gamalta> ").strip()
            except EOFError:
                break
            
            parts = user_input.split()
            if not parts:
                continue
            
            cmd = parts[0].lower()
            args = parts[1:]
            
            if not await handle_command(client, cmd, args):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        await client.disconnect()
        print("Disconnected. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
