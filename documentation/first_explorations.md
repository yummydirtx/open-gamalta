# Gamalta / Generic BLE Aquarium Light Protocol

**Version:** 1.0

**Status:** Reverse Engineered & Verified

**Device:** Gamalta 26W Smart Bluetooth App-Controlled Aquarium Light

**Protocol:** Bluetooth Low Energy (BLE)

## 1. Overview

This document details the reverse-engineered communication protocol for the "Gamalta" brand aquarium light. The device uses a proprietary Bluetooth Low Energy (BLE) protocol. It requires a specific "Handshake" sequence (Login + Time Sync) before it will accept control commands.

## 2. Hardware Connection

The device broadcasts a local name (often `Gamalta`, `LED`, or `SLED`) and enforces a **single-client connection rule**. You must disconnect any mobile apps before attempting to control it via third-party software.

* **Service UUID:** `0000fff0-0000-1000-8000-00805f9b34fb` (Generic Serial Service)
* **Write Characteristic (TX):** `0000fff3-0000-1000-8000-00805f9b34fb` (Handle ~0x0E or 0x0D)
* **Notify Characteristic (RX):** `0000fff4-0000-1000-8000-00805f9b34fb` (Handle ~0x11 or 0x10)

## 3. Protocol Structure

All commands sent to the device follow a fixed byte structure.
**Write Type:** `Write Without Response` (Command) is required. Standard `Write Request` often fails or is ignored.

| Byte | Name | Description |
| --- | --- | --- |
| **0** | **Header** | Always `0xA5`. Marks the start of a packet. |
| **1** | **Sequence** | `0x00`-`0xFF`. An incremental counter. If the device receives a duplicate sequence, it may ignore the command. It is recommended to randomize or increment this per packet. |
| **2** | **Command** | The instruction opcode (e.g., `0x50` for Color, `0x01` for Power). |
| **3** | **Sub-cmd / Length** | Often acts as a data mask or length indicator depending on the command. |
| **4+** | **Payload** | The data arguments (Color values, Time data, etc.). |
| **End** | **Padding** | Zero-padding is often used to reach a fixed length, though not strictly enforced. |

---

## 4. The Handshake (Required)

The device will **ignore** color/power commands until this sequence is completed upon every new connection.

### Step 1: Subscribe

The client must subscribe to the **Notify Characteristic** (`...fff4`).

### Step 2: Login

Sends a hardcoded ASCII password string "123456".

| Header | Seq | Cmd | Len | Data (02 + "123456" in ASCII) |
| --- | --- | --- | --- | --- |
| `A5` | `XX` | `10` | `07` | `02 31 32 33 34 35 36` |

### Step 3: Time Sync

Sets the device's internal clock. The device uses this for sunrise/sunset calculations.

| Header | Seq | Cmd | Len | Year | Month | Day | Hour | Min | Sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `A5` | `XX` | `16` | `07` | `YY` | `MM` | `DD` | `HH` | `mm` | `ss` |

* **YY:** Year minus 2000 (e.g., 2026 = `0x1A`).
* **MM/DD/HH/mm/ss:** Standard integer values.

---

## 5. Control Commands

### Power Control

Turns the light On or Off.

| Header | Seq | Cmd | Len | State | Pad | Pad |
| --- | --- | --- | --- | --- | --- | --- |
| `A5` | `XX` | `01` | `03` | `01` / `02` | `00` | `00` |

* **ON:** `0x01`
* **OFF:** `0x02`

### Direct Color Control (RGB)

Sets the color immediately. This command bypasses internal schedules.

| Header | Seq | Cmd | Mask | Red | Green | Blue | White | Cool | Pad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `A5` | `XX` | `50` | `06` | `00-FF` | `00-FF` | `00-FF` | `00` | `00` | `00` |

* **Mask:** `0x06` appears to indicate RGB mode.
* **W / C:** Warm White and Cool White channels. In testing, these were left as `0x00` with Mask `0x06`. If controlling white channels is required, the mask likely needs to change (e.g., to `0xFF`, `0x1F`, or `0x10`).

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

    def __init__(self, address=None):
        self.address = address
        self.client = None
        self._seq = random.randint(10, 100)

    async def connect(self):
        # 1. Discovery
        if not self.address:
            device = await BleakScanner.find_device_by_filter(
                lambda d, ad: d.name and "Gamalta" in d.name
            )
            if not device: raise Exception("Light not found")
            self.address = device.address

        self.client = BleakClient(self.address)
        await self.client.connect()
        
        # 2. Handshake
        await self.client.start_notify(self.UUID_NOTIFY, lambda s, d: None)
        await self._login()
        await self._sync_time()

    async def _send(self, payload):
        self._seq = (self._seq + 1) % 255
        packet = bytearray([0xA5, self._seq]) + payload
        await self.client.write_gatt_char(self.UUID_WRITE, packet, response=False)
        await asyncio.sleep(0.1) # Debounce

    async def _login(self):
        # Sends '123456'
        await self._send(bytearray([0x10, 0x07, 0x02, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36]))

    async def _sync_time(self):
        now = datetime.datetime.now()
        payload = bytearray([
            0x16, 0x07, now.year - 2000, now.month, now.day, 
            now.hour, now.minute, now.second
        ])
        await self._send(payload)

    async def set_rgb(self, r, g, b):
        # 0x50 = Direct Color Command
        await self._send(bytearray([0x50, 0x06, r, g, b, 0, 0, 0]))

    async def disconnect(self):
        if self.client: await self.client.disconnect()

```

## 7. Known Issues & Troubleshooting

1. **Device Not Found:** Ensure the official app is **force closed** and Bluetooth is toggled OFF on the phone. The light cannot support concurrent connections.
2. **Commands Ignored:** If the sequence number is not incremented (or randomized), the light's replay protection may discard the packet.
3. **No Response:** The handshake must be completed within a few seconds of connecting, or the device may timeout the auth session.