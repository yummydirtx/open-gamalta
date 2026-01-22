/**
 * WebSocket hook for real-time device state updates.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useDeviceStore } from '../stores/deviceStore';
import type { WSMessage } from '../types/device';

// Build WebSocket URL from window.location or env var
const getWsUrl = (): string => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws`;
};

const RECONNECT_DELAY = 3000;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isManuallyClosed = useRef<boolean>(false);

  const { setConnection, setState, setError } = useDeviceStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    isManuallyClosed.current = false;
    const ws = new WebSocket(getWsUrl());

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);

        switch (message.type) {
          case 'state':
            setState({
              power: message.payload.power,
              mode: message.payload.mode,
              modeName: message.payload.mode_name,
              brightness: message.payload.brightness,
              color: {
                r: message.payload.color.r,
                g: message.payload.color.g,
                b: message.payload.color.b,
                warmWhite: message.payload.color.warm_white,
                coolWhite: message.payload.color.cool_white,
              },
            });
            break;

          case 'connection':
            setConnection(
              message.payload.connected,
              message.payload.device_name,
              message.payload.device_address
            );
            break;

          case 'error':
            setError(message.payload.message);
            break;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      wsRef.current = null;

      // Only schedule reconnect if not manually closed
      if (!isManuallyClosed.current) {
        console.log('Scheduling reconnect...');
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = window.setTimeout(connect, RECONNECT_DELAY);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  }, [setConnection, setState, setError]);

  const disconnect = useCallback(() => {
    isManuallyClosed.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const refresh = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'refresh' }));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Refresh on tab visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        refresh();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [refresh]);

  return { refresh };
}
