/**
 * Premium color picker with RGB wheel and glowing RGBWC sliders.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Slider, Typography, Paper, Stack, alpha } from '@mui/material';
import { HexColorPicker } from 'react-colorful';
import { Palette, Lightbulb } from '@mui/icons-material';
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

interface ChannelSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  color: string;
  disabled?: boolean;
}

function ChannelSlider({ label, value, onChange, color, disabled }: ChannelSliderProps) {
  const glowOpacity = value / 255;

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
          {label}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            color: color,
            textShadow: `0 0 ${8 + glowOpacity * 8}px ${alpha(color, 0.5)}`,
          }}
        >
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
          height: 6,
          '& .MuiSlider-track': {
            border: 'none',
            boxShadow: `0 0 ${8 + glowOpacity * 12}px ${alpha(color, 0.4 + glowOpacity * 0.3)}`,
          },
          '& .MuiSlider-rail': {
            background: alpha(color, 0.15),
          },
          '& .MuiSlider-thumb': {
            width: 16,
            height: 16,
            backgroundColor: 'white',
            border: `3px solid ${color}`,
            boxShadow: `0 0 ${8 + glowOpacity * 10}px ${alpha(color, 0.5)}`,
            '&:hover, &.Mui-focusVisible': {
              boxShadow: `0 0 20px ${alpha(color, 0.7)}`,
            },
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
  const rgbColor = `rgb(${localColor.r}, ${localColor.g}, ${localColor.b})`;

  return (
    <Paper sx={{ p: 3, background: 'rgba(15, 31, 56, 0.5)', position: 'relative', overflow: 'hidden' }}>
      {/* Ambient glow from the current color */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: `radial-gradient(circle at 50% 0%, ${alpha(rgbColor, 0.2)} 0%, transparent 60%)`,
          pointerEvents: 'none',
        }}
      />

      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 2,
          }}
        >
          <Palette sx={{ color: hexColor }} />
          Color
        </Typography>

        <Stack spacing={3}>
          {/* Color wheel */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              '& .react-colorful': {
                boxShadow: `0 0 30px ${alpha(rgbColor, 0.3)}`,
              },
            }}
          >
            <HexColorPicker
              color={hexColor}
              onChange={handleHexChange}
              style={{ width: '100%', maxWidth: 220, height: 220 }}
            />
          </Box>

          {/* RGB Sliders */}
          <Box>
            <Typography
              variant="subtitle2"
              gutterBottom
              sx={{ color: 'text.secondary', fontSize: '0.75rem', letterSpacing: '0.05em' }}
            >
              RGB CHANNELS
            </Typography>
            <Stack spacing={1.5}>
              <ChannelSlider
                label="Red"
                value={localColor.r}
                onChange={(v) => handleChannelChange('r', v)}
                color="#ef4444"
                disabled={!connected}
              />
              <ChannelSlider
                label="Green"
                value={localColor.g}
                onChange={(v) => handleChannelChange('g', v)}
                color="#22c55e"
                disabled={!connected}
              />
              <ChannelSlider
                label="Blue"
                value={localColor.b}
                onChange={(v) => handleChannelChange('b', v)}
                color="#3b82f6"
                disabled={!connected}
              />
            </Stack>
          </Box>

          {/* White channels */}
          <Box>
            <Typography
              variant="subtitle2"
              gutterBottom
              sx={{
                color: 'text.secondary',
                fontSize: '0.75rem',
                letterSpacing: '0.05em',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <Lightbulb sx={{ fontSize: 16 }} />
              WHITE CHANNELS
            </Typography>
            <Stack spacing={1.5}>
              <ChannelSlider
                label="Warm White"
                value={localColor.warmWhite}
                onChange={(v) => handleChannelChange('warmWhite', v)}
                color="#fbbf24"
                disabled={!connected}
              />
              <ChannelSlider
                label="Cool White"
                value={localColor.coolWhite}
                onChange={(v) => handleChannelChange('coolWhite', v)}
                color="#93c5fd"
                disabled={!connected}
              />
            </Stack>
          </Box>

          {/* Live color preview */}
          <Box
            sx={{
              width: '100%',
              height: 48,
              borderRadius: 2,
              backgroundColor: rgbColor,
              boxShadow: `0 0 30px ${alpha(rgbColor, 0.5)}, inset 0 0 20px rgba(255,255,255,0.1)`,
              border: '1px solid rgba(255, 255, 255, 0.1)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* White overlay based on white channels */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: `linear-gradient(90deg, 
                  rgba(255, 200, 150, ${localColor.warmWhite / 255 * 0.6}) 0%, 
                  rgba(200, 220, 255, ${localColor.coolWhite / 255 * 0.6}) 100%)`,
                pointerEvents: 'none',
              }}
            />
            {/* Highlight */}
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '50%',
                background: 'linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 100%)',
                pointerEvents: 'none',
              }}
            />
          </Box>
        </Stack>
      </Box>
    </Paper>
  );
}
