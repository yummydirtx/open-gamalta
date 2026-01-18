/**
 * Color picker with RGB wheel and RGBWC sliders.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Slider, Typography, Paper, Stack } from '@mui/material';
import { HexColorPicker } from 'react-colorful';
import { useDeviceStore } from '../stores/deviceStore';
import { controlApi } from '../api/client';
import type { Color } from '../types/device';

// Convert RGB to hex
function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map((x) => x.toString(16).padStart(2, '0')).join('');
}

// Convert hex to RGB
function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 };
}

interface SliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  color: string;
  disabled?: boolean;
}

function ChannelSlider({ label, value, onChange, color, disabled }: SliderProps) {
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {value}
        </Typography>
      </Box>
      <Slider
        value={value}
        onChange={(_, v) => onChange(v as number)}
        min={0}
        max={255}
        disabled={disabled}
        sx={{
          color: color,
          '& .MuiSlider-thumb': {
            backgroundColor: 'white',
            border: `2px solid ${color}`,
          },
        }}
      />
    </Box>
  );
}

export function ColorPicker() {
  const { color, connected, setError } = useDeviceStore();
  const [localColor, setLocalColor] = useState<Color>(color);
  const debounceRef = useRef<number | null>(null);

  // Sync with store when external update comes
  useEffect(() => {
    setLocalColor(color);
  }, [color]);

  const sendColor = useCallback(
    async (newColor: Color) => {
      if (!connected) return;

      try {
        await controlApi.setColor(newColor);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to set color');
      }
    },
    [connected, setError]
  );

  const handleColorChange = useCallback(
    (newColor: Color) => {
      setLocalColor(newColor);

      // Debounce API calls
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      debounceRef.current = window.setTimeout(() => {
        sendColor(newColor);
      }, 200);
    },
    [sendColor]
  );

  const handleHexChange = useCallback(
    (hex: string) => {
      const rgb = hexToRgb(hex);
      handleColorChange({
        ...localColor,
        r: rgb.r,
        g: rgb.g,
        b: rgb.b,
      });
    },
    [localColor, handleColorChange]
  );

  const handleChannelChange = useCallback(
    (channel: keyof Color, value: number) => {
      handleColorChange({ ...localColor, [channel]: value });
    },
    [localColor, handleColorChange]
  );

  const hexColor = rgbToHex(localColor.r, localColor.g, localColor.b);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Color
      </Typography>

      <Stack spacing={3}>
        {/* Color wheel */}
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <HexColorPicker
            color={hexColor}
            onChange={handleHexChange}
            style={{ width: '100%', maxWidth: 200, height: 200 }}
          />
        </Box>

        {/* RGB Sliders */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            RGB Channels
          </Typography>
          <Stack spacing={1}>
            <ChannelSlider
              label="Red"
              value={localColor.r}
              onChange={(v) => handleChannelChange('r', v)}
              color="#f44336"
              disabled={!connected}
            />
            <ChannelSlider
              label="Green"
              value={localColor.g}
              onChange={(v) => handleChannelChange('g', v)}
              color="#4caf50"
              disabled={!connected}
            />
            <ChannelSlider
              label="Blue"
              value={localColor.b}
              onChange={(v) => handleChannelChange('b', v)}
              color="#2196f3"
              disabled={!connected}
            />
          </Stack>
        </Box>

        {/* White channels */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            White Channels
          </Typography>
          <Stack spacing={1}>
            <ChannelSlider
              label="Warm White"
              value={localColor.warmWhite}
              onChange={(v) => handleChannelChange('warmWhite', v)}
              color="#ffb74d"
              disabled={!connected}
            />
            <ChannelSlider
              label="Cool White"
              value={localColor.coolWhite}
              onChange={(v) => handleChannelChange('coolWhite', v)}
              color="#90caf9"
              disabled={!connected}
            />
          </Stack>
        </Box>

        {/* Color preview */}
        <Box
          sx={{
            width: '100%',
            height: 40,
            borderRadius: 1,
            backgroundColor: `rgb(${localColor.r}, ${localColor.g}, ${localColor.b})`,
            border: '1px solid',
            borderColor: 'divider',
          }}
        />
      </Stack>
    </Paper>
  );
}
