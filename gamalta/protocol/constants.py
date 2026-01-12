"""
Gamalta Protocol Constants

BLE UUIDs, command opcodes, and mode identifiers for the Gamalta smart light protocol.
"""

# =============================================================================
# BLE Service & Characteristic UUIDs
# =============================================================================

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
"""Main BLE UART-like service UUID"""

CHAR_WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
"""Write characteristic for sending commands (Write Without Response)"""

CHAR_NOTIFY_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"
"""Notify characteristic for receiving responses"""

# =============================================================================
# Packet Structure
# =============================================================================

PACKET_HEADER = 0xA5
"""All packets start with this header byte"""

DEFAULT_PASSWORD = "123456"
"""Default device password (ASCII)"""

# =============================================================================
# Command Opcodes
# =============================================================================

CMD_POWER = 0x01
"""Power on/off command"""

CMD_LOGIN = 0x10
"""Authentication/login command"""

CMD_TIME_SYNC = 0x16
"""Time synchronization command"""

CMD_COLOR = 0x50
"""Direct RGBWC color control"""

CMD_BRIGHTNESS = 0x52
"""Master brightness control (0-100%)"""

CMD_MODE = 0x6A
"""Set operating mode/scene"""

CMD_LIGHTNING = 0x76
"""Configure lightning effect schedule"""

# Discovered commands (needs more research)
CMD_STATE_QUERY = 0x03
"""
Query device state - response format:
  [04] [08] [power] [mode] [brightness] [R] [G] [B] [cool_w] [warm_w]
Example response for Fish Blue at 93%:
  04 08 01 03 5D C5 C5 C5 FF 00
  = Power ON, Mode 3 (Fish Blue), 93% brightness, RGB(197,197,197), Cool=255, Warm=0
"""

CMD_SET_NAME = 0x40
"""Set device name - payload [length] [name as ASCII], max ~16 chars
Example: 40 10 636C617564652074657374 = set name to "claude test" """

CMD_QUERY_NAME = 0x42
"""Query device name - response contains name as ASCII (e.g., "gary's domain")"""

CMD_UNKNOWN_09 = 0x09
"""Unknown query command - seen during app init"""

CMD_SCENE_ACTIVATE = 0x72
"""Activates the current scene/mode (seen after mode command)"""

CMD_UNKNOWN_56 = 0x56
"""Unknown - seen with values 01 and 02, possibly pump/accessory control"""

# Scene/Schedule Commands
CMD_SCENE_LIST = 0x64
"""Query scene list - payload [01] [slot], returns scene info"""

CMD_SCENE_META = 0x6E
"""Query scene metadata - payload [01] [scene_id]"""

CMD_SCENE_NAME = 0x68
"""Query scene name - payload [01] [scene_id], response is ASCII name (e.g., "Basic", "Pro")"""

CMD_SCENE_POINTS = 0x70
"""Query number of points in a scene's 24h schedule - payload [01] [scene_id]"""

CMD_QUERY_SCHEDULE_POINT = 0x62
"""Query schedule point data - payload [02] [scene_id] [point_index 1-5]
Response: time ranges and RGBWC values for each segment of the 24h cycle"""

CMD_START_SCENE_EDIT = 0x74
"""Start editing a scene - payload [01] [scene_id]
Must be called before writing schedule points"""

CMD_WRITE_SCHEDULE_POINT = 0x60
"""Write schedule point data - payload format (12 bytes total):
  [scene_id] [point_idx] [start_h] [start_m] [end_h] [end_m] [R] [G] [B] [W] [C] [brightness]
  
Example for 5AM node (red color):
  0B 01 14 00 05 00 FF 00 00 00 00 64
  = Scene 0x0B, Point 1, 20:00-05:00, RGB(255,0,0), W=0, C=0, 100% brightness
  
Point 0xFF is used as end marker to finalize the scene."""

CMD_WRITE_SCENE_META = 0x6C
"""Write scene metadata - payload includes sunrise/sunset times
Format: [scene_id] [02] [sunrise bytes] [02] [sunset bytes]
Example: 0B 02 B6 9C 9C 02 B6 9C 9C"""

# =============================================================================
# Power States
# =============================================================================

POWER_ON = 0x01
POWER_OFF = 0x02

# =============================================================================
# Operating Modes
# =============================================================================

MODE_MANUAL = 0x01
"""Static color mode - stays on last set color"""

MODE_CORAL_REEF = 0x02
"""24h cycle - High blue, high cool white, 50% brightness"""

MODE_FISH_BLUE = 0x03
"""24h cycle - Deep blue focus, 26% brightness"""

MODE_WATERWEED = 0x04
"""24h cycle - Plant growth mode"""

# =============================================================================
# Lightning Effect Constants
# =============================================================================

LIGHTNING_MASK = 0x07
"""Sub-command/mask for lightning configuration"""

LIGHTNING_PREVIEW = 0xFE
"""Special intensity value to trigger preview mode"""

# =============================================================================
# Day Bitmask (for lightning schedule)
# =============================================================================

DAY_MONDAY = 0x01
DAY_TUESDAY = 0x02
DAY_WEDNESDAY = 0x04
DAY_THURSDAY = 0x08
DAY_FRIDAY = 0x10
DAY_SATURDAY = 0x20
DAY_SUNDAY = 0x40
DAY_ENABLED = 0x80  # Master enable bit

DAYS_ALL = 0x7F  # All days selected (without enable bit)
DAYS_WEEKDAYS = DAY_MONDAY | DAY_TUESDAY | DAY_WEDNESDAY | DAY_THURSDAY | DAY_FRIDAY
DAYS_WEEKEND = DAY_SATURDAY | DAY_SUNDAY
