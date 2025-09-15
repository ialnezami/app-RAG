import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  MessageSquare, 
  FileText, 
  Users, 
  Activity,
  TrendingUp,
  Plus
} from 'lucide-react'
import { useAppStore } from '../store'
import { useApi } from '../hooks/useApi'
import { formatRelativeTime } from '../utils'

const Dashboard: React.FC = () => {
  const { 
    profiles, 
    documents, 
    chatSessions, 
    currentProfile,
    isLoading 
  } = useAppStore()
  
  const { execute, api } = useApi()

  useEffect(() => {
    // Load initial data
    const loadData = async () => {
      await Promise.all([
        execute(() => api.getProfiles()),
        execute(() => api.getDocuments()),
        execute(() => api.getChatSessions())
      ])
    }
    
    loadData()
  }, [])

  const stats = [
    {
      name: 'Total Profiles',
      value: profiles.length,
      icon: Users,
      color: 'bg-blue-500',
      href: '/profiles'
    },
    {
      name: 'Documents',
      value: documents.length,
      icon: FileText,
      color: 'bg-green-500',
      href: '/documents'
    },
    {
      name: 'Chat Sessions',
      value: chatSessions.length,
      icon: MessageSquare,
      color: 'bg-purple-500',
      href: '/chat'
    },
    {
      name: 'Processed Docs',
      value: documents.filter(d => d.processed).length,
      icon: Activity,
      color: 'bg-orange-500',
      href: '/documents'
    }
  ]

  const recentSessions = chatSessions
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 5)

  const recentDocuments = documents
    .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
    .slice(0, 5)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome to RAG Application
            </h1>
            <p className="mt-2 text-gray-600">
              Your intelligent document processing and chat platform
            </p>
          </div>
          {currentProfile && (
            <div className="flex items-center space-x-2 px-4 py-2 bg-primary-50 rounded-lg">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-primary-700">
                Active: {currentProfile.name}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white overflow-hidden shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`${stat.color} p-3 rounded-md`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Chat Sessions */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Recent Chat Sessions
              </h3>
              <Link
                to="/chat"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentSessions.length > 0 ? (
              recentSessions.map((session) => (
                <div key={session.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <Link
                        to={`/chat/${session.id}`}
                        className="text-sm font-medium text-gray-900 hover:text-primary-600 truncate"
                      >
                        {session.session_name || 'Untitled Chat'}
                      </Link>
                      <p className="text-sm text-gray-500">
                        {session.messages.length} messages
                      </p>
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatRelativeTime(session.updated_at)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center">
                <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No chat sessions
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by creating a new chat session.
                </p>
                <div className="mt-6">
                  <Link
                    to="/chat"
                    className="btn btn-primary btn-sm"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    New Chat
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Documents */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Recent Documents
              </h3>
              <Link
                to="/documents"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentDocuments.length > 0 ? (
              recentDocuments.map((document) => (
                <div key={document.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {document.original_filename}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          document.processed 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {document.processed ? 'Processed' : 'Processing'}
                        </span>
                        {document.file_size && (
                          <span className="text-xs text-gray-500">
                            {(document.file_size / 1024 / 1024).toFixed(1)} MB
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatRelativeTime(document.upload_date)}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No documents
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Upload your first document to get started.
                </p>
                <div className="mt-6">
                  <Link
                    to="/documents"
                    className="btn btn-primary btn-sm"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Upload Document
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link
            to="/chat"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <MessageSquare className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <div className="text-sm font-medium text-gray-900">Start New Chat</div>
              <div className="text-sm text-gray-500">Begin a conversation</div>
            </div>
          </Link>
          
          <Link
            to="/documents"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <FileText className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <div className="text-sm font-medium text-gray-900">Upload Document</div>
              <div className="text-sm text-gray-500">Add new content</div>
            </div>
          </Link>
          
          <Link
            to="/profiles"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Users className="h-8 w-8 text-purple-600 mr-3" />
            <div>
              <div className="text-sm font-medium text-gray-900">Manage Profiles</div>
              <div className="text-sm text-gray-500">Configure AI settings</div>
            </div>
          </Link>
          
          <Link
            to="/settings"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <TrendingUp className="h-8 w-8 text-orange-600 mr-3" />
            <div>
              <div className="text-sm font-medium text-gray-900">View Analytics</div>
              <div className="text-sm text-gray-500">Usage statistics</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
