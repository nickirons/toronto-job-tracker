import { RefreshCw, Settings } from 'lucide-react'
import { useStats, useRefresh } from '../hooks/useJobs'

interface HeaderProps {
  onOpenSettings: () => void
}

export default function Header({ onOpenSettings }: HeaderProps) {
  const { data: stats } = useStats()
  const refresh = useRefresh()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🍁</span>
          <h1 className="text-xl font-semibold text-gray-900">
            Toronto Job Tracker
          </h1>
        </div>

        <div className="flex items-center gap-4">
          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>{stats?.total || 0} jobs</span>
            {stats?.new && stats.new > 0 && (
              <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                {stats.new} new
              </span>
            )}
            {stats?.saved && stats.saved > 0 && (
              <span className="text-yellow-600">
                ⭐ {stats.saved} saved
              </span>
            )}
          </div>

          {/* Refresh button */}
          <button
            onClick={() => refresh.mutate()}
            disabled={refresh.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw
              className={`w-4 h-4 ${refresh.isPending ? 'animate-spin' : ''}`}
            />
            {refresh.isPending ? 'Refreshing...' : 'Refresh'}
          </button>

          {/* Settings button */}
          <button
            onClick={onOpenSettings}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Last refresh time */}
      {stats?.last_refresh && (
        <p className="text-xs text-gray-500 mt-2">
          Last refresh: {new Date(stats.last_refresh).toLocaleString()}
        </p>
      )}
    </header>
  )
}
