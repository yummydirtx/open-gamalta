/**
 * Premium lightning effect controls with dramatic styling.
 */

import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Slider,
  Button,
  Stack,
  FormGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  Switch,
  Collapse,
  IconButton,
  keyframes,
  alpha,
} from '@mui/material';
import { FlashOn, ExpandMore, Schedule } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { effectsApi } from '../api/client';

const flashPulse = keyframes`
  0%, 90%, 100% {
    opacity: 1;
    filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6));
  }
  95% {
    opacity: 0.3;
    filter: drop-shadow(0 0 20px rgba(251, 191, 36, 1));
  }
`;

const buttonFlash = keyframes`
  0%, 100% {
    box-shadow: 0 4px 20px rgba(251, 191, 36, 0.4);
  }
  50% {
    box-shadow: 0 4px 40px rgba(251, 191, 36, 0.8);
  }
`;

const DAYS = [
  { key: 'monday', label: 'Mon' },
  { key: 'tuesday', label: 'Tue' },
  { key: 'wednesday', label: 'Wed' },
  { key: 'thursday', label: 'Thu' },
  { key: 'friday', label: 'Fri' },
  { key: 'saturday', label: 'Sat' },
  { key: 'sunday', label: 'Sun' },
];

export function LightningControls() {
  const { connected, setError } = useDeviceStore();

  const [expanded, setExpanded] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Configuration state
  const [enabled, setEnabled] = useState(true);
  const [intensity, setIntensity] = useState(50);
  const [frequency, setFrequency] = useState(5);
  const [startTime, setStartTime] = useState('20:00');
  const [endTime, setEndTime] = useState('22:00');
  const [selectedDays, setSelectedDays] = useState<string[]>([
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ]);

  const handlePreview = async () => {
    if (!connected || previewing) return;

    setPreviewing(true);
    try {
      await effectsApi.previewLightning();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Preview failed');
    } finally {
      setPreviewing(false);
    }
  };

  const handleSave = async () => {
    if (!connected || saving) return;

    const [startHour, startMinute] = startTime.split(':').map(Number);
    const [endHour, endMinute] = endTime.split(':').map(Number);

    setSaving(true);
    try {
      await effectsApi.configureLightning({
        intensity,
        frequency,
        startHour,
        startMinute,
        endHour,
        endMinute,
        days: selectedDays,
        enabled,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const toggleDay = (day: string) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  return (
    <Paper sx={{ p: 3, background: 'rgba(15, 31, 56, 0.5)', position: 'relative', overflow: 'hidden' }}>
      {/* Ambient lightning glow */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          right: 0,
          width: '50%',
          height: '100%',
          background: 'radial-gradient(ellipse at 100% 0%, rgba(251, 191, 36, 0.1) 0%, transparent 60%)',
          pointerEvents: 'none',
        }}
      />

      <Box sx={{ position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            mb: 2,
          }}
          onClick={() => setExpanded(!expanded)}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 15px rgba(251, 191, 36, 0.3)',
              }}
            >
              <FlashOn
                sx={{
                  color: 'white',
                  animation: `${flashPulse} 3s ease-in-out infinite`,
                }}
              />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ lineHeight: 1.2 }}>
                Lightning Effect
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Simulate realistic lightning
              </Typography>
            </Box>
          </Box>
          <IconButton
            size="small"
            sx={{
              background: 'rgba(255, 255, 255, 0.05)',
              transition: 'all 0.3s ease',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          >
            <ExpandMore />
          </IconButton>
        </Box>

        {/* Preview button - always visible */}
        <Button
          variant="contained"
          startIcon={<FlashOn />}
          onClick={handlePreview}
          disabled={!connected || previewing}
          fullWidth
          sx={{
            background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
            color: '#1a1a1a',
            fontWeight: 600,
            py: 1.5,
            animation: previewing ? `${buttonFlash} 0.3s ease-in-out infinite` : 'none',
            '&:hover': {
              background: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
              boxShadow: '0 6px 30px rgba(251, 191, 36, 0.5)',
            },
            '&:disabled': {
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'rgba(255, 255, 255, 0.3)',
            },
          }}
        >
          {previewing ? 'Flashing...' : 'Preview Flash'}
        </Button>

        {/* Expandable configuration */}
        <Collapse in={expanded}>
          <Stack spacing={3} sx={{ mt: 3, pt: 3, borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
            {/* Enable switch */}
            <FormControlLabel
              control={
                <Switch
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                  disabled={!connected}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#fbbf24',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#f59e0b',
                    },
                  }}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Schedule sx={{ fontSize: 18, color: 'text.secondary' }} />
                  <Typography>Enable scheduled lightning</Typography>
                </Box>
              }
            />

            {/* Intensity */}
            <Box sx={{ opacity: enabled ? 1 : 0.5, transition: 'opacity 0.3s ease' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Intensity</Typography>
                <Typography
                  sx={{
                    fontWeight: 600,
                    color: 'warning.main',
                    textShadow: `0 0 ${intensity / 10}px rgba(251, 191, 36, 0.5)`,
                  }}
                >
                  {intensity}%
                </Typography>
              </Box>
              <Slider
                value={intensity}
                onChange={(_, v) => setIntensity(v as number)}
                min={0}
                max={100}
                disabled={!connected || !enabled}
                sx={{
                  color: '#fbbf24',
                  '& .MuiSlider-track': {
                    boxShadow: `0 0 ${intensity / 10 + 5}px rgba(251, 191, 36, 0.4)`,
                  },
                  '& .MuiSlider-thumb': {
                    boxShadow: `0 0 ${intensity / 10 + 5}px rgba(251, 191, 36, 0.5)`,
                  },
                }}
              />
            </Box>

            {/* Frequency */}
            <Box sx={{ opacity: enabled ? 1 : 0.5, transition: 'opacity 0.3s ease' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Frequency</Typography>
                <Typography sx={{ fontWeight: 600, color: 'warning.main' }}>
                  {frequency} flashes
                </Typography>
              </Box>
              <Slider
                value={frequency}
                onChange={(_, v) => setFrequency(v as number)}
                min={0}
                max={10}
                marks
                disabled={!connected || !enabled}
                sx={{ color: '#fbbf24' }}
              />
            </Box>

            {/* Time range */}
            <Stack direction="row" spacing={2} sx={{ opacity: enabled ? 1 : 0.5 }}>
              <TextField
                label="Start Time"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                disabled={!connected || !enabled}
                fullWidth
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'rgba(255, 255, 255, 0.03)',
                  },
                }}
              />
              <TextField
                label="End Time"
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                disabled={!connected || !enabled}
                fullWidth
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'rgba(255, 255, 255, 0.03)',
                  },
                }}
              />
            </Stack>

            {/* Days */}
            <Box sx={{ opacity: enabled ? 1 : 0.5 }}>
              <Typography gutterBottom sx={{ mb: 1.5 }}>
                Active Days
              </Typography>
              <FormGroup row sx={{ gap: 0.5 }}>
                {DAYS.map((day) => (
                  <FormControlLabel
                    key={day.key}
                    control={
                      <Checkbox
                        checked={selectedDays.includes(day.key)}
                        onChange={() => toggleDay(day.key)}
                        disabled={!connected || !enabled}
                        size="small"
                        sx={{
                          // Visually hidden but accessible for screen readers and keyboard
                          position: 'absolute',
                          width: 1,
                          height: 1,
                          padding: 0,
                          margin: -1,
                          overflow: 'hidden',
                          clip: 'rect(0, 0, 0, 0)',
                          whiteSpace: 'nowrap',
                          border: 0,
                        }}
                      />
                    }
                    label={day.label}
                    sx={{
                      m: 0,
                      px: 1.5,
                      py: 0.75,
                      borderRadius: 2,
                      position: 'relative',
                      background: selectedDays.includes(day.key)
                        ? alpha('#fbbf24', 0.2)
                        : 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid',
                      borderColor: selectedDays.includes(day.key)
                        ? alpha('#fbbf24', 0.4)
                        : 'rgba(255, 255, 255, 0.08)',
                      cursor: !connected || !enabled ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        borderColor:
                          !connected || !enabled ? undefined : alpha('#fbbf24', 0.3),
                      },
                      '&:focus-within': {
                        outline: '2px solid',
                        outlineColor: alpha('#fbbf24', 0.6),
                        outlineOffset: 2,
                      },
                      '& .MuiFormControlLabel-label': {
                        fontSize: '0.8rem',
                        fontWeight: 500,
                        color: selectedDays.includes(day.key)
                          ? '#fbbf24'
                          : 'text.secondary',
                      },
                    }}
                  />
                ))}
              </FormGroup>
            </Box>

            {/* Save button */}
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={!connected || saving}
              sx={{
                background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                py: 1.5,
                '&:hover': {
                  boxShadow: '0 6px 25px rgba(59, 130, 246, 0.4)',
                },
              }}
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </Stack>
        </Collapse>
      </Box>
    </Paper>
  );
}
