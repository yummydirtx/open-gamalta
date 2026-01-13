#!/usr/bin/env python3
"""
Scene Schedule Query Test

Query the Fish Blue scene's schedule points to understand the 24h color data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gamalta import GamaltaClient
from gamalta.protocol.packet import PacketBuilder
from gamalta.protocol.constants import (
    CMD_SCENE_POINTS, CMD_QUERY_SCHEDULE_POINT, 
    CMD_SCENE_NAME, CMD_SCENE_META,
    MODE_FISH_BLUE
)

# Fish Blue scene ID
FISH_BLUE = 0x03


async def main():
    print("Scene Schedule Query Test")
    print("=" * 50)
    print(f"Target Scene: Fish Blue (0x{FISH_BLUE:02X})")
    print()
    
    client = GamaltaClient()
    responses = []
    
    def capture_response(data: bytes):
        """Capture all responses for analysis."""
        responses.append(data)
        hex_str = data.hex(" ")
        print(f"  RX: {hex_str}")
    
    try:
        print("Connecting...")
        await client.connect()
        print("✓ Connected!")
        print()
        
        # Set up response capture
        client.on_notify(capture_response)
        
        # Query scene name
        print(f"1. Querying scene name (0x{CMD_SCENE_NAME:02X})...")
        payload = bytes([CMD_SCENE_NAME, 0x01, FISH_BLUE])
        await client._send(payload)
        await asyncio.sleep(0.3)
        print()
        
        # Query scene metadata
        print(f"2. Querying scene metadata (0x{CMD_SCENE_META:02X})...")
        payload = bytes([CMD_SCENE_META, 0x01, FISH_BLUE])
        await client._send(payload)
        await asyncio.sleep(0.3)
        print()
        
        # Query number of schedule points
        print(f"3. Querying schedule point count (0x{CMD_SCENE_POINTS:02X})...")
        payload = bytes([CMD_SCENE_POINTS, 0x01, FISH_BLUE])
        await client._send(payload)
        await asyncio.sleep(0.3)
        print()
        
        # Query each schedule point (try 1-10 to see what we get)
        print(f"4. Querying schedule points (0x{CMD_QUERY_SCHEDULE_POINT:02X})...")
        for point_idx in range(1, 11):
            print(f"   Point {point_idx}:")
            payload = bytes([CMD_QUERY_SCHEDULE_POINT, 0x02, FISH_BLUE, point_idx])
            await client._send(payload)
            await asyncio.sleep(0.3)
        print()
        
        # Summary
        print("=" * 50)
        print("Raw Response Summary:")
        print("=" * 50)
        for i, resp in enumerate(responses):
            cmd = resp[2] if len(resp) > 2 else 0
            print(f"Response {i+1}: cmd=0x{cmd:02X} data={resp.hex(' ')}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()
        print("\nDisconnected.")


if __name__ == "__main__":
    asyncio.run(main())
