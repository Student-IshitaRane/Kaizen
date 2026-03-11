import { toast } from 'react-hot-toast'

export interface WebSocketMessage {
  type: 'transaction_processed' | 'analysis_completed' | 'case_created' | 'system_status'
  data: any
  timestamp: string
}

export interface TransactionProcessedData {
  transactionId: string
  invoiceId: string
  vendorName: string
  amount: number
  timestamp: string
}

export interface AnalysisCompletedData {
  transactionId: string
  riskScore: number
  riskLevel: 'low' | 'medium' | 'high'
  processingTimeMs: number
  timestamp: string
}

export interface CaseCreatedData {
  caseId: string
  transactionId: string
  flagType: string
  riskScore: number
  timestamp: string
}

export interface SystemStatusData {
  pipelineStatus: 'operational' | 'degraded' | 'offline'
  activeConnections: number
  processingRate: number
  timestamp: string
}

class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, ((data: any) => void)[]> = new Map()
  private url: string

  constructor() {
    // Use environment variable or default to localhost:8000 (backend)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_HOST || 'localhost:8000'
    this.url = `${wsProtocol}//${host}/ws`
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      // Get authentication token from localStorage
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('No authentication token found for WebSocket connection')
        toast.error('Authentication required for real-time monitoring')
        return
      }

      // Add token to WebSocket URL
      const urlWithToken = `${this.url}?token=${encodeURIComponent(token)}`
      this.socket = new WebSocket(urlWithToken)

      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        toast.success('Real-time monitoring connected')
      }

      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.notifyListeners(message.type, message.data)
          
          // Show toast notifications for important events
          switch (message.type) {
            case 'transaction_processed':
              const txData = message.data as TransactionProcessedData
              toast.success(`Transaction processed: ${txData.invoiceId}`, {
                duration: 3000,
                icon: '💰'
              })
              break
            case 'case_created':
              const caseData = message.data as CaseCreatedData
              toast.error(`Flagged case created: ${caseData.caseId}`, {
                duration: 4000,
                icon: '⚠️'
              })
              break
            case 'analysis_completed':
              const analysisData = message.data as AnalysisCompletedData
              if (analysisData.riskLevel === 'high') {
                toast.error(`High risk detected: Score ${analysisData.riskScore}`, {
                  duration: 5000,
                  icon: '🚨'
                })
              }
              break
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.socket.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.attemptReconnect()
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      toast.error('Real-time monitoring disconnected')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.listeners.clear()
  }

  subscribe(eventType: string, callback: (data: any) => void) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType)!.push(callback)
  }

  unsubscribe(eventType: string, callback: (data: any) => void) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  private notifyListeners(eventType: string, data: any) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }

  send(message: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }
}

// Singleton instance
export const webSocketService = new WebSocketService()

// Hook for React components
export const useWebSocket = () => {
  return {
    connect: () => webSocketService.connect(),
    disconnect: () => webSocketService.disconnect(),
    subscribe: webSocketService.subscribe.bind(webSocketService),
    unsubscribe: webSocketService.unsubscribe.bind(webSocketService),
    send: webSocketService.send.bind(webSocketService),
    isConnected: webSocketService.isConnected.bind(webSocketService)
  }
}