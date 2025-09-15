import React, { useEffect, useRef } from 'react'
import { formatRelativeTime, highlightText } from '../../utils'
import { ChatMessage } from '../../services/types'
import ContextChunk from './ContextChunk'

interface MessageListProps {
  messages: ChatMessage[]
  streamingContent?: string
  isStreaming?: boolean
  className?: string
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  streamingContent,
  isStreaming,
  className
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  return (
    <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${className}`}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'message-user'
                : message.role === 'assistant'
                ? 'message-assistant'
                : 'message-system'
            }`}
          >
            <div
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{
                __html: highlightText(message.content, '')
              }}
            />
            
            {/* Context chunks for assistant messages */}
            {message.role === 'assistant' && message.context_chunks.length > 0 && (
              <div className="mt-3 space-y-2">
                <div className="text-xs font-medium text-gray-500">
                  Sources:
                </div>
                {message.context_chunks.map((chunk, index) => (
                  <ContextChunk key={index} chunk={chunk} />
                ))}
              </div>
            )}
            
            <div className="text-xs text-gray-500 mt-2">
              {formatRelativeTime(message.timestamp)}
            </div>
          </div>
        </div>
      ))}
      
      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <div className="flex justify-start">
          <div className="max-w-[80%] rounded-lg px-4 py-2 message-assistant">
            <div className="prose prose-sm max-w-none">
              {streamingContent}
              <span className="animate-pulse">|</span>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList
