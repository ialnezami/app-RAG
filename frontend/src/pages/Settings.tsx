import React, { useState, useEffect } from 'react'
import {
  Settings as SettingsIcon,
  Shield,
  Database,
  Zap,
  Monitor,
  Bell,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Lock,
  Users,
  BarChart3,
  FileText
} from 'lucide-react'
import { apiService } from '../services/api'
import Button from '../components/Common/Button'
import AnalyticsDashboard from '../components/Analytics/AnalyticsDashboard'
import toast from 'react-hot-toast'

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'general' | 'security' | 'analytics' | 'system'>('general')
  const [settings, setSettings] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [authStatus, setAuthStatus] = useState<any>(null)

  useEffect(() => {
    loadSettings()
    loadAuthStatus()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await apiService.getStatus()
      setSettings(response)
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const loadAuthStatus = async () => {
    try {
      const response = await apiService.api.get('/api/v1/auth/status')
      setAuthStatus(response.data)
    } catch (error) {
      console.error('Failed to load auth status:', error)
      setAuthStatus({ auth_enabled: false, auth_type: 'disabled' })
    }
  }

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'system', label: 'System', icon: Monitor }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">
            Configure your RAG application settings and monitor system health.
          </p>
        </div>
        <Button
          onClick={loadSettings}
          variant="secondary"
          size="sm"
          disabled={isLoading}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* General Settings Tab */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Application Configuration</h3>
                
                {settings && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Environment
                        </label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            settings.environment === 'production' ? 'bg-red-100 text-red-800' :
                            settings.environment === 'staging' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {settings.environment}
                          </span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Debug Mode
                        </label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            settings.configuration?.debug_mode ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {settings.configuration?.debug_mode ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Max File Size
                        </label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md">
                          {Math.round((settings.configuration?.max_file_size || 0) / 1024 / 1024)} MB
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Allowed File Types
                        </label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md">
                          <div className="flex flex-wrap gap-1">
                            {(settings.configuration?.allowed_file_types || []).map((type: string) => (
                              <span key={type} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {type}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          CORS Origins
                        </label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md max-h-20 overflow-y-auto">
                          <div className="space-y-1">
                            {(settings.configuration?.cors_origins || []).map((origin: string, index: number) => (
                              <div key={index} className="text-xs text-gray-600">{origin}</div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Security Settings Tab */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Security Configuration
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                      <div className="flex items-center">
                        <Lock className="w-5 h-5 text-blue-600 mr-2" />
                        <div>
                          <h4 className="text-sm font-medium text-blue-900">
                            Authentication Status
                          </h4>
                          <p className="text-xs text-blue-700">
                            {authStatus?.auth_enabled ? 'Enabled' : 'Disabled'} • {authStatus?.auth_type || 'Unknown'}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-green-50 border border-green-200 rounded-md p-4">
                      <div className="flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        <div>
                          <h4 className="text-sm font-medium text-green-900">
                            Rate Limiting
                          </h4>
                          <p className="text-xs text-green-700">
                            Active protection against abuse
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Security Features</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between py-2">
                          <span className="text-sm text-gray-600">CORS Protection</span>
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <span className="text-sm text-gray-600">Input Validation</span>
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <span className="text-sm text-gray-600">SQL Injection Protection</span>
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="flex items-center justify-between py-2">
                          <span className="text-sm text-gray-600">File Type Validation</span>
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <AnalyticsDashboard />
          )}

          {/* System Tab */}
          {activeTab === 'system' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  System Management
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Database Operations</h4>
                      <div className="space-y-2">
                        <Button variant="secondary" size="sm" className="w-full">
                          <Database className="w-4 h-4 mr-2" />
                          Backup Database
                        </Button>
                        <Button variant="secondary" size="sm" className="w-full">
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Optimize Database
                        </Button>
                        <Button variant="secondary" size="sm" className="w-full">
                          <BarChart3 className="w-4 h-4 mr-2" />
                          View Query Stats
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">System Info</h4>
                      {settings && (
                        <div className="bg-gray-50 border border-gray-300 rounded-md p-3 space-y-2">
                          <div className="flex justify-between">
                            <span className="text-xs text-gray-600">Service:</span>
                            <span className="text-xs font-medium">{settings.service}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-xs text-gray-600">Version:</span>
                            <span className="text-xs font-medium">{settings.version}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-xs text-gray-600">Status:</span>
                            <span className={`text-xs font-medium ${
                              settings.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {settings.status}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Settings
