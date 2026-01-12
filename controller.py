import asyncio
import random
import datetime
from bleak import BleakScanner, BleakClient

# --- CONFIGURATION ---
DEVICE_NAME = "Gamalta"
WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"
# ---------------------

def get_time_packet(seq):
    """Generates the time sync packet (Command 0x16) based on current system time."""
    now = datetime.datetime.now()
    # Year is just the last two digits (e.g. 2026 -> 26)
    year = now.year - 2000
    
    packet = bytearray([
        0xA5,           # Header
        seq,            # Sequence
        0x16,           # Command: Set Time
        0x07,           # Length/Sub-cmd
        year,           # YY
        now.month,      # MM
        now.day,        # DD
        now.hour,       # HH
        now.minute,     # MM
        now.second      # SS
    ])
    return packet

async def run():
    print(f"Scanning for '{DEVICE_NAME}'...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and DEVICE_NAME in d.name
    )

    if not device:
        print(f"❌ '{DEVICE_NAME}' not found.")
        return

    print(f"✅ Found {device.name}. Connecting...")
    
    async with BleakClient(device.address) as client:
        print("Connected!")
        
        # 1. SUBSCRIBE (Crucial)
        await client.start_notify(NOTIFY_UUID, lambda s, d: print(f" < RCV: {d.hex().upper()}"))
        print("Subscribed to notifications.")
        await asyncio.sleep(0.5)

        # 2. HANDSHAKE / LOGIN (Command 0x10)
        # Value: 02 followed by ASCII "123456"
        print("Sending HANDSHAKE (123456)...")
        seq = random.randint(10, 50)
        handshake = bytearray([0xA5, seq, 0x10, 0x07, 0x02, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36])
        await client.write_gatt_char(WRITE_UUID, handshake, response=False)
        await asyncio.sleep(0.5)

        # 3. TIME SYNC (Command 0x16)
        print("Sending TIME SYNC...")
        seq += 1
        time_packet = get_time_packet(seq)
        print(f" > Time Packet: {time_packet.hex().upper()}")
        await client.write_gatt_char(WRITE_UUID, time_packet, response=False)
        await asyncio.sleep(0.5)

        # 4. COLOR TEST (Command 0x50)
        print("\n--- ATTEMPTING CONTROL ---")
        
        # Turn ON first (just in case)
        seq += 1
        power_on = bytearray([0xA5, seq, 0x01, 0x03, 0x01, 0x00, 0x00])
        await client.write_gatt_char(WRITE_UUID, power_on, response=False)
        await asyncio.sleep(1)

        # Cycle Colors
        colors = [
            (255, 0, 0, "RED"),
            (0, 255, 0, "GREEN"),
            (0, 0, 255, "BLUE"),
            (0, 0, 0, "OFF")
        ]
        
        for r, g, b, name in colors:
            seq += 1
            # Command 0x50 (Direct Color), Mask 0x06 (RGB)
            cmd = bytearray([0xA5, seq, 0x50, 0x06, r, g, b, 0x00, 0x00, 0x00])
            print(f"Sending {name}: {cmd.hex().upper()}")
            await client.write_gatt_char(WRITE_UUID, cmd, response=False)
            await asyncio.sleep(2)

        print("Done.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())