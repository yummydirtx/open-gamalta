"""
Gamalta Packet Builder

Low-level packet assembly for the Gamalta protocol.
"""

import random
from .constants import PACKET_HEADER


class PacketBuilder:
    """
    Builds protocol packets with automatic sequence number management.
    
    All Gamalta packets follow the structure:
    [Header 0xA5] [Sequence] [Command] [Sub-cmd/Length] [Payload...]
    """
    
    def __init__(self, initial_seq: int | None = None):
        """
        Initialize the packet builder.
        
        Args:
            initial_seq: Starting sequence number (randomized if not provided)
        """
        if initial_seq is None:
            initial_seq = random.randint(10, 100)
        self._seq = initial_seq
    
    @property
    def sequence(self) -> int:
        """Current sequence number."""
        return self._seq
    
    def _next_seq(self) -> int:
        """Increment and return the next sequence number."""
        self._seq = (self._seq + 1) % 256
        return self._seq
    
    def build(self, payload: bytes | bytearray) -> bytes:
        """
        Build a complete packet with header and sequence.
        
        Args:
            payload: The command payload (starting with opcode)
            
        Returns:
            Complete packet bytes ready to send
        """
        seq = self._next_seq()
        packet = bytearray([PACKET_HEADER, seq])
        packet.extend(payload)
        return bytes(packet)
    
    def build_raw(self, *args: int) -> bytes:
        """
        Build a packet from individual byte values.
        
        Args:
            *args: Byte values for the payload
            
        Returns:
            Complete packet bytes ready to send
        """
        return self.build(bytes(args))
