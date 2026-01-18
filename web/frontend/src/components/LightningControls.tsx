/**
 * Lightning effect controls and configuration.
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
} from '@mui/material';
import { FlashOn, ExpandMore, ExpandLess } from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { effectsApi } from '../api/client';

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
    <Paper sx={{ p: 2 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FlashOn color="warning" />
          <Typography variant="h6">Lightning Effect</Typography>
        </Box>
        <IconButton size="small">
          {expanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          color="warning"
          startIcon={<FlashOn />}
          onClick={handlePreview}
          disabled={!connected || previewing}
          fullWidth
        >
          {previewing ? 'Flashing...' : 'Preview Flash'}
        </Button>
      </Box>

      <Collapse in={expanded}>
        <Stack spacing={3} sx={{ mt: 3 }}>
          {/* Enable switch */}
          <FormControlLabel
            control={
              <Switch
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                disabled={!connected}
              />
            }
            label="Enable scheduled lightning"
          />

          {/* Intensity */}
          <Box>
            <Typography gutterBottom>
              Intensity: {intensity}%
            </Typography>
            <Slider
              value={intensity}
              onChange={(_, v) => setIntensity(v as number)}
              min={0}
              max={100}
              disabled={!connected || !enabled}
            />
          </Box>

          {/* Frequency */}
          <Box>
            <Typography gutterBottom>
              Frequency: {frequency} flashes
            </Typography>
            <Slider
              value={frequency}
              onChange={(_, v) => setFrequency(v as number)}
              min={0}
              max={10}
              marks
              disabled={!connected || !enabled}
            />
          </Box>

          {/* Time range */}
          <Stack direction="row" spacing={2}>
            <TextField
              label="Start Time"
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              disabled={!connected || !enabled}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="End Time"
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              disabled={!connected || !enabled}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Stack>

          {/* Days */}
          <Box>
            <Typography gutterBottom>Active Days</Typography>
            <FormGroup row>
              {DAYS.map((day) => (
                <FormControlLabel
                  key={day.key}
                  control={
                    <Checkbox
                      checked={selectedDays.includes(day.key)}
                      onChange={() => toggleDay(day.key)}
                      disabled={!connected || !enabled}
                      size="small"
                    />
                  }
                  label={day.label}
                />
              ))}
            </FormGroup>
          </Box>

          {/* Save button */}
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={!connected || saving}
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </Button>
        </Stack>
      </Collapse>
    </Paper>
  );
}
