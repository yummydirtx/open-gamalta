#!/usr/bin/env python3
"""
Device Discovery Example

Scan for and list Gamalta devices, then show their BLE services.

Migrated from the original detector.py.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from bleak import BleakClient, BleakScanner
from gamalta import scan_for_devices


async def main():
    print("Gamalta Device Discovery")
    print("=" * 40)
    print()
    
    # Scan for all BLE devices first to see what's around
    print("Scanning for all BLE devices...")
    all_devices = await BleakScanner.discover(timeout=5.0)
    
    print(f"\nFound {len(all_devices)} total BLE devices:")
    for d in all_devices:
        name = d.name or "Unknown"
        print(f"  • {name} ({d.address})")
    
    # Filter for Gamalta devices
    print("\n" + "=" * 40)
    print("Filtering for Gamalta devices...")
    gamalta_devices = await scan_for_devices(timeout=5.0)
    
    if not gamalta_devices:
        print("\n✗ No Gamalta devices found!")
        print()
        print("Troubleshooting:")
        print("  • Make sure the light is powered on")
        print("  • Close any mobile apps connected to the light")
        print("  • The device may advertise as 'LED' or 'SLED' instead")
        return
    
    print(f"\n✓ Found {len(gamalta_devices)} Gamalta device(s):")
    for d in gamalta_devices:
        print(f"  • {d.name} ({d.address})")
    
    # Connect to first device and list services
    target = gamalta_devices[0]
    print(f"\n{'=' * 40}")
    print(f"Connecting to {target.name}...")
    
    try:
        async with BleakClient(target.address, timeout=10.0) as client:
            print("✓ Connected! Listing services...\n")
            
            for service in client.services:
                print(f"[Service] {service.uuid}")
                print(f"          {service.description}")
                
                for char in service.characteristics:
                    props = ", ".join(char.properties)
                    print(f"  └─ [Char] {char.uuid}")
                    print(f"     Handle: {char.handle}")
                    print(f"     Properties: {props}")
                    
                    if "write" in props or "write-without-response" in props:
                        print(f"     *** WRITABLE ***")
                    if "notify" in props:
                        print(f"     *** NOTIFIES ***")
                
                print("-" * 40)
    
    except Exception as e:
        print(f"✗ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
