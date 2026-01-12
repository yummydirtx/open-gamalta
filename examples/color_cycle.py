#!/usr/bin/env python3
"""
Color Cycle Example

Cycles through colors continuously. Press Ctrl+C to stop.

Migrated from the original controller.py.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient


async def main():
    print("Gamalta Color Cycle Demo")
    print("=" * 40)
    print("Press Ctrl+C to stop\n")
    
    colors = [
        (255, 0, 0, "Red"),
        (255, 127, 0, "Orange"),
        (255, 255, 0, "Yellow"),
        (0, 255, 0, "Green"),
        (0, 255, 255, "Cyan"),
        (0, 0, 255, "Blue"),
        (127, 0, 255, "Purple"),
        (255, 0, 255, "Magenta"),
    ]
    
    async with GamaltaClient() as light:
        print("✓ Connected!")
        
        # Ensure light is on and bright
        await light.power_on()
        await light.set_brightness(100)
        
        print("\nCycling colors...")
        try:
            cycle = 0
            while True:
                cycle += 1
                print(f"\n--- Cycle {cycle} ---")
                
                for r, g, b, name in colors:
                    print(f"  {name}")
                    await light.set_color(r, g, b)
                    await asyncio.sleep(1.5)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            # Turn off before exit
            await light.set_color(0, 0, 0)
            print("Light turned off")


if __name__ == "__main__":
    asyncio.run(main())
