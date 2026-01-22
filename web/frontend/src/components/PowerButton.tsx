/**
 * Premium power on/off toggle button with glow effects.
 */

import { useState } from 'react';
import { Box, Typography, CircularProgress, keyframes } from '@mui/material';
import { Power, PowerOff } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { controlApi } from '../api/client';

// Subtle pulse animation for the glow effect
const pulseGlow = keyframes`
  0%, 100% {
    box-shadow: 
      0 0 15px rgba(34, 197, 94, 0.3),
      0 0 25px rgba(34, 197, 94, 0.15);
  }
  50% {
    box-shadow: 
      0 0 20px rgba(34, 197, 94, 0.4),
      0 0 30px rgba(34, 197, 94, 0.2);
  }
`;

// Ripple removed for cleaner look

export function PowerButton() {
  const { power, connected, setError, setState } = useDeviceStore();
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    if (!connected || loading) return;

    setLoading(true);
    const newPower = !power;

    // Optimistic update
    setState({ power: newPower });

    try {
      await controlApi.setPower(newPower);
    } catch (e) {
      // Rollback on error
      setState({ power: !newPower });
      setError(e instanceof Error ? e.message : 'Failed to toggle power');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 2,
      }}
    >
      {/* Outer glow ring */}
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Glow ring when on */}

        {/* Main button */}
        <Box
          component="button"
          onClick={handleToggle}
          disabled={!connected || loading}
          sx={{
            width: 100,
            height: 100,
            borderRadius: '50%',
            border: 'none',
            cursor: connected ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            transition: 'all 0.3s ease',
            background: power
              ? 'linear-gradient(145deg, #22c55e 0%, #16a34a 100%)'
              : 'linear-gradient(145deg, #374151 0%, #1f2937 100%)',
            boxShadow: power
              ? '0 0 20px rgba(34, 197, 94, 0.4), 0 0 40px rgba(34, 197, 94, 0.2), inset 0 -2px 10px rgba(0,0,0,0.2)'
              : 'inset 0 2px 10px rgba(0, 0, 0, 0.3), 0 4px 20px rgba(0, 0, 0, 0.3)',
            animation: power && connected ? `${pulseGlow} 4s ease-in-out infinite` : 'none',
            '&:hover:not(:disabled)': {
              transform: 'scale(1.05)',
              boxShadow: power
                ? '0 0 30px rgba(34, 197, 94, 0.6), 0 0 60px rgba(34, 197, 94, 0.3)'
                : '0 0 20px rgba(255, 255, 255, 0.1), 0 4px 30px rgba(0, 0, 0, 0.4)',
            },
            '&:active:not(:disabled)': {
              transform: 'scale(0.98)',
            },
            '&:disabled': {
              opacity: 0.4,
              cursor: 'not-allowed',
            },
          }}
        >
          {/* Inner highlight */}
          <Box
            sx={{
              position: 'absolute',
              top: 4,
              left: 4,
              right: 4,
              height: '50%',
              borderRadius: '50% 50% 50% 50%',
              background: 'linear-gradient(180deg, rgba(255,255,255,0.2) 0%, transparent 100%)',
              pointerEvents: 'none',
            }}
          />

          {loading ? (
            <CircularProgress size={36} sx={{ color: 'white' }} />
          ) : power ? (
            <Power
              sx={{
                fontSize: 44,
                color: 'white',
                filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.5))',
              }}
            />
          ) : (
            <PowerOff
              sx={{
                fontSize: 44,
                color: 'rgba(255, 255, 255, 0.5)',
              }}
            />
          )}
        </Box>
      </Box>

      {/* Status label */}
      <Typography
        variant="body2"
        sx={{
          fontWeight: 600,
          letterSpacing: '0.1em',
          color: power ? 'success.main' : 'text.secondary',
          textShadow: power ? '0 0 20px rgba(34, 197, 94, 0.5)' : 'none',
          transition: 'all 0.3s ease',
        }}
      >
        {power ? 'ON' : 'OFF'}
      </Typography>
    </Box>
  );
}
