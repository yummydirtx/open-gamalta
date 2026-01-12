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
  [04] [08] [power] [mode] [brightness] [R] [G] [B] [C] [W]
  
NOTE: Colors are LIVE INTERPOLATED values based on current time of day,
not the static scene definition! For a 24h scene, these will change throughout the day.

Example response for Pro scene at ~12:16pm:
  04 08 01 0C 64 FF EE 11 6E 6E
  = Power ON, Mode 0x0C (Pro), 100%, RGB(255,238,17), Cool=110, Warm=110
"""

CMD_SET_NAME = 0x40
"""Set device name - payload [length] [name as ASCII], max ~16 chars
Example: 40 10 636C617564652074657374 = set name to "claude test" """

CMD_QUERY_NAME = 0x42
"""Query device name - response contains name as ASCII (e.g., "gary's domain")"""

CMD_UNKNOWN_09 = 0x09
"""Query device ID/serial - response is 2 bytes (e.g., 0x7C65)
Not the firmware version - that may come from BLE Device Information Service"""

CMD_SCENE_ACTIVATE = 0x72
"""Activates the current scene/mode (seen after mode command)
Response includes the active scene ID"""

CMD_TIMER_QUERY = 0x56
"""Query timer status - payload [01] [slot 1 or 2]
Response format: 57 08 [slot] 00...
There are 2 timer slots that work together (on timer + off timer)"""

CMD_TIMER_SET = 0x54
"""Set timer - payload format (7 bytes):
  [slot] [enabled] [FF] [hour] [??] [??] [action]
  
Slots: 01 = timer 1, 02 = timer 2
Action: 01 = turn ON, 00 = turn OFF

Example for 6h off-timer at 12:24 (off at 18:24):
  Slot 1: 01 01 FF 0C 18 0C 01
  Slot 2: 02 01 FF 12 18 0C 00"""

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
  [scene_id] [point_idx] [start_h] [start_m] [end_h] [end_m] [R] [G] [B] [C] [W] [brightness]
  
  NOTE: Order is R G B C W (Cool White before Warm White) - differs from 0x50 color command!
  
Example for Pro scene 5AM node (red + cool white):
  0C 01 14 00 05 00 FF 00 00 9E 00 64
  = Scene 0x0C, Point 1, 20:00-05:00, RGB(255,0,0), Cool=158, Warm=0, 100%
  
Example for Pro scene 8PM node (warm white only):
  0C 05 19 00 14 00 00 00 00 00 1E 64  
  = Scene 0x0C, Point 5, 19:00-20:00, RGB(0,0,0), Cool=0, Warm=30, 100%
  
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

MODE_MANUAL = 0x00
"""Static color mode - exits scene, stays on last set color"""

MODE_MANUAL_ALT = 0x01
"""Alternative manual mode (may be equivalent to 0x00 in some contexts)"""

MODE_CORAL_REEF = 0x02
"""24h cycle - High blue, high cool white, 50% brightness"""

MODE_FISH_BLUE = 0x03
"""24h cycle - Deep blue focus, 26% brightness"""

MODE_WATERWEED = 0x04
"""24h cycle - Plant growth mode"""

# Custom scenes start at 0x0B
MODE_CUSTOM_BASIC = 0x0B
"""Custom scene slot 1 (default name: 'Basic')"""

MODE_CUSTOM_PRO = 0x0C
"""Custom scene slot 2 (default name: 'Pro')"""

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
