import { useState, useEffect } from 'react'
import { X, Eye, EyeOff, Trash2 } from 'lucide-react'
import { useSettings, useUpdateSettings, useClearJobs, useStats } from '../hooks/useJobs'

interface SettingsProps {
  isOpen: boolean
  onClose: () => void
}

export default function Settings({ isOpen, onClose }: SettingsProps) {
  const { data: settings } = useSettings()
  const { data: stats } = useStats()
  const updateSettings = useUpdateSettings()
  const clearJobs = useClearJobs()

  const [apiKey, setApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState(15)

  useEffect(() => {
    if (settings) {
      setApiKey(settings.rapidapi_key_set ? '••••••••••••' : '')
      setRefreshInterval(settings.refresh_interval_minutes)
    }
  }, [settings])

  if (!isOpen) return null

  const handleSaveApiKey = () => {
    if (apiKey && !apiKey.includes('•')) {
      updateSettings.mutate({ rapidapi_key: apiKey })
    }
  }

  const handleSaveInterval = () => {
    updateSettings.mutate({ refresh_interval_minutes: refreshInterval })
  }

  const handleClearJobs = () => {
    if (confirm('Are you sure you want to delete all jobs? This cannot be undone.')) {
      clearJobs.mutate()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              RapidAPI Key
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your RapidAPI key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showApiKey ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              <button
                onClick={handleSaveApiKey}
                disabled={!apiKey || apiKey.includes('•')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Save
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Get your free API key from{' '}
              <a
                href="https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                RapidAPI JSearch
              </a>
            </p>
            {settings?.rapidapi_key_set && (
              <p className="mt-1 text-xs text-green-600">✓ API key configured</p>
            )}
          </div>

          {/* Refresh Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-refresh Interval
            </label>
            <div className="flex gap-2">
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={5}>Every 5 minutes</option>
                <option value={15}>Every 15 minutes</option>
                <option value={30}>Every 30 minutes</option>
                <option value={60}>Every hour</option>
              </select>
              <button
                onClick={handleSaveInterval}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Save
              </button>
            </div>
          </div>

          {/* Data Management */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Management
            </label>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {stats?.total || 0} jobs stored
                  </p>
                  <p className="text-xs text-gray-500">
                    {stats?.saved || 0} saved, {stats?.new || 0} new
                  </p>
                </div>
              </div>
              <button
                onClick={handleClearJobs}
                className="flex items-center gap-2 px-4 py-2 text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Clear All Jobs
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <p className="text-xs text-gray-500 text-center">
            Toronto Job Tracker v1.0 • Built for 3rd year CS students 🎓
          </p>
        </div>
      </div>
    </div>
  )
}
