import asyncio
from bleak import BleakScanner, BleakClient

# The handle you identified in the logs (0x000E = 14)
# The script will look for the UUID associated with this handle.
TARGET_HANDLE = 14

async def set_color(client, uuid, r, g, b, w, c):
    """
    Sets the color of the light.
    R, G, B, W, C should be integers between 0 and 255.
    """
    # Structure: A5 [Seq] 76 [Mask] [R] [G] [B] [W] [C] [Pad] [Pad]
    # We use a static sequence (0x11) and Mask (0x07) for now.
    # Note: If W/C don't work, we might need to change the Mask to 0x0F or similar.
    
    command = bytearray([
        0xA5,       # Header
        0x12,       # Sequence (arbitrary)
        0x76,       # Command: Set Color
        0x07,       # Mode/Mask (Likely RGB active)
        r, g, b,    # RGB Channels
        w, c,       # White/Cool Channels
        0x00, 0x00  # Padding
    ])
    
    print(f"Sending Color Command: {command.hex().upper()}")
    await client.write_gatt_char(uuid, command, response=True)

async def run():
    print("Scanning for Gamalta/Generic light...")
    devices = await BleakScanner.discover()
    
    target_device = None
    
    # 1. FIND THE DEVICE
    for d in devices:
        # If your device shows up as something else, change this string!
        # Common names: "Gamalta", "QHM", "SLED", "LED", "IS-RGB"
        if d.name and ("Gamalta" in d.name or "LED" in d.name):
            print(f"Found match: {d.name} - {d.address}")
            target_device = d
            break

    if not target_device:
        print("Light not found in scan. List of devices found:")
        for d in devices:
            print(f" - {d.name or 'Unknown'} ({d.address})")
        return

    # 2. CONNECT AND MAP HANDLE TO UUID
    print(f"Connecting to {target_device.name}...")
    async with BleakClient(target_device.address) as client:
        print("Connected!")
        
        target_uuid = None
        
        # Iterate through services to find the UUID for handle 14
        for service in client.services:
            for char in service.characteristics:
                if char.handle == TARGET_HANDLE:
                    target_uuid = char.uuid
                    break
        
        if not target_uuid:
            print(f"Could not find a characteristic at handle {TARGET_HANDLE} (0x0E).")
            # Fallback: Sometimes the handle shifts. We can try to guess a common UUID here
            # or you can list all characteristics to debug.
            return
        
        print(f"Mapped Handle {TARGET_HANDLE} to UUID: {target_uuid}")

        # 3. SEND COMMANDS
        
        # Example 1: Set to Full RGB White (Your Request)
        # R=255, G=255, B=255, W=0, C=0
        await set_color(client, target_uuid, 255, 255, 255, 0, 0)
        
        # Wait 2 seconds so you can see the change
        await asyncio.sleep(2)

        # Example 2: Turn Off (Using the command we found earlier)
        # A5 13 01 03 02 00 00
        print("Turning OFF...")
        off_cmd = bytearray([0xA5, 0x13, 0x01, 0x03, 0x02, 0x00, 0x00])
        await client.write_gatt_char(target_uuid, off_cmd, response=True)

loop = asyncio.new_event_loop()
loop.run_until_complete(run())