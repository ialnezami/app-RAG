import React from 'react'
import { Settings as SettingsIcon, Database, Cpu, Globe } from 'lucide-react'
import { useApi } from '../hooks/useApi'

const Settings: React.FC = () => {
  const { isConnected, execute, api } = useApi()

  const handleTestConnection = async () => {
    await execute(() => api.testConnection())
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* System Status */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <SettingsIcon className="h-6 w-6 text-gray-600 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Connection</span>
              <div className="flex items-center">
                <div className={`h-2 w-2 rounded-full mr-2 ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <button
              onClick={handleTestConnection}
              className="btn btn-outline btn-sm"
            >
              Test Connection
            </button>
          </div>
        </div>

        {/* Database Settings */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Database className="h-6 w-6 text-gray-600 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">Database</h3>
          </div>
          
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              PostgreSQL with pgvector extension
            </div>
            <div className="text-sm text-gray-500">
              Vector similarity search enabled
            </div>
          </div>
        </div>

        {/* AI Providers */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Cpu className="h-6 w-6 text-gray-600 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">AI Providers</h3>
          </div>
          
          <div className="space-y-2">
            <div className="text-sm text-gray-600">Available providers:</div>
            <div className="text-sm text-gray-500">
              OpenAI, Google Gemini, Anthropic Claude
            </div>
          </div>
        </div>

        {/* Network Settings */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Globe className="h-6 w-6 text-gray-600 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">Network</h3>
          </div>
          
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              WebSocket connections enabled
            </div>
            <div className="text-sm text-gray-500">
              Real-time chat support
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
