import React from 'react'
import { User } from 'lucide-react'

interface TypingIndicatorProps {
  users: Set<string>
  className?: string
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  users,
  className
}) => {
  if (users.size === 0) return null

  const userList = Array.from(users)
  const displayText = userList.length === 1 
    ? `${userList[0]} is typing...`
    : userList.length === 2
    ? `${userList[0]} and ${userList[1]} are typing...`
    : `${userList[0]} and ${userList.length - 1} others are typing...`

  return (
    <div className={`flex items-center space-x-2 text-sm text-gray-500 ${className}`}>
      <div className="flex -space-x-1">
        {userList.slice(0, 3).map((user, index) => (
          <div
            key={user}
            className="h-6 w-6 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center"
            style={{ zIndex: 3 - index }}
          >
            <User className="h-3 w-3 text-gray-600" />
          </div>
        ))}
      </div>
      <span>{displayText}</span>
      <div className="flex space-x-1">
        <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )
}

export default TypingIndicator
