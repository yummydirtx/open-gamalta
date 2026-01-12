#!/usr/bin/env python3
"""
Basic Control Example

Simple demonstration of connecting and controlling a Gamalta light.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient, Mode


async def main():
    print("Gamalta Basic Control Example")
    print("=" * 40)
    
    # Using context manager for automatic connect/disconnect
    async with GamaltaClient() as light:
        print("✓ Connected!")
        
        # Power on
        print("\n1. Turning light ON...")
        await light.power_on()
        await asyncio.sleep(1)
        
        # Set brightness
        print("2. Setting brightness to 75%...")
        await light.set_brightness(75)
        await asyncio.sleep(1)
        
        # Set a warm color
        print("3. Setting warm orange color...")
        await light.set_color(255, 100, 30)
        await asyncio.sleep(2)
        
        # Try a mode
        print("4. Switching to Coral Reef mode...")
        await light.set_mode(Mode.CORAL_REEF)
        await asyncio.sleep(2)
        
        # Back to manual with blue
        print("5. Back to manual with blue color...")
        await light.set_color(0, 50, 255)
        await asyncio.sleep(2)
        
        print("\n✓ Demo complete!")
        print("  (Light left on - run cli.py to turn off)")


if __name__ == "__main__":
    asyncio.run(main())
