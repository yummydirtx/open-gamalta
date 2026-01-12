#!/usr/bin/env python3
"""
Protocol Probe Script

Systematically test unknown commands and parameters to discover more protocol details.
Run with caution - some commands may have unexpected effects!

Usage:
    python examples/probe.py [--test <name>]
    
Tests:
    modes       - Probe all mode IDs 0x00-0x0F
    scenes      - Query scene names for IDs 0x00-0x1F
    commands    - Try unknown command opcodes
    gatt        - Read standard BLE device info
    all         - Run all probes
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from bleak import BleakClient, BleakScanner
from gamalta import GamaltaClient, scan_for_devices
from gamalta.protocol.constants import (
    CHAR_WRITE_UUID, CHAR_NOTIFY_UUID, PACKET_HEADER
)


class ProtocolProbe:
    """Probe the Gamalta protocol for undocumented features."""
    
    def __init__(self):
        self.client = None
        self.bleak_client = None
        self.seq = 0x20
        self.responses = []
        
    async def connect(self):
        """Connect to the device."""
        print("Scanning for Gamalta device...")
        devices = await scan_for_devices(timeout=5.0)
        
        if not devices:
            print("❌ No Gamalta device found!")
            return False
            
        device = devices[0]
        print(f"✓ Found: {device.name} ({device.address})")
        
        self.bleak_client = BleakClient(device.address)
        await self.bleak_client.connect()
        
        # Subscribe to notifications
        await self.bleak_client.start_notify(
            CHAR_NOTIFY_UUID, 
            self._on_notify
        )
        
        # Perform handshake
        await self._handshake()
        print("✓ Connected and authenticated\n")
        return True
    
    async def disconnect(self):
        """Disconnect from device."""
        if self.bleak_client:
            await self.bleak_client.disconnect()
    
    def _on_notify(self, sender, data: bytearray):
        """Handle notification responses."""
        self.responses.append(bytes(data))
        
    async def _send(self, payload: bytes, wait_response: bool = True) -> bytes | None:
        """Send a raw command and optionally wait for response."""
        self.responses.clear()
        self.seq = (self.seq + 1) % 256
        packet = bytes([PACKET_HEADER, self.seq]) + payload
        
        await self.bleak_client.write_gatt_char(
            CHAR_WRITE_UUID, packet, response=False
        )
        
        if wait_response:
            await asyncio.sleep(0.15)
            if self.responses:
                return self.responses[0]
        return None
    
    async def _handshake(self):
        """Login and time sync."""
        import datetime
        
        # Login
        await self._send(bytes([0x10, 0x07, 0x02, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36]))
        
        # Time sync
        now = datetime.datetime.now()
        await self._send(bytes([
            0x16, 0x07, now.year - 2000, now.month, now.day,
            now.hour, now.minute, now.second
        ]))
    
    # =========================================================================
    # PROBE TESTS
    # =========================================================================
    
    async def probe_modes(self):
        """Test all mode IDs from 0x00 to 0x0F."""
        print("=" * 60)
        print("PROBING MODE IDs (0x00 - 0x0F)")
        print("=" * 60)
        
        known_modes = {
            0x00: "Manual",
            0x01: "SunSync",
            0x02: "Coral Reef",
            0x03: "Fish Blue",
            0x04: "Waterweed",
            0x0B: "Custom Basic",
            0x0C: "Custom Pro",
        }
        
        for mode_id in range(0x10):
            # Query state after setting mode
            await self._send(bytes([0x6A, 0x01, mode_id]))
            response = await self._send(bytes([0x03, 0x00]))
            
            status = known_modes.get(mode_id, "???")
            
            if response:
                # Parse response: 04 08 [power] [mode] [bright] ...
                actual_mode = response[4] if len(response) > 4 else None
                if actual_mode == mode_id:
                    print(f"  0x{mode_id:02X}: ✓ Accepted ({status})")
                else:
                    print(f"  0x{mode_id:02X}: → Redirected to 0x{actual_mode:02X} ({status})")
            else:
                print(f"  0x{mode_id:02X}: ? No response ({status})")
            
            await asyncio.sleep(0.2)
        
        # Return to manual
        await self._send(bytes([0x6A, 0x01, 0x00]))
        print()
    
    async def probe_scene_names(self):
        """Query scene names for IDs 0x00 to 0x1F."""
        print("=" * 60)
        print("PROBING SCENE NAMES (0x00 - 0x1F)")
        print("=" * 60)
        
        for scene_id in range(0x20):
            response = await self._send(bytes([0x68, 0x01, scene_id]))
            
            if response and len(response) > 3:
                # Response format: 69 [len] [name as ASCII]
                name_bytes = response[3:]
                # Find null terminator
                null_idx = name_bytes.find(0)
                if null_idx > 0:
                    name = name_bytes[:null_idx].decode('ascii', errors='replace')
                    print(f"  0x{scene_id:02X}: \"{name}\"")
                elif name_bytes[0] != 0:
                    name = name_bytes.decode('ascii', errors='replace').rstrip('\x00')
                    print(f"  0x{scene_id:02X}: \"{name}\"")
                else:
                    print(f"  0x{scene_id:02X}: (empty)")
            else:
                print(f"  0x{scene_id:02X}: (no response)")
            
            await asyncio.sleep(0.1)
        print()
    
    async def probe_unknown_commands(self):
        """Test undocumented command opcodes."""
        print("=" * 60)
        print("PROBING UNKNOWN COMMAND OPCODES")
        print("=" * 60)
        
        # Known commands to skip
        known = {0x01, 0x03, 0x09, 0x10, 0x16, 0x40, 0x42, 0x50, 0x52, 0x54, 0x56, 
                 0x60, 0x62, 0x64, 0x68, 0x6A, 0x6C, 0x6E, 0x70, 0x72, 0x74, 0x76}
        
        # Test ranges where we might find commands
        test_ranges = [
            (0x02, 0x10),   # Near power/login
            (0x17, 0x20),   # After time sync
            (0x44, 0x50),   # Before color
            (0x58, 0x60),   # After timer
            (0x78, 0x80),   # After lightning
        ]
        
        for start, end in test_ranges:
            print(f"\n  Testing 0x{start:02X} - 0x{end-1:02X}:")
            for cmd in range(start, end):
                if cmd in known:
                    continue
                    
                # Try with minimal payload
                response = await self._send(bytes([cmd, 0x00]))
                
                if response and len(response) > 2:
                    resp_cmd = response[2]
                    print(f"    0x{cmd:02X}: Response 0x{resp_cmd:02X} - {response[3:].hex()}")
                else:
                    print(f"    0x{cmd:02X}: (no response)")
                
                await asyncio.sleep(0.1)
        print()
    
    async def probe_gatt_info(self):
        """Read standard BLE GATT characteristics."""
        print("=" * 60)
        print("READING STANDARD BLE DEVICE INFO")
        print("=" * 60)
        
        # Standard GATT UUIDs
        standard_chars = {
            "00002a00-0000-1000-8000-00805f9b34fb": "Device Name",
            "00002a01-0000-1000-8000-00805f9b34fb": "Appearance",
            "00002a24-0000-1000-8000-00805f9b34fb": "Model Number",
            "00002a25-0000-1000-8000-00805f9b34fb": "Serial Number",
            "00002a26-0000-1000-8000-00805f9b34fb": "Firmware Revision",
            "00002a27-0000-1000-8000-00805f9b34fb": "Hardware Revision",
            "00002a28-0000-1000-8000-00805f9b34fb": "Software Revision",
            "00002a29-0000-1000-8000-00805f9b34fb": "Manufacturer Name",
        }
        
        for uuid, name in standard_chars.items():
            try:
                value = await self.bleak_client.read_gatt_char(uuid)
                # Try to decode as string
                try:
                    decoded = value.decode('utf-8')
                    print(f"  {name}: \"{decoded}\"")
                except:
                    print(f"  {name}: {value.hex()}")
            except Exception as e:
                print(f"  {name}: (not available)")
        
        print()
    
    async def probe_device_id(self):
        """Query the device ID command in more detail."""
        print("=" * 60)
        print("PROBING DEVICE ID (0x09)")
        print("=" * 60)
        
        # Try different payload values
        for payload in [0x00, 0x01, 0x02, 0xFF]:
            response = await self._send(bytes([0x09, 0x01, payload]))
            if response:
                print(f"  Payload 0x{payload:02X}: {response.hex()}")
            await asyncio.sleep(0.1)
        print()
    
    async def run_all(self):
        """Run all probe tests."""
        await self.probe_gatt_info()
        await self.probe_modes()
        await self.probe_scene_names()
        await self.probe_device_id()
        await self.probe_unknown_commands()
        
        print("=" * 60)
        print("PROBING COMPLETE")
        print("=" * 60)


async def main():
    probe = ProtocolProbe()
    
    test_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if not await probe.connect():
        return
    
    try:
        if test_name == "modes":
            await probe.probe_modes()
        elif test_name == "scenes":
            await probe.probe_scene_names()
        elif test_name == "commands":
            await probe.probe_unknown_commands()
        elif test_name == "gatt":
            await probe.probe_gatt_info()
        elif test_name == "all":
            await probe.run_all()
        else:
            print(f"Unknown test: {test_name}")
            print("Available: modes, scenes, commands, gatt, all")
    finally:
        await probe.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
