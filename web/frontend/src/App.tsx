/**
 * Main application component with premium UI design.
 */

import { useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Typography,
  Box,
  Paper,
  Stack,
  Alert,
  Snackbar,
  Grid,
  alpha,
} from '@mui/material';
import { Waves } from '@mui/icons-material';
import {
  ConnectionStatus,
  PowerButton,
  ColorPicker,
  BrightnessSlider,
  ModeSelector,
  LightningControls,
} from './components';
import { useWebSocket } from './hooks/useWebSocket';
import { useDeviceStore } from './stores/deviceStore';

// Create premium dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    },
    secondary: {
      main: '#06b6d4',
      light: '#22d3ee',
      dark: '#0891b2',
    },
    success: {
      main: '#22c55e',
      light: '#4ade80',
      dark: '#16a34a',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    background: {
      default: '#050a15',
      paper: 'rgba(15, 31, 56, 0.7)',
    },
    text: {
      primary: 'rgba(255, 255, 255, 0.95)',
      secondary: 'rgba(255, 255, 255, 0.6)',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h4: {
      fontWeight: 600,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    subtitle1: {
      fontWeight: 500,
    },
    body1: {
      letterSpacing: '0.01em',
    },
    body2: {
      letterSpacing: '0.01em',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: 'none',
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          transition: 'all 0.25s ease',
          '&:hover': {
            borderColor: 'rgba(59, 130, 246, 0.2)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 10,
          padding: '10px 20px',
          transition: 'all 0.25s ease',
        },
        contained: {
          boxShadow: '0 4px 14px rgba(0, 0, 0, 0.3)',
          '&:hover': {
            boxShadow: '0 6px 20px rgba(59, 130, 246, 0.4)',
            transform: 'translateY(-1px)',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': {
            borderWidth: '1.5px',
            backgroundColor: 'rgba(59, 130, 246, 0.08)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          backdropFilter: 'blur(10px)',
        },
        filled: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          height: 8,
        },
        thumb: {
          width: 20,
          height: 20,
          boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)',
          '&:hover, &.Mui-focusVisible': {
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.7)',
          },
        },
        track: {
          border: 'none',
          boxShadow: '0 0 10px currentColor',
        },
        rail: {
          backgroundColor: 'rgba(255, 255, 255, 0.15)',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(15, 31, 56, 0.95)',
          backdropFilter: 'blur(30px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backdropFilter: 'blur(20px)',
          transition: 'all 0.25s ease',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: 'all 0.25s ease',
        },
      },
    },
  },
});

function App() {
  // Initialize WebSocket connection
  useWebSocket();

  const { connected, lastError, setError } = useDeviceStore();

  // Clear error after 5 seconds
  useEffect(() => {
    if (lastError) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [lastError, setError]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      {/* Animated Background */}
      <Box className="animated-bg" />

      {/* Premium Header */}
      <Box
        component="header"
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          py: 2,
          px: 3,
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          background: alpha('#0a1628', 0.8),
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            {/* Logo & Title */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: '12px',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 20px rgba(59, 130, 246, 0.4)',
                  animation: connected ? 'none' : 'wave 2s ease-in-out infinite',
                }}
              >
                <Waves sx={{ fontSize: 26, color: 'white' }} />
              </Box>
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.7) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  open-gamalta
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ color: 'text.secondary', letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: '0.65rem' }}
                >
                  Web Light Controller
                </Typography>
              </Box>
            </Box>

            {/* Connection Status */}
            <ConnectionStatus />
          </Box>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {!connected ? (
          // Disconnected state with premium styling
          <Paper
            sx={{
              p: 6,
              textAlign: 'center',
              background: 'rgba(15, 31, 56, 0.5)',
              borderRadius: 4,
            }}
          >
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 3,
                animation: 'float 3s ease-in-out infinite',
              }}
            >
              <Waves sx={{ fontSize: 60, color: 'primary.main', opacity: 0.8 }} />
            </Box>
            <Typography
              variant="h5"
              gutterBottom
              sx={{
                background: 'linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.6) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              No Device Connected
            </Typography>
            <Typography color="text.secondary" sx={{ maxWidth: 400, mx: 'auto' }}>
              Click "Connect" above to scan for and connect to your Gamalta aquarium light.
            </Typography>
          </Paper>
        ) : (
          // Connected state - show controls
          <Stack spacing={3}>
            {/* Top row - Power and Brightness */}
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 4 }}>
                <Paper
                  sx={{
                    p: 3,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100%',
                    background: 'rgba(15, 31, 56, 0.5)',
                  }}
                >
                  <PowerButton />
                </Paper>
              </Grid>
              <Grid size={{ xs: 12, md: 8 }}>
                <BrightnessSlider />
              </Grid>
            </Grid>

            {/* Mode selector */}
            <Paper sx={{ p: 3, background: 'rgba(15, 31, 56, 0.5)' }}>
              <ModeSelector />
            </Paper>

            {/* Color picker and Lightning */}
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <ColorPicker />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <LightningControls />
              </Grid>
            </Grid>
          </Stack>
        )}
      </Container>

      {/* Error snackbar with premium styling */}
      <Snackbar
        open={!!lastError}
        autoHideDuration={5000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{
            backdropFilter: 'blur(20px)',
            background: 'rgba(239, 68, 68, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}
        >
          {lastError}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
