#!/usr/bin/env python3
"""
Lightning Effect Demo

Demonstrates the lightning storm effect configuration and preview.
"""

import asyncio
import sys
from pathlib import Path
from datetime import time

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient, LightningConfig, Day


async def main():
    print("Gamalta Lightning Effect Demo")
    print("=" * 40)
    
    async with GamaltaClient() as light:
        print("✓ Connected!")
        
        # Make sure light is on
        await light.power_on()
        await light.set_brightness(80)
        
        # Set a dark blue color for atmosphere
        print("\n1. Setting moody blue atmosphere...")
        await light.set_color(0, 20, 80)
        await asyncio.sleep(1)
        
        # Trigger a single lightning preview
        print("2. Triggering lightning flash preview...")
        await light.preview_lightning()
        await asyncio.sleep(2)
        
        # Trigger a few more flashes
        print("3. More flashes...")
        for i in range(3):
            await asyncio.sleep(1)
            await light.preview_lightning()
        
        await asyncio.sleep(2)
        
        # Configure an actual lightning schedule (optional)
        print("\n4. Configuring a lightning schedule...")
        print("   (Will run from 18:00-22:00 on weekdays)")
        
        schedule = LightningConfig(
            intensity=75,       # 75% intensity
            frequency=5,        # Medium frequency
            start_time=time(18, 0),   # 6:00 PM
            end_time=time(22, 0),     # 10:00 PM
            days=Day.MONDAY | Day.TUESDAY | Day.WEDNESDAY | Day.THURSDAY | Day.FRIDAY,
            enabled=True
        )
        
        await light.configure_lightning(schedule)
        print("   ✓ Schedule configured!")
        print()
        print("   Note: Lightning will only trigger during the scheduled window")
        print("         when the device's internal clock matches the time range.")
        
        # Reset to normal
        print("\n5. Returning to normal color...")
        await light.set_color(255, 200, 150)
        
        print("\n✓ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
