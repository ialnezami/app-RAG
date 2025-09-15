import React, { useState, useEffect } from 'react'
import { Plus, Users } from 'lucide-react'
import { useAppStore } from '../../store'
import { useWebSocket } from '../../hooks/useWebSocket'
import { useApi } from '../../hooks/useApi'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import TypingIndicator from './TypingIndicator'
import Button from '../Common/Button'
import Modal from '../Common/Modal'

interface ChatInterfaceProps {
  sessionId?: string
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
  const { currentProfile, currentSession, setCurrentSession } = useAppStore()
  const { execute, api } = useApi()
  const {
    messages,
    isConnected,
    isStreaming,
    streamingContent,
    typingUsers,
    sendMessage,
    sendTyping
  } = useWebSocket(sessionId)

  const [isCreatingSession, setIsCreatingSession] = useState(false)
  const [showSessionModal, setShowSessionModal] = useState(false)

  useEffect(() => {
    if (sessionId) {
      // Load existing session
      execute(() => api.getChatSession(sessionId)).then((session) => {
        if (session) {
          setCurrentSession(session)
        }
      })
    } else {
      // No specific session, show session creation or general chat
      setCurrentSession(null)
    }
  }, [sessionId])

  const handleSendMessage = (message: string) => {
    if (!currentProfile) {
      alert('Please select a profile first')
      return
    }

    if (sessionId) {
      // Send to existing session
      sendMessage(message, currentProfile.id)
    } else {
      // Create new session or send to general chat
      if (!currentSession) {
        createNewSession(message)
      } else {
        sendMessage(message, currentProfile.id)
      }
    }
  }

  const createNewSession = async (firstMessage?: string) => {
    if (!currentProfile) return

    setIsCreatingSession(true)
    try {
      const session = await execute(() => 
        api.createChatSession({
          profile_id: currentProfile.id,
          session_name: `Chat with ${currentProfile.name}`
        })
      )
      
      if (session) {
        setCurrentSession(session)
        if (firstMessage) {
          sendMessage(firstMessage, currentProfile.id)
        }
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    } finally {
      setIsCreatingSession(false)
      setShowSessionModal(false)
    }
  }

  const handleFileUpload = (file: File) => {
    // Handle file upload logic here
    console.log('File uploaded:', file.name)
  }

  if (!currentProfile) {
    return (
      <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200 flex items-center justify-center">
        <div className="text-center">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No Profile Selected
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Please select a profile to start chatting.
          </p>
          <div className="mt-6">
            <Button onClick={() => window.location.href = '/profiles'}>
              Go to Profiles
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {currentProfile.name.charAt(0)}
            </span>
          </div>
          <div>
            <h2 className="text-lg font-medium text-gray-900">
              {currentSession?.session_name || 'New Chat'}
            </h2>
            <p className="text-sm text-gray-500">
              {currentProfile.name} • {currentProfile.provider}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-xs text-gray-500">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSessionModal(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Session
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 flex flex-col min-h-0">
        <MessageList
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
          className="flex-1"
        />
        
        {/* Typing indicator */}
        <TypingIndicator users={typingUsers} className="px-4 pb-2" />
      </div>

      {/* Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        onSendTyping={sendTyping}
        disabled={!isConnected || isCreatingSession}
        allowFileUpload={true}
        onFileUpload={handleFileUpload}
      />

      {/* Session Creation Modal */}
      <Modal
        isOpen={showSessionModal}
        onClose={() => setShowSessionModal(false)}
        title="Create New Chat Session"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Create a new chat session with the current profile: <strong>{currentProfile.name}</strong>
          </p>
          
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowSessionModal(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => createNewSession()}
              loading={isCreatingSession}
            >
              Create Session
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default ChatInterface
