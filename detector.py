import asyncio
from bleak import BleakScanner, BleakClient

async def run():
    print("Scanning for 'Gamalta' specifically...")
    
    # 1. SCAN FOR DEVICES
    devices = await BleakScanner.discover(timeout=5.0)
    
    target_device = None
    
    # Debug: Print everything we found so you can see if it's hiding
    for d in devices:
        name = d.name or "Unknown"
        print(f" - Found: {name} ({d.address})")
        
        # STRICT FILTER: Only match if "Gamalta" is in the name
        if "Gamalta" in name:
            target_device = d

    if not target_device:
        print("\n❌ Could not find a device named 'Gamalta'.")
        print("Make sure the light is plugged in and NOT connected to your phone.")
        return

    print(f"\n✅ Found Target: {target_device.name} ({target_device.address})")
    print("Attempting connection...")

    # 2. CONNECT AND LIST UUIDS
    try:
        async with BleakClient(target_device.address, timeout=10.0) as client:
            print("Connected! Listing Services & Characteristics...\n")
            
            for service in client.services:
                print(f"[Service] {service.uuid} ({service.description})")
                for char in service.characteristics:
                    props = ",".join(char.properties)
                    print(f"  └─ [Char] {char.uuid}")
                    print(f"     Properties: {props}")
                    print(f"     Handle: {char.handle}")
                    
                    if "write" in props or "write-without-response" in props:
                        print(f"     *** WRITABLE! UUID: {char.uuid} ***")
                print("-" * 40)
                
    except Exception as e:
        print(f"Connection failed: {e}")
        print("TROUBLESHOOTING: Turn your phone's Bluetooth OFF. The light can only talk to one device at a time.")

loop = asyncio.new_event_loop()
loop.run_until_complete(run())