/**
 * Zustand store for device state management.
 */

import { create } from 'zustand';
import type { Color, ModeInfo } from '../types/device';

interface DeviceStore {
  // Connection state
  connected: boolean;
  connecting: boolean;
  deviceName: string | null;
  deviceAddress: string | null;

  // Light state
  power: boolean;
  mode: number;
  modeName: string;
  brightness: number;
  color: Color;

  // Available modes (cached)
  modes: ModeInfo[];

  // UI state
  pendingCommand: boolean;
  lastError: string | null;
  isEditingColor: boolean;  // Prevents WebSocket from overwriting color while user is editing

  // Actions
  setConnection: (connected: boolean, name?: string | null, address?: string | null) => void;
  setConnecting: (connecting: boolean) => void;
  setState: (state: Partial<{
    power: boolean;
    mode: number;
    modeName: string;
    brightness: number;
    color: Color;
  }>) => void;
  setModes: (modes: ModeInfo[]) => void;
  setError: (error: string | null) => void;
  setPending: (pending: boolean) => void;
  setEditingColor: (editing: boolean) => void;
  reset: () => void;
}

const initialState = {
  connected: false,
  connecting: false,
  deviceName: null,
  deviceAddress: null,
  power: false,
  mode: 0,
  modeName: 'MANUAL',
  brightness: 0,
  color: { r: 0, g: 0, b: 0, warmWhite: 0, coolWhite: 0 },
  modes: [],
  pendingCommand: false,
  lastError: null,
  isEditingColor: false,
};

export const useDeviceStore = create<DeviceStore>((set, get) => ({
  ...initialState,

  setConnection: (connected, name = null, address = null) =>
    set({
      connected,
      connecting: false,
      deviceName: name,
      deviceAddress: address,
      ...(connected ? {} : { power: false, brightness: 0 }),
    }),

  setConnecting: (connecting) => set({ connecting }),

  setState: (state) =>
    set((prev) => {
      // If editing color, don't update color from external source (WebSocket)
      const newColor = state.color && !get().isEditingColor
        ? { ...prev.color, ...state.color }
        : prev.color;

      return {
        ...prev,
        ...state,
        color: newColor,
      };
    }),

  setModes: (modes) => set({ modes }),

  setError: (error) => set({ lastError: error }),

  setPending: (pending) => set({ pendingCommand: pending }),

  setEditingColor: (editing) => set({ isEditingColor: editing }),

  reset: () => set(initialState),
}));

