/**
 * Main application component.
 */

import { useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  Stack,
  Alert,
  Snackbar,
  Grid,
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

// Create dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#00bcd4',
    },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
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

      {/* App Bar */}
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar>
          <Waves sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Gamalta Light Controller
          </Typography>
          <ConnectionStatus />
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {!connected ? (
          // Disconnected state
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Waves sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              No Device Connected
            </Typography>
            <Typography color="text.secondary">
              Click "Connect" above to scan for and connect to your Gamalta light.
            </Typography>
          </Paper>
        ) : (
          // Connected state - show controls
          <Stack spacing={3}>
            {/* Top row - Power and Brightness */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
                  <PowerButton />
                </Paper>
              </Grid>
              <Grid item xs={12} md={8}>
                <BrightnessSlider />
              </Grid>
            </Grid>

            {/* Mode selector */}
            <Paper sx={{ p: 2 }}>
              <ModeSelector />
            </Paper>

            {/* Color picker and Lightning */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <ColorPicker />
              </Grid>
              <Grid item xs={12} md={6}>
                <LightningControls />
              </Grid>
            </Grid>
          </Stack>
        )}
      </Container>

      {/* Error snackbar */}
      <Snackbar
        open={!!lastError}
        autoHideDuration={5000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {lastError}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
