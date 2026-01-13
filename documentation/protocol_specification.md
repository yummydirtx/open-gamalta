# Gamalta BLE Protocol Specification

**Version:** 2.0  
**Status:** Reverse Engineered & Verified  
**Device:** Gamalta 26W Smart Bluetooth App-Controlled Aquarium Light  
**Last Updated:** 2026-01-12

---

## 1. Connection

### BLE Characteristics

| UUID | Handle | Type | Description |
|------|--------|------|-------------|
| `0000fff0-...` | - | Service | Main UART-like service |
| `0000fff3-...` | 0x000E | Write | Command TX (Write Without Response) |
| `0000fff4-...` | 0x0011 | Notify | Response RX |

### Connection Rules
- Device enforces **single-client connection**
- Must disconnect mobile apps before third-party control
- MTU negotiation: requests 185, device responds with 23

---

## 2. Packet Structure

All packets follow this format:

```
[Header] [Sequence] [Command] [Length/Mask] [Payload...]
   A5       XX         XX          XX         ...
```

| Byte | Name | Description |
|------|------|-------------|
| 0 | Header | Always `0xA5` |
| 1 | Sequence | `0x00-0xFF`, increment per packet (replay protection) |
| 2 | Command | Opcode (see command table) |
| 3 | Length/Mask | Varies by command |
| 4+ | Payload | Command-specific data |

### Response Format
Responses use `command + 1` as the response opcode. Example: `0x50` → `0x51`.

---

## 3. Handshake (Required)

The device ignores all commands until this sequence completes.

### Step 1: Subscribe to Notifications
Enable notifications on `0xFFF4` (handle 0x0012).

### Step 2: Login
Send password "123456" as ASCII.

```
A5 [Seq] 10 07 02 31 32 33 34 35 36
              │  │  │  └─ "123456" in ASCII
              │  │  └─ Unknown flag
              │  └─ Length (7 bytes)
              └─ CMD_LOGIN
```

### Step 3: Time Sync
Set the device's internal clock.

```
A5 [Seq] 16 07 [YY] [MM] [DD] [WD] [HH] [mm] [ss]
              │    │    │    │    │    │    └─ Second
              │    │    │    │    │    └─ Minute
              │    │    │    │    └─ Hour
              │    │    │    └─ Weekday (1=Mon ... 7=Sun)
              │    │    └─ Day
              │    └─ Month
              └─ Year = actual year - 2000
```

### Step 4: Stabilization (Critical)
After Time Sync and/or Scene Activation, the official app sends a specific sequence of queries. Omitting these may cause the device to reset its state (0 brightness/color) or disconnect.

Recommended sequence:
1. `CMD_STATE_QUERY` (0x03)
2. `CMD_LIGHTNING_QUERY` (0x77 slot 1? actually just command 0x76 read?) -> Actually command `0x76` is set. Query is likely `0x77`? No, app sends 0x76 07 ... as query? Need to check.
   - *Correction*: Official app just sends state query, lightning query (likely `77 01 00`?), and timer queries (`56 01 01`, `56 01 02`).

Minimal proven sequence:
- `CMD_STATE_QUERY` (0x03 00)
- `CMD_TIMER_QUERY` x2 (0x56 01 01, 0x56 01 02)

---

## 4. Command Reference

### Power Control (`0x01`)

```
A5 [Seq] 01 03 [State] 00 00
               │
               ├─ 01 = ON
               └─ 02 = OFF
```

### Color Control (`0x50`)

Sets RGBWC color directly. **Order is R G B C W** (Cool before Warm).

```
A5 [Seq] 50 06 [R] [G] [B] [C] [W] [Flag]
              │   │   │   │   │   │
              │   │   │   │   │   └─ 01=apply, 00=preview
              │   │   │   │   └─ Warm White (0-255)
              │   │   │   └─ Cool White (0-255)
              │   │   └─ Blue (0-255)
              │   └─ Green (0-255)
              └─ Red (0-255)
```

### Brightness (`0x52`)

```
A5 [Seq] 52 01 [Percent]
               └─ 0x00-0x64 (0-100%)
```

### Mode Selection (`0x6A`)

```
A5 [Seq] 6A 01 [Mode]
```

| Mode | Name |
|------|------|
| `0x00` | Manual (static color) |
| `0x01` | Intelligent SunSync |
| `0x02` | Coral Reef |
| `0x03` | Fish Blue |
| `0x04` | Waterweed |
| `0x0B` | Custom Basic |
| `0x0C` | Custom Pro |

### Scene Activate (`0x72`)

Activates the current mode. Called after `0x6A`.

```
A5 [Seq] 72 01 00
```

Response includes active scene ID.

---

## 5. State Query (`0x03`)

Query current device state.

```
Request:  A5 [Seq] 03 00
Response: A5 [Seq] 04 08 [Power] [Mode] [Bright] [R] [G] [B] [C] [W]
```

> **Note:** Colors are **live interpolated** values based on current time, not static scene definitions.

Example response `04 08 01 0C 64 FF EE 11 6E 6E`:
- Power: ON
- Mode: 0x0C (Pro)
- Brightness: 100%
- RGB(255, 238, 17), Cool=110, Warm=110

---

## 6. Device Name

