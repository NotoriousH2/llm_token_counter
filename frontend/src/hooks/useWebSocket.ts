import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '@/stores/appStore';
import type { WebSocketMessage } from '@/types';

const WS_RECONNECT_DELAY = 3000;
const WS_MAX_RECONNECT_ATTEMPTS = 5;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const { setModels, setWsConnected } = useAppStore();

  const getWsUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/tokenizer/api/ws`;
  }, []);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'init':
        case 'model_added':
          if (message.data) {
            setModels(
              message.data.official,
              message.data.custom,
              message.data.version
            );
          }
          break;

        case 'error':
          console.error('WebSocket error:', message.error);
          break;
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, [setModels]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(getWsUrl());

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = handleMessage;

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      wsRef.current = null;

      // Attempt reconnection
      if (reconnectAttempts.current < WS_MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1;
        console.log(`Reconnecting... attempt ${reconnectAttempts.current}`);
        reconnectTimeoutRef.current = setTimeout(connect, WS_RECONNECT_DELAY);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  }, [getWsUrl, handleMessage, setWsConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  }, [setWsConnected]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const addModel = useCallback((name: string, category: 'official' | 'custom') => {
    sendMessage({
      type: 'add_model',
      name,
      category,
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    sendMessage,
    addModel,
    reconnect: connect,
  };
}
