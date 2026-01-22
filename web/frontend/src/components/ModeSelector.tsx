/**
 * Premium mode selector with stunning gradient cards.
 */

import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardActionArea,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  keyframes,
  alpha,
} from '@mui/material';
import {
  Tune,
  WbSunny,
  Waves,
  Water,
  Grass,
} from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { modesApi } from '../api/client';
import type { ModeInfo } from '../types/device';

// Mode configurations with colors
const MODE_CONFIG: Record<string, { icon: ReactNode; gradient: string; color: string }> = {
  MANUAL: {
    icon: <Tune />,
    gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    color: '#8b5cf6',
  },
  SUNSYNC: {
    icon: <WbSunny />,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
    color: '#f59e0b',
  },
  CORAL_REEF: {
    icon: <Waves />,
    gradient: 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
    color: '#ec4899',
  },
  FISH_BLUE: {
    icon: <Water />,
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
    color: '#3b82f6',
  },
  WATERWEED: {
    icon: <Grass />,
    gradient: 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)',
    color: '#22c55e',
  },
};

const glowPulse = keyframes`
  0%, 100% {
    box-shadow: 0 0 20px var(--glow-color), 0 4px 20px rgba(0, 0, 0, 0.3);
  }
  50% {
    box-shadow: 0 0 35px var(--glow-color), 0 4px 25px rgba(0, 0, 0, 0.35);
  }
`;

const iconFloat = keyframes`
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
`;

interface ModeCardProps {
  mode: ModeInfo;
  selected: boolean;
  disabled: boolean;
  onSelect: () => void;
}

function ModeCard({ mode, selected, disabled, onSelect }: ModeCardProps) {
  const config = MODE_CONFIG[mode.name] || MODE_CONFIG.MANUAL;

  return (
    <Card
      sx={{
        height: '100%',
        background: selected
          ? alpha(config.color, 0.15)
          : 'rgba(15, 31, 56, 0.4)',
        border: '1px solid',
        borderColor: selected ? alpha(config.color, 0.5) : 'rgba(255, 255, 255, 0.06)',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.3s ease',
        '--glow-color': alpha(config.color, 0.4),
        animation: selected ? `${glowPulse} 3s ease-in-out infinite` : 'none',
        '&:hover': {
          borderColor: disabled ? undefined : alpha(config.color, 0.4),
          transform: disabled ? 'none' : 'translateY(-4px)',
          boxShadow: disabled ? 'none' : `0 8px 30px ${alpha(config.color, 0.2)}`,
        },
      } as any}
    >
      <CardActionArea
        onClick={onSelect}
        disabled={disabled}
        sx={{ height: '100%', p: 0.5 }}
      >
        <CardContent sx={{ textAlign: 'center', py: 2 }}>
          {/* Icon with gradient background */}
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '12px',
              background: selected ? config.gradient : 'rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 1.5,
              transition: 'all 0.3s ease',
              boxShadow: selected ? `0 4px 20px ${alpha(config.color, 0.4)}` : 'none',
              animation: selected ? `${iconFloat} 3s ease-in-out infinite` : 'none',
              '& svg': {
                fontSize: 26,
                color: selected ? 'white' : 'text.secondary',
                transition: 'all 0.3s ease',
              },
            }}
          >
            {config.icon}
          </Box>

          {/* Mode name */}
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 600,
              color: selected ? config.color : 'text.primary',
              transition: 'all 0.3s ease',
              mb: 0.5,
            }}
          >
            {mode.name.replace('_', ' ')}
          </Typography>

          {/* Description */}
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: 'block',
              lineHeight: 1.4,
              minHeight: 36,
            }}
          >
            {mode.description}
          </Typography>

          {/* Schedule badge */}
          {mode.hasSchedule && (
            <Chip
              label="24h Schedule"
              size="small"
              sx={{
                mt: 1,
                height: 22,
                fontSize: '0.65rem',
                background: selected
                  ? alpha(config.color, 0.2)
                  : 'rgba(255, 255, 255, 0.08)',
                color: selected ? config.color : 'text.secondary',
                border: `1px solid ${selected ? alpha(config.color, 0.3) : 'transparent'}`,
              }}
            />
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}

export function ModeSelector() {
  const { mode, modes, connected, setModes, setError } = useDeviceStore();
  const [loading, setLoading] = useState(false);
  const [changing, setChanging] = useState(false);

  // Fetch modes on mount
  useEffect(() => {
    const fetchModes = async () => {
      setLoading(true);
      try {
        const result = await modesApi.list();
        setModes(
          result.modes.map((m) => ({
            id: m.id,
            name: m.name,
            description: m.description,
            hasSchedule: m.has_schedule,
          }))
        );
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load modes');
      } finally {
        setLoading(false);
      }
    };

    fetchModes();
  }, [setModes, setError]);

  const handleModeSelect = async (modeInfo: ModeInfo) => {
    if (!connected || changing || modeInfo.id === mode) return;

    setChanging(true);
    try {
      await modesApi.set(modeInfo.name);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to change mode');
    } finally {
      setChanging(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  return (
    <Box>
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
        <Tune sx={{ color: 'primary.main' }} />
        Light Mode
      </Typography>

      <Grid container spacing={2}>
        {modes.map((m) => (
          <Grid size={{ xs: 6, sm: 4, md: 2.4 }} key={m.id}>
            <ModeCard
              mode={m}
              selected={m.id === mode}
              disabled={!connected || changing}
              onSelect={() => handleModeSelect(m)}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
