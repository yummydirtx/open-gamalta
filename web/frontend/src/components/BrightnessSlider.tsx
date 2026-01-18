/**
 * Brightness control slider.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Box, Slider, Typography, Paper, Stack } from '@mui/material';
import { Brightness7, Brightness4 } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { controlApi } from '../api/client';

export function BrightnessSlider() {
  const { brightness, connected, setError } = useDeviceStore();
  const [localBrightness, setLocalBrightness] = useState(brightness);
  const debounceRef = useRef<number | null>(null);

  // Sync with store when external update comes
  useEffect(() => {
    setLocalBrightness(brightness);
  }, [brightness]);

  const sendBrightness = useCallback(
    async (value: number) => {
      if (!connected) return;

      try {
        await controlApi.setBrightness(value);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to set brightness');
      }
    },
    [connected, setError]
  );

  const handleChange = useCallback(
    (_: Event, value: number | number[]) => {
      const newValue = value as number;
      setLocalBrightness(newValue);

      // Debounce API calls
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      debounceRef.current = window.setTimeout(() => {
        sendBrightness(newValue);
      }, 200);
    },
    [sendBrightness]
  );

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Brightness
      </Typography>

      <Stack direction="row" spacing={2} alignItems="center">
        <Brightness4 color="action" />
        <Slider
          value={localBrightness}
          onChange={handleChange}
          min={0}
          max={100}
          disabled={!connected}
          valueLabelDisplay="auto"
          valueLabelFormat={(v) => `${v}%`}
          sx={{ flex: 1 }}
        />
        <Brightness7 color="warning" />
      </Stack>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
        <Typography variant="h4" color={connected ? 'text.primary' : 'text.disabled'}>
          {localBrightness}%
        </Typography>
      </Box>
    </Paper>
  );
}
