import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from './useAuth'

interface WebSocketMessage {
  type: string
  payload: any
}

interface UseWebSocketProps {
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useWebSocket({
  onMessage,
  onError,
  onConnect,
  onDisconnect,
}: UseWebSocketProps = {}) {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const { user } = useAuth()
  
  // Store callbacks in refs to avoid recreating connectWebSocket
  const onMessageRef = useRef(onMessage)
  const onErrorRef = useRef(onError)
  const onConnectRef = useRef(onConnect)
  const onDisconnectRef = useRef(onDisconnect)
  
  useEffect(() => {
    onMessageRef.current = onMessage
    onErrorRef.current = onError
    onConnectRef.current = onConnect
    onDisconnectRef.current = onDisconnect
  }, [onMessage, onError, onConnect, onDisconnect])

  const connectWebSocket = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    // Include session_id in WebSocket URL for Google Ads integration
    const sessionId = typeof window !== 'undefined' 
      ? (localStorage.getItem('session_id') || crypto.randomUUID())
      : crypto.randomUUID()
    
    if (typeof window !== 'undefined' && !localStorage.getItem('session_id')) {
      localStorage.setItem('session_id', sessionId)
    }
    
    const baseWsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat'
    let wsUrl = `${baseWsUrl}?session_id=${sessionId}`
    
    // Add authentication token if user is logged in
    if (user) {
      try {
        const idToken = await user.getIdToken()
        wsUrl += `&token=${idToken}`
      } catch (error) {
        console.error('Failed to get auth token:', error)
      }
    }
    
    console.log('Attempting WebSocket connection to:', wsUrl.replace(/token=.*/, 'token=***'))
    
    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setConnectionStatus('connected')
        reconnectAttemptsRef.current = 0
        onConnectRef.current?.()
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          onMessageRef.current?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onErrorRef.current?.(error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setConnectionStatus('disconnected')
        wsRef.current = null
        onDisconnectRef.current?.()

        // Reconnect with exponential backoff
        const attempts = reconnectAttemptsRef.current
        if (attempts < 5) {
          const delay = Math.min(1000 * Math.pow(2, attempts), 10000)
          console.log(`Reconnecting in ${delay}ms (attempt ${attempts + 1})`)
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connectWebSocket()
          }, delay)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      setConnectionStatus('disconnected')
    }
  }, [user])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    console.log('sendMessage called:', {
      message,
      wsRef: wsRef.current,
      readyState: wsRef.current?.readyState,
      readyStateString: wsRef.current ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][wsRef.current.readyState] : 'NO_SOCKET'
    })
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const messageString = JSON.stringify(message)
      console.log('Sending WebSocket message:', messageString)
      wsRef.current.send(messageString)
      console.log('Message sent successfully')
    } else {
      console.error('WebSocket is not connected:', {
        readyState: wsRef.current?.readyState,
        readyStateString: wsRef.current ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][wsRef.current.readyState] : 'NO_SOCKET',
        connectionStatus
      })
    }
  }, [connectionStatus])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  useEffect(() => {
    connectWebSocket()

    return () => {
      disconnect()
    }
  }, [connectWebSocket, disconnect])

  return {
    sendMessage,
    connectionStatus,
    reconnect: connectWebSocket,
    disconnect,
  }
}