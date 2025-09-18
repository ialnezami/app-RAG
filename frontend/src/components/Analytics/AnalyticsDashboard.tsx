import React, { useState, useEffect } from 'react'
import {
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  MessageSquare,
  Cpu,
  HardDrive,
  Activity,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react'
import { apiService } from '../../services/api'
import Button from '../Common/Button'
import toast from 'react-hot-toast'

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  uptime: number
  timestamp: string
}

interface DatabaseMetrics {
  total_profiles: number
  total_documents: number
  total_chunks: number
  total_chat_sessions: number
  total_messages: number
  processed_documents: number
  unprocessed_documents: number
}

interface UsageMetrics {
  daily_queries: number
  weekly_queries: number
  monthly_queries: number
  average_response_time: number
  popular_models: Array<{
    provider: string
    model: string
    count: number
  }>
  active_profiles: number
}

interface AnalyticsData {
  system: SystemMetrics
  database: DatabaseMetrics
  usage: UsageMetrics
  timestamp: string
}

const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  const loadAnalytics = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await apiService.api.get('/api/v1/analytics/dashboard')
      setAnalytics(response.data)
      setLastRefresh(new Date())
    } catch (error: any) {
      setError(error.message || 'Failed to load analytics')
      toast.error('Failed to load analytics data')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadAnalytics()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAnalytics, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  const getUsageColor = (usage: number) => {
    if (usage > 90) return 'text-red-600'
    if (usage > 70) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getUsageBgColor = (usage: number) => {
    if (usage > 90) return 'bg-red-100'
    if (usage > 70) return 'bg-yellow-100'
    return 'bg-green-100'
  }

  if (isLoading && !analytics) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <div className="text-center py-8">
            <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error && !analytics) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <div className="text-center py-8">
            <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Unavailable</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={loadAnalytics}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600 mt-1">
            System performance and usage metrics
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
          <Button
            onClick={loadAnalytics}
            variant="secondary"
            size="sm"
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {analytics && (
        <>
          {/* System Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                  <p className={`text-2xl font-bold ${getUsageColor(analytics.system.cpu_usage)}`}>
                    {analytics.system.cpu_usage.toFixed(1)}%
                  </p>
                </div>
                <div className={`p-3 rounded-full ${getUsageBgColor(analytics.system.cpu_usage)}`}>
                  <Cpu className={`w-6 h-6 ${getUsageColor(analytics.system.cpu_usage)}`} />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                  <p className={`text-2xl font-bold ${getUsageColor(analytics.system.memory_usage)}`}>
                    {analytics.system.memory_usage.toFixed(1)}%
                  </p>
                </div>
                <div className={`p-3 rounded-full ${getUsageBgColor(analytics.system.memory_usage)}`}>
                  <Activity className={`w-6 h-6 ${getUsageColor(analytics.system.memory_usage)}`} />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Disk Usage</p>
                  <p className={`text-2xl font-bold ${getUsageColor(analytics.system.disk_usage)}`}>
                    {analytics.system.disk_usage.toFixed(1)}%
                  </p>
                </div>
                <div className={`p-3 rounded-full ${getUsageBgColor(analytics.system.disk_usage)}`}>
                  <HardDrive className={`w-6 h-6 ${getUsageColor(analytics.system.disk_usage)}`} />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Uptime</p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatUptime(analytics.system.uptime)}
                  </p>
                </div>
                <div className="p-3 rounded-full bg-green-100">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Database Metrics */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Database Statistics
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{analytics.database.total_profiles}</div>
                  <div className="text-sm text-gray-500">Profiles</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{analytics.database.total_documents}</div>
                  <div className="text-sm text-gray-500">Documents</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{analytics.database.total_chunks}</div>
                  <div className="text-sm text-gray-500">Text Chunks</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">{analytics.database.total_chat_sessions}</div>
                  <div className="text-sm text-gray-500">Chat Sessions</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-indigo-600">{analytics.database.total_messages}</div>
                  <div className="text-sm text-gray-500">Messages</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{analytics.database.processed_documents}</div>
                  <div className="text-sm text-gray-500">Processed</div>
                </div>
                
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-600">{analytics.database.unprocessed_documents}</div>
                  <div className="text-sm text-gray-500">Processing</div>
                </div>
              </div>
            </div>
          </div>

          {/* Usage Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Usage Trends
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Daily Queries</span>
                    <span className="text-lg font-bold text-blue-600">{analytics.usage.daily_queries}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Weekly Queries</span>
                    <span className="text-lg font-bold text-green-600">{analytics.usage.weekly_queries}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Monthly Queries</span>
                    <span className="text-lg font-bold text-purple-600">{analytics.usage.monthly_queries}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Active Profiles</span>
                    <span className="text-lg font-bold text-orange-600">{analytics.usage.active_profiles}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Avg Response Time</span>
                    <span className="text-lg font-bold text-indigo-600">{analytics.usage.average_response_time}s</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  Popular AI Models
                </h3>
                
                {analytics.usage.popular_models.length > 0 ? (
                  <div className="space-y-3">
                    {analytics.usage.popular_models.map((model, index) => (
                      <div key={`${model.provider}-${model.model}`} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                            index === 0 ? 'bg-yellow-500' :
                            index === 1 ? 'bg-gray-400' :
                            index === 2 ? 'bg-orange-500' : 'bg-gray-300'
                          }`}>
                            {index + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {model.provider.charAt(0).toUpperCase() + model.provider.slice(1)}
                            </p>
                            <p className="text-xs text-gray-500">{model.model}</p>
                          </div>
                        </div>
                        <span className="text-sm font-bold text-gray-900">{model.count} profiles</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No usage data available</p>
                )}
              </div>
            </div>
          </div>

          {/* Processing Status */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Document Processing Status
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  <div className="text-2xl font-bold text-green-600">{analytics.database.processed_documents}</div>
                  <div className="text-sm text-gray-500">Processed Documents</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {analytics.database.total_documents > 0 ? 
                      `${((analytics.database.processed_documents / analytics.database.total_documents) * 100).toFixed(1)}% of total`
                      : '0% of total'
                    }
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Clock className="w-8 h-8 text-yellow-600" />
                  </div>
                  <div className="text-2xl font-bold text-yellow-600">{analytics.database.unprocessed_documents}</div>
                  <div className="text-sm text-gray-500">Processing Queue</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {analytics.database.total_documents > 0 ? 
                      `${((analytics.database.unprocessed_documents / analytics.database.total_documents) * 100).toFixed(1)}% pending`
                      : '0% pending'
                    }
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-8 h-8 text-blue-600" />
                  </div>
                  <div className="text-2xl font-bold text-blue-600">{analytics.database.total_chunks}</div>
                  <div className="text-sm text-gray-500">Text Chunks</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {analytics.database.processed_documents > 0 ? 
                      `${Math.round(analytics.database.total_chunks / analytics.database.processed_documents)} avg per doc`
                      : 'No chunks yet'
                    }
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="secondary" size="sm" className="w-full">
                <Users className="w-4 h-4 mr-2" />
                Manage Users
              </Button>
              <Button variant="secondary" size="sm" className="w-full">
                <FileText className="w-4 h-4 mr-2" />
                View Documents
              </Button>
              <Button variant="secondary" size="sm" className="w-full">
                <MessageSquare className="w-4 h-4 mr-2" />
                Chat Sessions
              </Button>
              <Button variant="secondary" size="sm" className="w-full">
                <Settings className="w-4 h-4 mr-2" />
                System Settings
              </Button>
            </div>
          </div>

          {/* Health Status */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                System Health
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Database</p>
                    <p className="text-xs text-gray-500">Connected and healthy</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">API Services</p>
                    <p className="text-xs text-gray-500">All endpoints responding</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">AI Providers</p>
                    <p className="text-xs text-gray-500">Gemini API configured</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default AnalyticsDashboard
