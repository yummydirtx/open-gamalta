/**
 * Mode selector with cards for each mode.
 */

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

// Mode icons mapping
const MODE_ICONS: Record<string, React.ReactNode> = {
  MANUAL: <Tune />,
  SUNSYNC: <WbSunny />,
  CORAL_REEF: <Waves />,
  FISH_BLUE: <Water />,
  WATERWEED: <Grass />,
};

interface ModeCardProps {
  mode: ModeInfo;
  selected: boolean;
  disabled: boolean;
  onSelect: () => void;
}

function ModeCard({ mode, selected, disabled, onSelect }: ModeCardProps) {
  return (
    <Card
      variant={selected ? 'elevation' : 'outlined'}
      sx={{
        height: '100%',
        opacity: disabled ? 0.5 : 1,
        borderColor: selected ? 'primary.main' : 'divider',
        borderWidth: selected ? 2 : 1,
      }}
    >
      <CardActionArea
        onClick={onSelect}
        disabled={disabled}
        sx={{ height: '100%', p: 1 }}
      >
        <CardContent sx={{ textAlign: 'center' }}>
          <Box sx={{ mb: 1, color: selected ? 'primary.main' : 'text.secondary' }}>
            {MODE_ICONS[mode.name] || <Tune />}
          </Box>
          <Typography variant="subtitle2" gutterBottom>
            {mode.name.replace('_', ' ')}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            {mode.description}
          </Typography>
          {mode.hasSchedule && (
            <Chip
              label="24h"
              size="small"
              color="info"
              sx={{ mt: 1 }}
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
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Mode
      </Typography>

      <Grid container spacing={2}>
        {modes.map((m) => (
          <Grid item xs={6} sm={4} md={2.4} key={m.id}>
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
