/**
 * Visual light status display showing current color and state.
 */

import { Box, Typography, Paper, Chip, Stack } from '@mui/material';
import {
  Power,
  PowerOff,
  Bluetooth,
  WbSunny,
  Tune,
  Waves,
  Water,
  Grass,
} from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';

const MODE_ICONS: Record<string, React.ReactNode> = {
  MANUAL: <Tune fontSize="small" />,
  SUNSYNC: <WbSunny fontSize="small" />,
  CORAL_REEF: <Waves fontSize="small" />,
  FISH_BLUE: <Water fontSize="small" />,
  WATERWEED: <Grass fontSize="small" />,
};

export function LightStatus() {
  const { deviceName, power, brightness, color, modeName } = useDeviceStore();

  // Calculate display color
  const rgbColor = `rgb(${color.r}, ${color.g}, ${color.b})`;

  // Calculate white intensity for glow effect
  const whiteIntensity = Math.max(color.warmWhite, color.coolWhite) / 255;
  const warmRatio = color.warmWhite / (color.warmWhite + color.coolWhite + 1);
  const whiteColor = `rgba(255, ${220 + warmRatio * 35}, ${180 + warmRatio * 75}, ${whiteIntensity * 0.8})`;

  return (
    <Paper
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #1a2744 0%, #0d1b2a 100%)',
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background glow effect when on */}
      {power && (
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 300,
            height: 300,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${rgbColor}40 0%, transparent 70%)`,
            filter: 'blur(40px)',
            pointerEvents: 'none',
          }}
        />
      )}

      <Stack spacing={2} alignItems="center" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Device name */}
        <Stack direction="row" alignItems="center" spacing={1}>
          <Bluetooth sx={{ fontSize: 16, color: 'success.main' }} />
          <Typography variant="body2" color="text.secondary">
            {deviceName}
          </Typography>
        </Stack>

        {/* Light visualization */}
        <Box
          sx={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: power
              ? `radial-gradient(circle at 30% 30%, ${whiteColor}, ${rgbColor})`
              : 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)',
            boxShadow: power
              ? `0 0 60px ${rgbColor}80, 0 0 100px ${rgbColor}40, inset 0 0 30px rgba(255,255,255,0.1)`
              : 'inset 0 2px 4px rgba(0,0,0,0.5)',
            border: '3px solid',
            borderColor: power ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.05)',
            transition: 'all 0.3s ease',
          }}
        >
          {power ? (
            <Power sx={{ fontSize: 40, color: 'rgba(255,255,255,0.9)' }} />
          ) : (
            <PowerOff sx={{ fontSize: 40, color: 'rgba(255,255,255,0.3)' }} />
          )}
        </Box>

        {/* Status chips */}
        <Stack direction="row" spacing={1} flexWrap="wrap" justifyContent="center">
          <Chip
            icon={power ? <Power /> : <PowerOff />}
            label={power ? 'ON' : 'OFF'}
            size="small"
            color={power ? 'success' : 'default'}
            variant={power ? 'filled' : 'outlined'}
          />
          <Chip
            icon={MODE_ICONS[modeName] || <Tune />}
            label={modeName.replace('_', ' ')}
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label={`${brightness}%`}
            size="small"
            variant="outlined"
            sx={{ minWidth: 60 }}
          />
        </Stack>

        {/* RGBWC values */}
        <Stack direction="row" spacing={0.5} sx={{ opacity: 0.7 }}>
          <Box sx={{ px: 1, py: 0.25, borderRadius: 1, bgcolor: 'rgba(244,67,54,0.3)' }}>
            <Typography variant="caption">R:{color.r}</Typography>
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: 1, bgcolor: 'rgba(76,175,80,0.3)' }}>
            <Typography variant="caption">G:{color.g}</Typography>
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: 1, bgcolor: 'rgba(33,150,243,0.3)' }}>
            <Typography variant="caption">B:{color.b}</Typography>
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: 1, bgcolor: 'rgba(255,183,77,0.3)' }}>
            <Typography variant="caption">W:{color.warmWhite}</Typography>
          </Box>
          <Box sx={{ px: 1, py: 0.25, borderRadius: 1, bgcolor: 'rgba(144,202,249,0.3)' }}>
            <Typography variant="caption">C:{color.coolWhite}</Typography>
          </Box>
        </Stack>
      </Stack>
    </Paper>
  );
}
