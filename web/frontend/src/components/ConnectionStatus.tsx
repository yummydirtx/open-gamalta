/**
 * Premium connection status indicator and controls.
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
  keyframes,
  alpha,
} from '@mui/material';
import {
  Bluetooth,
  BluetoothDisabled,
  Search,
  LinkOff,
  BluetoothSearching,
} from '@mui/icons-material';
import { useDeviceStore } from '../stores/deviceStore';
import { deviceApi } from '../api/client';
import type { DeviceInfo } from '../types/device';

const pulseGlow = keyframes`
  0%, 100% {
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
  }
  50% {
    box-shadow: 0 0 16px rgba(34, 197, 94, 0.7);
  }
`;

const scanPulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
`;

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
      {/* Connection status chip */}
      <Chip
        icon={
          connected ? (
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                backgroundColor: 'success.main',
                animation: `${pulseGlow} 2s ease-in-out infinite`,
                ml: 1,
              }}
            />
          ) : (
            <BluetoothDisabled sx={{ fontSize: 18 }} />
          )
        }
        label={connected ? deviceName || 'Connected' : 'Disconnected'}
        sx={{
          background: connected
            ? 'rgba(34, 197, 94, 0.15)'
            : 'rgba(255, 255, 255, 0.05)',
          border: '1px solid',
          borderColor: connected
            ? alpha('#22c55e', 0.3)
            : 'rgba(255, 255, 255, 0.1)',
          color: connected ? 'success.light' : 'text.secondary',
          fontWeight: 500,
          backdropFilter: 'blur(10px)',
          px: 0.5,
          '& .MuiChip-icon': {
            color: connected ? 'success.main' : 'text.secondary',
          },
        }}
      />

      {connected ? (
        <Button
          variant="outlined"
          color="error"
          size="small"
          startIcon={<LinkOff />}
          onClick={handleDisconnect}
          sx={{
            borderColor: alpha('#ef4444', 0.5),
            '&:hover': {
              borderColor: '#ef4444',
              background: alpha('#ef4444', 0.1),
            },
          }}
        >
          Disconnect
        </Button>
      ) : (
        <Button
          variant="contained"
          size="small"
          startIcon={
            connecting ? (
              <CircularProgress size={16} sx={{ color: 'white' }} />
            ) : (
              <Bluetooth />
            )
          }
          onClick={handleScan}
          disabled={connecting}
          sx={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
            boxShadow: '0 4px 20px rgba(59, 130, 246, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #2563eb 0%, #0891b2 100%)',
              boxShadow: '0 6px 25px rgba(59, 130, 246, 0.5)',
            },
          }}
        >
          {connecting ? 'Connecting...' : 'Connect'}
        </Button>
      )}

      {/* Scan dialog */}
      <Dialog
        open={scanOpen}
        onClose={() => setScanOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(15, 31, 56, 0.95)',
            backdropFilter: 'blur(30px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          }}
        >
          <BluetoothSearching sx={{ color: 'primary.main' }} />
          Connect to Device
        </DialogTitle>
        <DialogContent sx={{ py: 3 }}>
          {scanning ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                py: 4,
              }}
            >
              <Box
                sx={{
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: 'rgba(59, 130, 246, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  animation: `${scanPulse} 1.5s ease-in-out infinite`,
                }}
              >
                <BluetoothSearching sx={{ fontSize: 30, color: 'primary.main' }} />
              </Box>
              <Typography color="text.secondary">Scanning for devices...</Typography>
            </Box>
          ) : scanError ? (
            <Alert
              severity="error"
              sx={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
              }}
            >
              {scanError}
            </Alert>
          ) : devices.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography color="text.secondary" gutterBottom>
                No devices found.
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Make sure your Gamalta light is powered on and in range.
              </Typography>
            </Box>
          ) : (
            <List sx={{ mx: -2 }}>
              {devices.map((device) => (
                <ListItem key={device.address} disablePadding>
                  <ListItemButton
                    onClick={() => handleConnect(device.address)}
                    sx={{
                      borderRadius: 2,
                      mx: 1,
                      '&:hover': {
                        background: 'rgba(59, 130, 246, 0.1)',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '10px',
                        background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 2,
                      }}
                    >
                      <Bluetooth sx={{ color: 'white' }} />
                    </Box>
                    <ListItemText
                      primary={device.name}
                      secondary={device.address}
                      primaryTypographyProps={{ fontWeight: 500 }}
                      secondaryTypographyProps={{ sx: { opacity: 0.6 } }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', px: 3, py: 2 }}>
          <Button onClick={() => setScanOpen(false)} sx={{ color: 'text.secondary' }}>
            Cancel
          </Button>
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
