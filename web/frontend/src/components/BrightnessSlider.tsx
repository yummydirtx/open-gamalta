/**
 * Premium brightness control slider with glowing effects.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Box, Slider, Typography, Paper, Stack, keyframes } from '@mui/material';
import { WbSunny, NightsStay } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { controlApi } from '../api/client';

const sunPulse = keyframes`
  0%, 100% {
    filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6));
    transform: scale(1);
  }
  50% {
    filter: drop-shadow(0 0 16px rgba(251, 191, 36, 0.9));
    transform: scale(1.1);
  }
`;

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

  // Calculate glow intensity based on brightness
  const glowIntensity = localBrightness / 100;
  const glowColor = `rgba(251, 191, 36, ${0.3 + glowIntensity * 0.4})`;

  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(15, 31, 56, 0.5)',
        position: 'relative',
        overflow: 'hidden',
        minHeight: 180,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      {/* Background glow based on brightness */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: '60%',
          height: '100%',
          background: `radial-gradient(ellipse at 100% 50%, ${glowColor} 0%, transparent 70%)`,
          opacity: glowIntensity,
          transition: 'all 0.3s ease',
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
            mb: 3,
          }}
        >
          <WbSunny
            sx={{
              color: 'warning.main',
              animation: localBrightness > 50 ? `${sunPulse} 2s ease-in-out infinite` : 'none',
            }}
          />
          Brightness
        </Typography>

        <Stack direction="row" spacing={3} alignItems="center">
          <NightsStay
            sx={{
              fontSize: 28,
              color: localBrightness < 30 ? 'primary.main' : 'text.secondary',
              transition: 'all 0.3s ease',
              filter: localBrightness < 30 ? 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))' : 'none',
            }}
          />

          <Slider
            value={localBrightness}
            onChange={handleChange}
            min={0}
            max={100}
            disabled={!connected}
            valueLabelDisplay="auto"
            valueLabelFormat={(v) => `${v}%`}
            sx={{
              flex: 1,
              height: 10,
              '& .MuiSlider-track': {
                background: 'linear-gradient(90deg, #3b82f6 0%, #fbbf24 100%)',
                border: 'none',
                boxShadow: `0 0 ${10 + glowIntensity * 15}px rgba(251, 191, 36, ${0.3 + glowIntensity * 0.3})`,
              },
              '& .MuiSlider-rail': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
              '& .MuiSlider-thumb': {
                width: 24,
                height: 24,
                background: 'linear-gradient(145deg, #ffffff 0%, #e0e0e0 100%)',
                boxShadow: `0 0 ${10 + glowIntensity * 10}px rgba(251, 191, 36, ${0.4 + glowIntensity * 0.4})`,
                '&:hover, &.Mui-focusVisible': {
                  boxShadow: `0 0 20px rgba(251, 191, 36, 0.7)`,
                },
                '&::before': {
                  display: 'none',
                },
              },
              '& .MuiSlider-valueLabel': {
                background: 'rgba(15, 31, 56, 0.95)',
                borderRadius: 2,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              },
            }}
          />

          <WbSunny
            sx={{
              fontSize: 32,
              color: localBrightness > 70 ? 'warning.main' : 'text.secondary',
              transition: 'all 0.3s ease',
              animation: localBrightness > 70 ? `${sunPulse} 2s ease-in-out infinite` : 'none',
            }}
          />
        </Stack>

        {/* Large brightness display */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(135deg, rgba(255,255,255,${0.5 + glowIntensity * 0.5}) 0%, rgba(251, 191, 36, ${glowIntensity}) 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              textShadow: connected ? `0 0 ${20 + glowIntensity * 20}px rgba(251, 191, 36, ${glowIntensity * 0.5})` : 'none',
              transition: 'all 0.3s ease',
              opacity: connected ? 1 : 0.4,
            }}
          >
            {localBrightness}%
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}
