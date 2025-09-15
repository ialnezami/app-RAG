import React from 'react'
import { useParams } from 'react-router-dom'
import ChatInterface from '../components/Chat/ChatInterface'

const Chat: React.FC = () => {
  const { sessionId } = useParams<{ sessionId?: string }>()

  return (
    <div className="h-full">
      <ChatInterface sessionId={sessionId} />
    </div>
  )
}

export default Chat
