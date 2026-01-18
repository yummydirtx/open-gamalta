/**
 * REST API client for the Gamalta backend.
 */

import axios from 'axios';
import type {
  ScanResponse,
  ConnectResponse,
  StatusResponse,
  ModesResponse,
  Color,
} from '../types/device';

const API_BASE = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Device endpoints
export const deviceApi = {
  scan: async (timeout = 5.0): Promise<ScanResponse> => {
    const response = await api.get<ScanResponse>(`/device/scan?timeout=${timeout}`);
    return response.data;
  },

  connect: async (address?: string): Promise<ConnectResponse> => {
    const response = await api.post<ConnectResponse>('/device/connect', { address });
    return response.data;
  },

  disconnect: async (): Promise<void> => {
    await api.post('/device/disconnect');
  },

  getStatus: async (): Promise<StatusResponse> => {
    const response = await api.get<StatusResponse>('/device/status');
    return response.data;
  },

  getName: async (): Promise<string> => {
    const response = await api.get<{ name: string }>('/device/name');
    return response.data.name;
  },

  setName: async (name: string): Promise<void> => {
    await api.put('/device/name', { name });
  },
};

// Control endpoints
export const controlApi = {
  setPower: async (on: boolean): Promise<void> => {
    await api.post('/control/power', { on });
  },

  setColor: async (color: Color): Promise<void> => {
    await api.post('/control/color', {
      r: color.r,
      g: color.g,
      b: color.b,
      warm_white: color.warmWhite,
      cool_white: color.coolWhite,
    });
  },

  setBrightness: async (percent: number): Promise<void> => {
    await api.post('/control/brightness', { percent });
  },
};

// Mode endpoints
export const modesApi = {
  list: async (): Promise<ModesResponse> => {
    const response = await api.get<ModesResponse>('/modes');
    return response.data;
  },

  set: async (mode: string): Promise<void> => {
    await api.post('/modes/set', { mode });
  },
};

// Effects endpoints
export const effectsApi = {
  previewLightning: async (): Promise<void> => {
    await api.post('/effects/lightning/preview');
  },

  configureLightning: async (config: {
    intensity: number;
    frequency: number;
    startHour: number;
    startMinute: number;
    endHour: number;
    endMinute: number;
    days: string[];
    enabled: boolean;
  }): Promise<void> => {
    await api.post('/effects/lightning/configure', {
      intensity: config.intensity,
      frequency: config.frequency,
      start_hour: config.startHour,
      start_minute: config.startMinute,
      end_hour: config.endHour,
      end_minute: config.endMinute,
      days: config.days,
      enabled: config.enabled,
    });
  },
};

export default api;
