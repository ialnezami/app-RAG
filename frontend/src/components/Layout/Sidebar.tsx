import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  MessageSquare, 
  FileText, 
  Users, 
  Settings, 
  X,
  Activity
} from 'lucide-react'
import { useAppStore } from '../../store'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation()
  const { chatSessions } = useAppStore()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Profiles', href: '/profiles', icon: Users },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-sm border-r border-gray-200">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-gray-900">RAG App</h1>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={`group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                            isActive(item.href)
                              ? 'bg-primary-50 text-primary-700'
                              : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50'
                          }`}
                        >
                          <Icon
                            className={`h-6 w-6 shrink-0 ${
                              isActive(item.href)
                                ? 'text-primary-700'
                                : 'text-gray-400 group-hover:text-primary-700'
                            }`}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>

              {/* Chat Sessions */}
              <li>
                <div className="text-xs font-semibold leading-6 text-gray-400 uppercase tracking-wide">
                  Recent Chats
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {chatSessions.slice(0, 5).map((session) => (
                    <li key={session.id}>
                      <Link
                        to={`/chat/${session.id}`}
                        className="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium text-gray-700 hover:text-primary-700 hover:bg-gray-50"
                      >
                        <MessageSquare className="h-5 w-5 shrink-0 text-gray-400 group-hover:text-primary-700" />
                        <span className="truncate">
                          {session.session_name || 'Untitled Chat'}
                        </span>
                      </Link>
                    </li>
                  ))}
                  {chatSessions.length === 0 && (
                    <li className="text-sm text-gray-500 px-2 py-1">
                      No recent chats
                    </li>
                  )}
                </ul>
              </li>

              {/* System Status */}
              <li className="mt-auto">
                <div className="text-xs font-semibold leading-6 text-gray-400 uppercase tracking-wide mb-2">
                  System Status
                </div>
                <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-md">
                  <Activity className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-gray-600">All systems operational</span>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div className={`lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">R</span>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900">RAG App</h1>
              </div>
            </div>
            <button
              type="button"
              className="rounded-md p-2 text-gray-400 hover:text-gray-500"
              onClick={onClose}
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <nav className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50'
                    }`}
                    onClick={onClose}
                  >
                    <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* Chat Sessions */}
            <div className="mt-8">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                Recent Chats
              </div>
              <div className="space-y-1">
                {chatSessions.slice(0, 5).map((session) => (
                  <Link
                    key={session.id}
                    to={`/chat/${session.id}`}
                    className="group flex items-center px-2 py-2 text-sm font-medium text-gray-700 rounded-md hover:text-primary-700 hover:bg-gray-50"
                    onClick={onClose}
                  >
                    <MessageSquare className="mr-3 h-5 w-5 flex-shrink-0" />
                    <span className="truncate">
                      {session.session_name || 'Untitled Chat'}
                    </span>
                  </Link>
                ))}
                {chatSessions.length === 0 && (
                  <div className="text-sm text-gray-500 px-2 py-1">
                    No recent chats
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Sidebar
