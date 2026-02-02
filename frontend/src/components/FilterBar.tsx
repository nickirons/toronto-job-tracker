import { Search } from 'lucide-react'
import { useStats } from '../hooks/useJobs'

interface FilterBarProps {
  search: string
  onSearchChange: (value: string) => void
  filter: string
  onFilterChange: (value: string) => void
  source: string
  onSourceChange: (value: string) => void
}

const STATUS_FILTERS = [
  { id: 'new', label: 'New', color: 'bg-blue-600', hoverColor: 'hover:bg-blue-700' },
  { id: 'reviewed', label: 'Reviewed', color: 'bg-gray-600', hoverColor: 'hover:bg-gray-700' },
  { id: 'applied', label: 'Applied', color: 'bg-green-600', hoverColor: 'hover:bg-green-700' },
  { id: 'rejected', label: 'Rejected', color: 'bg-red-600', hoverColor: 'hover:bg-red-700' },
  { id: 'saved', label: 'Saved', color: 'bg-yellow-600', hoverColor: 'hover:bg-yellow-700' },
  { id: 'all', label: 'All', color: 'bg-purple-600', hoverColor: 'hover:bg-purple-700' },
]

export default function FilterBar({
  search,
  onSearchChange,
  filter,
  onFilterChange,
  source,
  onSourceChange,
}: FilterBarProps) {
  const { data: stats } = useStats()

  const sources = stats?.by_source
    ? ['All', ...Object.keys(stats.by_source)]
    : ['All']

  // Get count for each filter
  const getCount = (filterId: string): number => {
    if (!stats) return 0
    switch (filterId) {
      case 'new': return stats.new || 0
      case 'reviewed': return stats.reviewed || 0
      case 'applied': return stats.applied || 0
      case 'rejected': return stats.rejected || 0
      case 'saved': return stats.saved || 0
      case 'all': return stats.total || 0
      default: return 0
    }
  }

  return (
    <div className="p-4 border-b border-gray-200 space-y-3">
      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search jobs..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Status filter tabs */}
      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((f) => {
          const count = getCount(f.id)
          const isSelected = filter === f.id
          return (
            <button
              key={f.id}
              onClick={() => onFilterChange(f.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center gap-1.5 ${
                isSelected
                  ? `${f.color} text-white`
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {f.label}
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                isSelected ? 'bg-white/20' : 'bg-gray-200'
              }`}>
                {count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Source dropdown */}
      <select
        value={source}
        onChange={(e) => onSourceChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {sources.map((s) => (
          <option key={s} value={s === 'All' ? '' : s}>
            {s === 'All' ? 'All Sources' : s}{' '}
            {s !== 'All' && stats?.by_source?.[s]
              ? `(${stats.by_source[s]})`
              : ''}
          </option>
        ))}
      </select>
    </div>
  )
}
