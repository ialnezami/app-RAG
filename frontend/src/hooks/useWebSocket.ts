import { useState, useEffect, useCallback, useRef } from 'react'
import wsService from '../services/websocket'
import { ChatMessage } from '../services/types'

export function useWebSocket(sessionId?: string, userId?: string) {
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set())
  const [streamingContent, setStreamingContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  
  const sessionIdRef = useRef(sessionId)
  const userIdRef = useRef(userId)

  useEffect(() => {
    sessionIdRef.current = sessionId
    userIdRef.current = userId
  }, [sessionId, userId])

  const connect = useCallback(async (newSessionId?: string, newUserId?: string) => {
    const targetSessionId = newSessionId || sessionIdRef.current
    const targetUserId = newUserId || userIdRef.current || 'anonymous'
    
    if (!targetSessionId) {
      setError('Session ID is required')
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      await wsService.connect(targetSessionId, targetUserId)
      setIsConnected(true)
      setIsConnecting(false)
    } catch (err: any) {
      setError(err.message || 'Failed to connect')
      setIsConnecting(false)
    }
  }, [])

  const disconnect = useCallback(() => {
    wsService.disconnect()
    setIsConnected(false)
    setMessages([])
    setIsTyping(false)
    setTypingUsers(new Set())
    setStreamingContent('')
    setIsStreaming(false)
  }, [])

  const sendMessage = useCallback((message: string, profileId: number) => {
    if (!sessionIdRef.current) return
    
    wsService.sendMessage(sessionIdRef.current, message, profileId)
  }, [])

  const sendTyping = useCallback((typing: boolean) => {
    wsService.sendTyping(typing)
  }, [])

  const joinSession = useCallback((targetSessionId: string) => {
    wsService.joinSession(targetSessionId)
  }, [])

  useEffect(() => {
    // Event handlers
    const handleConnected = () => {
      setIsConnected(true)
      setIsConnecting(false)
      setError(null)
    }

    const handleDisconnected = () => {
      setIsConnected(false)
      setIsConnecting(false)
    }

    const handleError = (error: any) => {
      setError(error.message || 'WebSocket error')
      setIsConnecting(false)
    }

    const handleMessageReceived = (data: any) => {
      const message: ChatMessage = {
        id: data.id,
        role: data.role,
        content: data.content,
        context_chunks: data.context_chunks || [],
        timestamp: data.timestamp
      }
      
      setMessages(prev => [...prev, message])
    }

    const handleAIStreaming = (data: any) => {
      setIsStreaming(true)
      setStreamingContent(prev => prev + data.chunk)
    }

    const handleAIMessageComplete = (data: any) => {
      const message: ChatMessage = {
        id: data.id,
        role: data.role,
        content: data.content,
        context_chunks: data.context_chunks || [],
        timestamp: data.timestamp
      }
      
      setMessages(prev => [...prev, message])
      setIsStreaming(false)
      setStreamingContent('')
    }

    const handleTypingIndicator = (data: any) => {
      if (data.typing) {
        setTypingUsers(prev => new Set([...prev, data.user_id]))
      } else {
        setTypingUsers(prev => {
          const newSet = new Set(prev)
          newSet.delete(data.user_id)
          return newSet
        })
      }
    }

    const handleSessionJoined = (data: any) => {
      console.log('Joined session:', data.session_name)
    }

    const handleServerError = (data: any) => {
      setError(data.message)
    }

    // Register event handlers
    wsService.on('connected', handleConnected)
    wsService.on('disconnected', handleDisconnected)
    wsService.on('error', handleError)
    wsService.on('message_received', handleMessageReceived)
    wsService.on('ai_streaming', handleAIStreaming)
    wsService.on('ai_message_complete', handleAIMessageComplete)
    wsService.on('typing_indicator', handleTypingIndicator)
    wsService.on('session_joined', handleSessionJoined)
    wsService.on('error', handleServerError)

    // Cleanup
    return () => {
      wsService.off('connected', handleConnected)
      wsService.off('disconnected', handleDisconnected)
      wsService.off('error', handleError)
      wsService.off('message_received', handleMessageReceived)
      wsService.off('ai_streaming', handleAIStreaming)
      wsService.off('ai_message_complete', handleAIMessageComplete)
      wsService.off('typing_indicator', handleTypingIndicator)
      wsService.off('session_joined', handleSessionJoined)
      wsService.off('error', handleError)
    }
  }, [])

  // Auto-connect when sessionId changes
  useEffect(() => {
    if (sessionId && !isConnected && !isConnecting) {
      connect(sessionId, userId)
    }
  }, [sessionId, connect, isConnected, isConnecting])

  return {
    isConnected,
    isConnecting,
    error,
    messages,
    isTyping,
    typingUsers,
    streamingContent,
    isStreaming,
    connect,
    disconnect,
    sendMessage,
    sendTyping,
    joinSession
  }
}
