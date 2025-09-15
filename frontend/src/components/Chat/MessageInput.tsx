import React, { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, X } from 'lucide-react'
import Button from '../Common/Button'
import { CONSTANTS } from '../../utils'

interface MessageInputProps {
  onSendMessage: (message: string) => void
  onSendTyping: (typing: boolean) => void
  disabled?: boolean
  placeholder?: string
  maxLength?: number
  allowFileUpload?: boolean
  onFileUpload?: (file: File) => void
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onSendTyping,
  disabled = false,
  placeholder = 'Type your message...',
  maxLength = CONSTANTS.MAX_MESSAGE_LENGTH,
  allowFileUpload = false,
  onFileUpload
}) => {
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  // Typing indicator
  useEffect(() => {
    if (message.trim() && !isTyping) {
      setIsTyping(true)
      onSendTyping(true)
    } else if (!message.trim() && isTyping) {
      setIsTyping(false)
      onSendTyping(false)
    }
  }, [message, isTyping, onSendTyping])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      setIsTyping(false)
      onSendTyping(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && onFileUpload) {
      setSelectedFile(file)
      onFileUpload(file)
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* File attachment */}
        {selectedFile && (
          <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
            <Paperclip className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-700 truncate flex-1">
              {selectedFile.name}
            </span>
            <button
              type="button"
              onClick={removeFile}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Input area */}
        <div className="flex items-end space-x-2">
          {/* File upload button */}
          {allowFileUpload && (
            <button
              type="button"
              onClick={openFileDialog}
              disabled={disabled}
              className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
            >
              <Paperclip className="h-5 w-5" />
            </button>
          )}

          {/* Hidden file input */}
          {allowFileUpload && (
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              className="hidden"
              accept=".pdf,.doc,.docx,.txt,.md"
            />
          )}

          {/* Text input */}
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              maxLength={maxLength}
              rows={1}
              className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
          </div>

          {/* Send button */}
          <Button
            type="submit"
            disabled={!message.trim() || disabled}
            size="sm"
            className="px-3"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Character count */}
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>
            {message.length}/{maxLength} characters
          </span>
          <span>
            Press Enter to send, Shift+Enter for new line
          </span>
        </div>
      </form>
    </div>
  )
}

export default MessageInput
