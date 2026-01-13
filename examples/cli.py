#!/usr/bin/env python3
"""
Gamalta CLI Controller

Interactive command-line interface for testing and controlling Gamalta lights.

Usage:
    python -m examples.cli
    python examples/cli.py --debug     # Enable debug logging to debug.txt
    
Or if installed:
    python examples/cli.py
"""

import argparse
import asyncio
import sys
from datetime import datetime, time
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient, Mode, Color, LightningConfig, scan_for_devices
from gamalta.transport.ble import BleTransport


class DebugLogger:
    """
    Debug logger that captures terminal I/O and BLE packets to a file.
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._file = None
        self._filepath = Path(__file__).parent / "debug.txt"
    
    def start(self):
        """Start logging session."""
        if self.enabled:
            self._file = open(self._filepath, "a", encoding="utf-8")
            self._log("SESSION", "=== Debug session started ===")
    
    def stop(self):
        """Stop logging session."""
        if self._file:
            self._log("SESSION", "=== Debug session ended ===")
            self._file.close()
            self._file = None
    
    def _log(self, category: str, message: str):
        """Write a timestamped log entry."""
        if self._file:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self._file.write(f"[{ts}] [{category}] {message}\n")
            self._file.flush()
    
    def log_input(self, text: str):
        """Log user input."""
        self._log("INPUT", text)
    
    def log_output(self, text: str):
        """Log terminal output."""
        self._log("OUTPUT", text)
    
    def log_ble_tx(self, data: bytes):
        """Log outgoing BLE packet."""
        hex_str = data.hex(" ")
        self._log("BLE TX", hex_str)
    
    def log_ble_rx(self, data: bytes):
        """Log incoming BLE packet."""
        hex_str = data.hex(" ")
        self._log("BLE RX", hex_str)


class DebugTransport:
    """
    Wrapper around BleTransport that logs all packets.
    """
    
    def __init__(self, transport: BleTransport, logger: DebugLogger):
        self._transport = transport
        self._logger = logger
        self._user_callback = None
    
    @property
    def is_connected(self) -> bool:
        return self._transport.is_connected
    
    @property
    def address(self):
        return self._transport.address
    
    async def connect(self, address: str) -> None:
        await self._transport.connect(address)
    
    async def disconnect(self) -> None:
        await self._transport.disconnect()
    
    async def write(self, data: bytes) -> None:
        self._logger.log_ble_tx(data)
        await self._transport.write(data)
    
    async def subscribe(self, callback) -> None:
        self._user_callback = callback
        
        def logging_callback(data: bytes):
            self._logger.log_ble_rx(data)
            if self._user_callback:
                self._user_callback(data)
        
        await self._transport.subscribe(logging_callback if callback else None)


# Global debug logger (set in main)
debug_logger: DebugLogger | None = None


def debug_print(text: str):
    """Print and optionally log output."""
    print(text)
    if debug_logger and debug_logger.enabled:
        debug_logger.log_output(text)


def debug_input(prompt: str) -> str:
    """Get input and optionally log it."""
    result = input(prompt)
    if debug_logger and debug_logger.enabled:
        debug_logger.log_input(result)
    return result


def print_help():
    """Print available commands."""
    help_text = """
