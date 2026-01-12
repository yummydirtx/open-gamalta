# Gamalta / Generic BLE Aquarium Light Protocol

**Version:** 1.1 (Scene & Brightness Update)

**Status:** Reverse Engineered & Verified

**Device:** Gamalta 26W Smart Bluetooth App-Controlled Aquarium Light

**Protocol:** Bluetooth Low Energy (BLE)

## 1. Overview

This document details the reverse-engineered communication protocol for the "Gamalta" brand aquarium light. The device uses a proprietary Bluetooth Low Energy (BLE) protocol. It requires a specific **Handshake** (Login + Time Sync) to unlock control.

**Key Findings (v1.1):**

* The "Scenes" are firmware-based 24-hour cycles, not just app-side automations.
* Scenes rely heavily on the **Time Sync** command to function correctly.
* Brightness is controlled via a separate command (`0x52`) from color (`0x50`).

## 2. Hardware Connection

* **Service UUID:** `0000fff0-0000-1000-8000-00805f9b34fb`
* **Write Characteristic (TX):** `0000fff3-0000-1000-8000-00805f9b34fb`
* **Notify Characteristic (RX):** `0000fff4-0000-1000-8000-00805f9b34fb`

*Note: The device enforces a single-connection rule. Disconnect other apps before using.*

## 3. The Handshake (Required)

The device ignores all commands until this sequence is completed.

### Step 1: Login

Sends password "123456".
`A5 [Seq] 10 07 02 31 32 33 34 35 36`

### Step 2: Time Sync

Sets the device's internal clock. **Crucial for Scenes.**
`A5 [Seq] 16 07 [YY] [MM] [DD] [HH] [mm] [ss]`
*(Year is YY - 2000)*

---

## 4. Control Commands

All packets start with Header `0xA5` and a Sequence Byte.

### A. Direct Color Control (RGBWC)

Sets the color immediately. This usually forces the device into "Manual Mode" internally, but sending the Explicit Mode command (`0x6A` -> `0x01`) afterwards is recommended.

| Header | Seq | Cmd | Mask | Red | Green | Blue | Warm W | Cool W | Flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `A5` | `XX` | `50` | `06` | `00-FF` | `00-FF` | `00-FF` | `00-FF` | `00-FF` | `01` |

* **Mask `0x06**`: Active channels (RGB+W+C).
* **Flag `0x01**`: Likely "Apply Immediately" or "Fade".

### B. Master Brightness

Sets the global brightness of the light (0-100%).

| Header | Seq | Cmd | Len | Level (%) |
| --- | --- | --- | --- | --- |
| `A5` | `XX` | `52` | `01` | `00-64` (Hex) |

* **Level:** `0x00` (0%) to `0x64` (100%).

### C. Power Control

| Header | Seq | Cmd | Len | State | Pad | Pad |
| --- | --- | --- | --- | --- | --- | --- |
| `A5` | `XX` | `01` | `03` | `01` / `02` | `00` | `00` |

* **ON:** `0x01`
* **OFF:** `0x02`

---

## 5. Scenes & Modes

The device has internal "Modes" that trigger 24-hour lighting cycles based on the internal clock.

### Set Mode Command (`0x6A`)

Activates a specific behavior.

| Header | Seq | Cmd | Len | Mode ID |
| --- | --- | --- | --- | --- |
| `A5` | `XX` | `6A` | `01` | `ID` |

### Known Mode IDs

| ID | Name | Description |
| --- | --- | --- |
| **`0x01`** | **Manual** | Static color. Stays on the last set `0x50` color command. |
| **`0x02`** | **Coral Reef** | 24h Cycle. High Blue, High Cool White, Medium brightness (50%). |
| **`0x03`** | **Fish Blue** | 24h Cycle. Deep Blue focus, Low brightness (26%). |
| **`0x04`+** | *Unknown* | Likely other presets (Sunrise, Daylight, etc.). |

**Implementation Note:** When activating a scene from the OFF state, the official app sends:

1. **Color Command (`0x50`):** Sets the LEDs to what the scene *should* look like right now (preventing visual lag).
2. **Brightness Command (`0x52`):** Sets the scene's default brightness.
3. **Mode Command (`0x6A`):** Engages the firmware logic to take over from there.
4. **Scene Activate (`0x72`):** Payload `01 00` - possibly confirms scene activation.
5. **State Query (`0x03`):** Payload `00` - queries current device state.

> **Note:** There is NO explicit power-on command (`0x01`) in this sequence! Setting the mode appears to implicitly turn the light on.

### Additional Commands Observed

| Cmd | Payload | Notes |
|-----|---------|-------|
| `0x72` | `01 00` | Seen after mode command, possibly "activate scene" |
| `0x03` | `00` | State query - response contains mode, brightness, color |
| `0x76` | `07 FF 00...` | Lightning with intensity 0xFF (disabled?) |
| `0x56` | `01 01`, `01 02` | Unknown - possibly pump/accessory control |

---

## 6. Reference Implementation (Python)

*Dependencies:* `bleak`

```python
import asyncio
import random
import datetime
from bleak import BleakScanner, BleakClient

class GamaltaLight:
    UUID_WRITE  = "0000fff3-0000-1000-8000-00805f9b34fb"
    UUID_NOTIFY = "0000fff4-0000-1000-8000-00805f9b34fb"
    
    MODE_MANUAL     = 0x01
    MODE_CORAL_REEF = 0x02
    MODE_FISH_BLUE  = 0x03

    def __init__(self, address=None):
        self.address = address
        self.client = None
        self._seq = random.randint(10, 100)

    async def connect(self):
        if not self.address:
            # Simple scan
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: d.name and "Gamalta" in d.name
            )
            self.address = device.address
        
        self.client = BleakClient(self.address)
        await self.client.connect()
        await self.client.start_notify(self.UUID_NOTIFY, lambda s, d: None)
        await self._handshake()

    async def _send(self, payload):
        self._seq = (self._seq + 1) % 255
        packet = bytearray([0xA5, self._seq]) + payload
        await self.client.write_gatt_char(self.UUID_WRITE, packet, response=False)
        await asyncio.sleep(0.1)

    async def _handshake(self):
        # Login
        await self._send(bytearray([0x10, 0x07, 0x02, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36]))
        # Time Sync
        now = datetime.datetime.now()
        await self._send(bytearray([
            0x16, 0x07, now.year - 2000, now.month, now.day, 
            now.hour, now.minute, now.second
        ]))

    async def set_color(self, r, g, b, w=0, c=0):
        # Sets color and enforces manual mode
        await self._send(bytearray([0x50, 0x06, r, g, b, w, c, 0x01]))
        await self.set_mode(self.MODE_MANUAL)

    async def set_brightness(self, percent):
        # 0-100%
        await self._send(bytearray([0x52, 0x01, percent]))

    async def set_mode(self, mode):
        # 0x01=Manual, 0x02=Coral, 0x03=FishBlue
        await self._send(bytearray([0x6A, 0x01, mode]))

```
