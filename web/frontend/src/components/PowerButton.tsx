/**
 * Power on/off toggle button.
 */

import { useState } from 'react';
import { Box, IconButton, Typography, CircularProgress } from '@mui/material';
import { Power, PowerOff } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { controlApi } from '../api/client';

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
        gap: 1,
      }}
    >
      <IconButton
        onClick={handleToggle}
        disabled={!connected || loading}
        sx={{
          width: 80,
          height: 80,
          backgroundColor: power ? 'success.main' : 'grey.300',
          color: power ? 'white' : 'grey.600',
          '&:hover': {
            backgroundColor: power ? 'success.dark' : 'grey.400',
          },
          '&:disabled': {
            backgroundColor: 'grey.200',
            color: 'grey.400',
          },
        }}
      >
        {loading ? (
          <CircularProgress size={32} color="inherit" />
        ) : power ? (
          <Power sx={{ fontSize: 40 }} />
        ) : (
          <PowerOff sx={{ fontSize: 40 }} />
        )}
      </IconButton>
      <Typography variant="caption" color="text.secondary">
        {power ? 'ON' : 'OFF'}
      </Typography>
    </Box>
  );
}