╔════════════════════════════════════════════════════════════════════╗
║                    GAMALTA CLI CONTROLLER                          ║
╠════════════════════════════════════════════════════════════════════╣
║  POWER                                                             ║
║    on                    - Turn light on                           ║
║    off                   - Turn light off                          ║
║                                                                    ║
║  COLOR                                                             ║
║    rgb <r> <g> <b>       - Set RGB color (0-255 each)              ║
║    rgbwc <r><g><b><w><c> - Set all channels (0-255 each)           ║
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
║    sunsync               - Intelligent SunSync 24h cycle           ║
║    coral                 - Coral reef 24h cycle                    ║
║    fish                  - Fish blue 24h cycle                     ║
║    waterweed             - Plant growth mode                       ║
║                                                                    ║
║  EFFECTS                                                           ║
║    lightning             - Preview lightning flash                 ║
║    storm <int> <freq>    - Configure lightning (0-100, 0-10)       ║
║                                                                    ║
║  OTHER                                                             ║
║    status                - Show current light state                ║
║    scan                  - Scan for devices                        ║
║    help                  - Show this help                          ║
║    quit / exit           - Disconnect and exit                     ║
╚════════════════════════════════════════════════════════════════════╝
"""
    debug_print(help_text)


async def handle_command(client: GamaltaClient, cmd: str, args: list[str]) -> bool:
    """
    Handle a single command.
    
    Returns False if should exit, True otherwise.
    """
    try:
        # Power commands
        if cmd == "on":
            await client.power_on()
            debug_print("✓ Light ON")
        
        elif cmd == "off":
            await client.power_off()
            debug_print("✓ Light OFF")
        
        elif cmd == "rgb":
            if len(args) < 3:
                debug_print("Usage: rgb <r> <g> <b>")
                return True
            r, g, b = int(args[0]), int(args[1]), int(args[2])
            await client.set_rgb(r, g, b)
            debug_print(f"✓ Color set to RGB({r}, {g}, {b})")
        
        elif cmd == "rgbwc":
            if len(args) < 5:
                debug_print("Usage: rgbwc <r> <g> <b> <w> <c>")
                return True
            r, g, b = int(args[0]), int(args[1]), int(args[2])
            w, c = int(args[3]), int(args[4])
            await client.set_rgbwc(r, g, b, w, c)
            debug_print(f"✓ Color set to RGBWC({r}, {g}, {b}, {w}, {c})")
        
        elif cmd == "color":
            if not args:
                debug_print("Usage: color <red|green|blue|white|off>")
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
                debug_print(f"Unknown color. Available: {', '.join(colors.keys())}")
                return True
            r, g, b = colors[name]
            await client.set_rgb(r, g, b)
            debug_print(f"✓ Color set to {name}")
        
        elif cmd == "warm":
            if not args:
                debug_print("Usage: warm <0-255>")
                return True
            level = int(args[0])
            await client.set_warm_white(level)
            debug_print(f"✓ Warm white set to {level}")
        
        elif cmd == "cool":
            if not args:
                debug_print("Usage: cool <0-255>")
                return True
            level = int(args[0])
            await client.set_cool_white(level)
            debug_print(f"✓ Cool white set to {level}")
        
        # Brightness commands
        elif cmd in ("bright", "brightness"):
            if not args:
                debug_print("Usage: bright <0-100>")
                return True
            percent = int(args[0])
            await client.set_brightness(percent)
            debug_print(f"✓ Brightness set to {percent}%")
        
        elif cmd == "dim":
            await client.set_brightness(25)
            debug_print("✓ Brightness set to 25%")
        
        elif cmd == "full":
            await client.set_brightness(100)
            debug_print("✓ Brightness set to 100%")
        
        # Mode commands
        elif cmd == "manual":
            await client.set_mode(Mode.MANUAL)
            debug_print("✓ Mode: Manual")
        
        elif cmd == "sunsync":
            await client.set_mode(Mode.SUNSYNC)
            debug_print("✓ Mode: SunSync (24h intelligent cycle)")
        
        elif cmd == "coral":
            await client.set_mode(Mode.CORAL_REEF)
            debug_print("✓ Mode: Coral Reef (24h cycle)")
        
        elif cmd == "fish":
            await client.set_mode(Mode.FISH_BLUE)
            debug_print("✓ Mode: Fish Blue (24h cycle)")
        
        elif cmd == "waterweed":
            await client.set_mode(Mode.WATERWEED)
            debug_print("✓ Mode: Waterweed")
        
        # Effect commands
        elif cmd == "lightning":
            await client.preview_lightning()
            debug_print("✓ Lightning preview triggered")
        
        elif cmd == "storm":
            if len(args) < 2:
                debug_print("Usage: storm <intensity 0-100> <frequency 0-10>")
                return True
            intensity = int(args[0])
            frequency = int(args[1])
            config = LightningConfig(
                intensity=intensity,
                frequency=frequency,
                start_time=time(18, 0),
                end_time=time(6, 0),
                days=0x7F,
                enabled=True
            )
            await client.configure_lightning(config)
            debug_print(f"✓ Lightning configured: intensity={intensity}%, frequency={frequency}")
        
        # Utility commands
        elif cmd == "status":
            debug_print("Querying device state...")
            state = await client.query_state()
            power_str = "ON" if state["power"] else "OFF"
            mode_name = Mode(state["mode"]).name if state["mode"] in [m.value for m in Mode] else f"Unknown({state['mode']})"
            color = state["color"]
            debug_print(f"  Power:      {power_str}")
            debug_print(f"  Mode:       {mode_name}")
            debug_print(f"  Brightness: {state['brightness']}%")
            debug_print(f"  Color:      RGB({color.r}, {color.g}, {color.b}) W:{color.warm_white} C:{color.cool_white}")
        
        elif cmd == "scan":
            debug_print("Scanning for devices...")
            devices = await scan_for_devices(timeout=5.0)
            if devices:
                debug_print(f"Found {len(devices)} device(s):")
                for d in devices:
                    debug_print(f"  • {d.name} ({d.address})")
            else:
                debug_print("No devices found")
        
        elif cmd == "help":
            print_help()
        
        elif cmd in ("quit", "exit", "q"):
            debug_print("Disconnecting...")
            return False
        
        elif cmd == "":
            pass  # Empty command, ignore
        
        else:
            debug_print(f"Unknown command: {cmd}")
            debug_print("Type 'help' for available commands")
        
        return True
    
    except ValueError as e:
        debug_print(f"Invalid value: {e}")
        return True
    except Exception as e:
        debug_print(f"Error: {e}")
        return True


async def main():
    """Main CLI loop."""
    global debug_logger
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Gamalta CLI Controller")
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging to debug.txt (logs all I/O and BLE packets)"
    )
    args = parser.parse_args()
    
    # Initialize debug logger
    debug_logger = DebugLogger(enabled=args.debug)
    debug_logger.start()
    
    if args.debug:
        debug_print(f"[DEBUG MODE] Logging to {debug_logger._filepath}")
    
    debug_print("╔════════════════════════════════════════════════════════════════════╗")
    debug_print("║              GAMALTA SMART LIGHT CLI CONTROLLER                   ║")
    debug_print("╚════════════════════════════════════════════════════════════════════╝")
    debug_print("")
    
    # Create transport with optional debug wrapper
    ble_transport = BleTransport()
    if args.debug:
        transport = DebugTransport(ble_transport, debug_logger)
    else:
        transport = ble_transport
    
    # Create client with the transport
    client = GamaltaClient(transport=transport)
    
    # Connect
    debug_print("Searching for Gamalta device...")
    try:
        await client.connect()
        debug_print("✓ Connected!")
        debug_print("")
        debug_print("Type 'help' for available commands, 'quit' to exit.")
        debug_print("")
    except Exception as e:
        debug_print(f"✗ Failed to connect: {e}")
        debug_print("")
        debug_print("Troubleshooting:")
        debug_print("  • Make sure the light is powered on")
        debug_print("  • Close any mobile apps connected to the light")
        debug_print("  • Try toggling Bluetooth off/on")
        debug_logger.stop()
        return
    
    # Command loop
    try:
        while True:
            try:
                user_input = debug_input("gamalta> ").strip()
            except EOFError:
                break
            
            parts = user_input.split()
            if not parts:
                continue
            
            cmd = parts[0].lower()
            args_list = parts[1:]
            
            if not await handle_command(client, cmd, args_list):
                break
    
    except KeyboardInterrupt:
        debug_print("\nInterrupted")
    
    finally:
        await client.disconnect()
        debug_print("Disconnected. Goodbye!")
        debug_logger.stop()


if __name__ == "__main__":
    asyncio.run(main())
