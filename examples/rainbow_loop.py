#!/usr/bin/env python3
"""
Rainbow Loop Demo

Connects to a Gamalta light, switches to manual mode, and performs
a smooth rainbow color cycle.
"""

import asyncio
import colorsys
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient, Mode, Color


async def main():
    print("Gamalta Rainbow Loop Demo")
    print("=" * 40)
    print("Press Ctrl+C to stop.")
    
    print("Scanning for device...")
    # Using context manager for automatic connect/disconnect
    async with GamaltaClient() as light:
        print("✓ Connected!")
        
        # Explicitly switch to manual mode as requested
        print("1. Switching to Manual mode...")
        await light.set_mode(Mode.MANUAL)
        await asyncio.sleep(0.5)
        
        # Turn on if off
        print("2. Ensuring power is ON...")
        await light.power_on()
        await asyncio.sleep(0.5)
        
        print("3. Starting rainbow loop...")
        
        hue = 0.0
        # Speed factor: how much to increment hue per step
        # 0.01 per 0.1s = ~10 seconds per full cycle
        hue_step = 0.05 
        
        try:
            while True:
                # Calculate RGB from HSV (Hue, Saturation=1.0, Value=1.0)
                # colorsys returns 0-1 floats, we need 0-255 integers
                r_float, g_float, b_float = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                
                r = int(r_float * 255)
                g = int(g_float * 255)
                b = int(b_float * 255)
                
                # Update light color
                # We disable set_manual_mode=True to avoid sending extra mode commands
                # since we are already in manual mode.
                await light.set_color(r, g, b, set_manual_mode=False)
                
                # Increment hue and wrap around
                hue += hue_step
                if hue > 1.0:
                    hue -= 1.0
                
                # Small delay for smooth transition without flooding the bus
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            print("\nStopped.")
        except KeyboardInterrupt:
            print("\nStopped by user.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
