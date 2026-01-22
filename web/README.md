# Gamalta Web Frontend

Web-based control interface for Gamalta BLE aquarium lights.

## Architecture

- **Backend**: FastAPI server wrapping the `gamalta` Python library
- **Frontend**: React SPA with Material UI
- **Communication**: REST API + WebSocket for real-time updates

## Requirements

- Python 3.10+
- Node.js 18+
- Bluetooth adapter (for BLE communication)
- The machine running the backend must have physical access to the Gamalta light via Bluetooth

## Quick Start

### 1. Install backend dependencies

```bash
cd web
pip install -e ".[dev]"
```

Or with the parent project:

```bash
pip install -e "..[dev]"
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Start the backend

```bash
# From the web directory
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Or from project root
python -m uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080` with:
- Swagger docs: `http://localhost:8080/docs`
- WebSocket: `ws://localhost:8080/ws`

### 4. Start the frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using Make (recommended)

A Makefile is provided for convenience:

```bash
make install    # Install all dependencies
make backend    # Start backend server
make frontend   # Start frontend dev server
make help       # Show all available commands
```

## API Endpoints

### Device Management
- `GET /api/device/scan` - Scan for Gamalta devices
- `POST /api/device/connect` - Connect to a device
- `POST /api/device/disconnect` - Disconnect
- `GET /api/device/status` - Get connection and device status

### Light Control
- `POST /api/control/power` - Power on/off
- `POST /api/control/color` - Set RGBWC color
- `POST /api/control/brightness` - Set brightness (0-100)

### Mode Control
- `GET /api/modes` - List available modes
- `POST /api/modes/set` - Set operating mode

### Effects
- `POST /api/effects/lightning/preview` - Trigger lightning flash
- `POST /api/effects/lightning/configure` - Configure lightning schedule

## WebSocket Protocol

Connect to `ws://localhost:8080/ws` for real-time updates.

### Server messages:
```json
{"type": "state", "payload": {"power": true, "mode": 0, "brightness": 75, "color": {...}}}
{"type": "connection", "payload": {"connected": true, "device_name": "Gamalta"}}
{"type": "error", "payload": {"message": "Error description"}}
```

### Client messages:
```json
{"type": "refresh"}  // Request immediate state update
```

## Development

### Backend
```bash
# Run tests
pytest

# Type check
mypy backend
```

### Frontend
```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Type check
npx tsc --noEmit
```

## Environment Variables

Backend configuration via environment:

- `GAMALTA_HOST` - Server host (default: 0.0.0.0)
- `GAMALTA_PORT` - Server port (default: 8080)
- `GAMALTA_POLL_INTERVAL` - State polling interval in seconds (default: 5.0)