### Query (`0x42`)
```
A5 [Seq] 42 01 00
Response: 43 10 [name as ASCII, null-padded]
```

### Set (`0x40`)
```
A5 [Seq] 40 10 [name as ASCII, up to 16 chars]
```

---

## 7. Timer Control

Two timer slots work together (on/off pair).

### Set Timer (`0x54`)

```
A5 [Seq] 54 07 [Slot] [Enable] FF [Hour] [??] [??] [Action]
               │      │           │            │
               │      │           │            ├─ 01 = turn ON
               │      │           │            └─ 00 = turn OFF
               │      │           └─ Time bytes (encoding TBD)
               │      └─ 01 = enabled
               └─ 01 or 02
```

### Query Timer (`0x56`)
```
A5 [Seq] 56 01 [Slot]
Response: 57 08 [Slot] [Enabled] [Time data...]
```

---

## 8. Custom Scene Editing

### Scene Edit Sequence

1. **Start Edit** (`0x74`): `74 01 [scene_id]`
2. **Write Points** (`0x60`): Write 5 schedule points
3. **Write Metadata** (`0x6C`): Sunrise/sunset params
4. **Finalize** (`0x60`): Point `0xFF` as end marker
5. **Activate**: Color → Brightness → Mode → Scene Activate

### Schedule Point Format (`0x60`)

```
A5 [Seq] 60 0C [Scene] [Point] [StartH] [StartM] [EndH] [EndM] [R] [G] [B] [C] [W] [Bright]
```

| Field | Description |
|-------|-------------|
| Scene | Scene ID (0x0B or 0x0C) |
| Point | Point index 1-5, or 0xFF to finalize |
| StartH/M | Start time (hour, minute) |
| EndH/M | End time of this segment |
| R G B C W | Color values (Cool before Warm) |
| Bright | Brightness percentage (0x64 = 100%) |

Example 5-point schedule for scene 0x0C (Pro):

| Point | Time Range | Color |
|-------|------------|-------|
| 1 | 20:00 → 05:00 | Night/Dawn |
| 2 | 05:00 → Sunrise | Sunrise transition |
| 3 | Sunrise → 12:00 | Midday |
| 4 | 12:00 → Sunset | Afternoon |
| 5 | Sunset → 20:00 | Dusk |

### Scene Metadata (`0x6C`)

```
A5 [Seq] 6C 10 [Scene] 02 [Sunrise bytes] 02 [Sunset bytes]
```

Basic scene: `B6 9C 9C`  
Pro scene: `D5 AA CA`

Exact encoding of sunrise/sunset times TBD.

### Query Scene Data

| Command | Purpose |
|---------|---------|
| `0x64 01 [slot]` | Query scene list |
| `0x6E 01 [id]` | Query scene metadata |
| `0x68 01 [id]` | Query scene name (ASCII) |
| `0x70 01 [id]` | Query point count |
| `0x62 02 [id] [point]` | Query schedule point |

---

## 9. Lightning Effect (`0x76`)

```
A5 [Seq] 76 07 [Intensity] [Freq] [StartH] [StartM] [EndH] [EndM] [Days]
               │           │      │                 │              │
               │           │      └─────── Schedule window ────────┘
               │           └─ Flashes per interval (0-10)
               └─ 0-100% or 0xFE for preview
```

### Days Bitmask
| Bit | Day |
|-----|-----|
| 0 | Monday |
| 1 | Tuesday |
| 2 | Wednesday |
| 3 | Thursday |
| 4 | Friday |
| 5 | Saturday |
| 6 | Sunday |
| 7 | **Master Enable** |

Example: `0xFF` = enabled every day, `0x7F` = disabled (master off)

---

## 10. Other Commands

| Cmd | Purpose | Status |
|-----|---------|--------|
| `0x09` | Query device ID/serial | Returns 2-byte ID |
| `0x64` | Query scene slot list | Complete |
| `0x6E` | Query scene metadata | Complete |
| `0x68` | Query scene name | Complete |
| `0x70` | Query scene point count | Complete |

---

## 11. Response Codes

Responses typically echo the sequence number and use `cmd + 1`:

| Request | Response |
|---------|----------|
| `0x10` (login) | `0x11` |
| `0x50` (color) | `0x51` |
| `0x6A` (mode) | `0x6B` |

Success is indicated by the response arriving; no explicit error codes observed.

---

## Appendix A: Quick Reference

### Handshake
```python
login = [0xA5, seq, 0x10, 0x07, 0x02, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36]
time_sync = [0xA5, seq, 0x16, 0x07, year-2000, month, day, weekday, hour, min, sec]
```

### Common Commands
```python
power_on   = [0xA5, seq, 0x01, 0x03, 0x01, 0x00, 0x00]
power_off  = [0xA5, seq, 0x01, 0x03, 0x02, 0x00, 0x00]
color      = [0xA5, seq, 0x50, 0x06, R, G, B, C, W, 0x01]
brightness = [0xA5, seq, 0x52, 0x01, percent]
mode       = [0xA5, seq, 0x6A, 0x01, mode_id]
```

---

## Appendix B: Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01 | Initial protocol documentation |
| 2.0 | 2026-01-12 | Added scene editing, timers, R G B C W order confirmation, all mode IDs |
