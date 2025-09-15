import { useState, useEffect } from 'react'
import apiService from '../services/api'

export function useApi() {
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const connected = await apiService.testConnection()
        setIsConnected(connected)
        setError(null)
      } catch (err: any) {
        setIsConnected(false)
        setError(err.message || 'Connection failed')
      }
    }

    // Check connection on mount
    checkConnection()

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000)

    return () => clearInterval(interval)
  }, [])

  const execute = async <T>(apiCall: () => Promise<T>): Promise<T | null> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await apiCall()
      setIsLoading(false)
      return result
    } catch (err: any) {
      setIsLoading(false)
      setError(err.message || 'An error occurred')
      return null
    }
  }

  return {
    isConnected,
    isLoading,
    error,
    execute,
    api: apiService
  }
}
