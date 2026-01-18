/**
 * Type definitions for the Gamalta device API.
 */

export interface Color {
  r: number;
  g: number;
  b: number;
  warmWhite: number;
  coolWhite: number;
}

export interface DeviceState {
  connected: boolean;
  power: boolean;
  mode: number;
  modeName: string;
  brightness: number;
  color: Color;
  timestamp?: string;
}

export interface DeviceInfo {
  address: string;
  name: string;
}

export interface ModeInfo {
  id: number;
  name: string;
  description: string;
  hasSchedule: boolean;
}

export interface ConnectionStatus {
  connected: boolean;
  deviceName: string | null;
  deviceAddress: string | null;
}

// WebSocket message types
export type WSMessageType = 'state' | 'connection' | 'error' | 'scene_tick';

export interface WSStateMessage {
  type: 'state';
  payload: {
    connected: boolean;
    power: boolean;
    mode: number;
    mode_name: string;
    brightness: number;
    color: {
      r: number;
      g: number;
      b: number;
      warm_white: number;
      cool_white: number;
    };
    timestamp?: string;
  };
}

export interface WSConnectionMessage {
  type: 'connection';
  payload: {
    connected: boolean;
    device_name: string | null;
    device_address: string | null;
  };
}

export interface WSErrorMessage {
  type: 'error';
  payload: {
    code: string;
    message: string;
  };
}

export type WSMessage = WSStateMessage | WSConnectionMessage | WSErrorMessage;

// API response types
export interface ScanResponse {
  devices: DeviceInfo[];
}

export interface ConnectResponse {
  success: boolean;
  device_name: string | null;
}

export interface StatusResponse {
  connected: boolean;
  device_name: string | null;
  device_address: string | null;
  state: {
    connected: boolean;
    power: boolean;
    mode: number;
    mode_name: string;
    brightness: number;
    color: {
      r: number;
      g: number;
      b: number;
      warm_white: number;
      cool_white: number;
    };
  } | null;
}

export interface ModesResponse {
  modes: Array<{
    id: number;
    name: string;
    description: string;
    has_schedule: boolean;
  }>;
}
