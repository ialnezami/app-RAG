import React from 'react'

interface ChatInterfaceProps {
  sessionId?: string
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
  return (
    <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Chat Interface
        </h2>
        <p className="text-gray-600">
          Chat interface will be implemented here.
          {sessionId && ` Session ID: ${sessionId}`}
        </p>
      </div>
    </div>
  )
}

export default ChatInterface
