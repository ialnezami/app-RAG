import {
  WebSocketMessage,
  JoinSessionMessage,
  SendMessageMessage,
  TypingMessage,
  MessageReceivedMessage,
  AIStreamingMessage,
  AIMessageCompleteMessage,
  TypingIndicatorMessage,
  SessionJoinedMessage,
  SessionCreatedMessage,
  ErrorMessage
} from './types'

type WebSocketEventHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 1000
  private isConnecting = false
  private eventHandlers = new Map<string, Set<WebSocketEventHandler>>()

  constructor() {
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  }

  connect(sessionId: string, userId: string = 'anonymous'): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
        resolve()
        return
      }

      this.isConnecting = true
      const wsUrl = `${this.url}?session_id=${sessionId}&user_id=${userId}`
      
      try {
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.emit('connected')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          this.emit('disconnected')
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect(sessionId, userId)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          this.emit('error', error)
          reject(error)
        }

      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  private scheduleReconnect(sessionId: string, userId: string): void {
    this.reconnectAttempts++
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      this.connect(sessionId, userId).catch(() => {
        // Reconnection failed, will be handled by onclose
      })
    }, delay)
  }

  private handleMessage(message: WebSocketMessage): void {
    this.emit(message.type, message)
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
  }

  // Message sending methods
  joinSession(sessionId: string): void {
    const message: JoinSessionMessage = {
      type: 'join_session',
      session_id: sessionId
    }
    this.send(message)
  }

  sendMessage(sessionId: string, message: string, profileId: number): void {
    const wsMessage: SendMessageMessage = {
      type: 'send_message',
      session_id: sessionId,
      message,
      profile_id: profileId
    }
    this.send(wsMessage)
  }

  sendTyping(typing: boolean): void {
    const message: TypingMessage = {
      type: 'typing',
      typing
    }
    this.send(message)
  }

  private send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message:', message)
    }
  }

  // Event handling
  on(event: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  off(event: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error('Error in WebSocket event handler:', error)
        }
      })
    }
  }

  // Connection status
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get connectionState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED
  }

  // URL management
  setUrl(url: string): void {
    this.url = url
  }

  getUrl(): string {
    return this.url
  }
}

// Export singleton instance
export const wsService = new WebSocketService()
export default wsService
