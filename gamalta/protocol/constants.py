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
