/**
 * Connection status indicator and connect/disconnect controls.
 */

import { useState } from 'react';
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  CircularProgress,
  Typography,
  Alert,
} from '@mui/material';
import {
  Bluetooth,
  BluetoothDisabled,
  Search,
  LinkOff,
} from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { deviceApi } from '../api/client';
import type { DeviceInfo } from '../types/device';

export function ConnectionStatus() {
  const { connected, connecting, deviceName, setConnecting, setConnection, setError } =
    useDeviceStore();

  const [scanOpen, setScanOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [scanError, setScanError] = useState<string | null>(null);

  const handleScan = async () => {
    setScanOpen(true);
    setScanning(true);
    setScanError(null);
    setDevices([]);

    try {
      const result = await deviceApi.scan(5.0);
      setDevices(result.devices);
    } catch (e) {
      setScanError(e instanceof Error ? e.message : 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleConnect = async (address?: string) => {
    setScanOpen(false);
    setConnecting(true);
    setError(null);

    try {
      const result = await deviceApi.connect(address);
      setConnection(true, result.device_name, address);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Connection failed');
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await deviceApi.disconnect();
      setConnection(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Disconnect failed');
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Chip
        icon={connected ? <Bluetooth /> : <BluetoothDisabled />}
        label={connected ? deviceName || 'Connected' : 'Disconnected'}
        color={connected ? 'success' : 'default'}
        variant={connected ? 'filled' : 'outlined'}
      />

      {connected ? (
        <Button
          variant="outlined"
          color="error"
          size="small"
          startIcon={<LinkOff />}
          onClick={handleDisconnect}
        >
          Disconnect
        </Button>
      ) : (
        <Button
          variant="contained"
          size="small"
          startIcon={connecting ? <CircularProgress size={16} /> : <Search />}
          onClick={handleScan}
          disabled={connecting}
        >
          {connecting ? 'Connecting...' : 'Connect'}
        </Button>
      )}

      <Dialog open={scanOpen} onClose={() => setScanOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Connect to Device</DialogTitle>
        <DialogContent>
          {scanning ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 4 }}>
              <CircularProgress size={24} />
              <Typography>Scanning for devices...</Typography>
            </Box>
          ) : scanError ? (
            <Alert severity="error">{scanError}</Alert>
          ) : devices.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>
              No devices found. Make sure your Gamalta light is powered on.
            </Typography>
          ) : (
            <List>
              {devices.map((device) => (
                <ListItem key={device.address} disablePadding>
                  <ListItemButton onClick={() => handleConnect(device.address)}>
                    <ListItemText
                      primary={device.name}
                      secondary={device.address}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScanOpen(false)}>Cancel</Button>
          {!scanning && devices.length === 0 && (
            <Button onClick={() => handleConnect()} variant="contained">
              Auto-discover
            </Button>
          )}
          {!scanning && (
            <Button onClick={handleScan} startIcon={<Search />}>
              Rescan
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
