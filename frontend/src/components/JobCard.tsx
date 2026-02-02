import { MapPin, Clock, Check, X } from 'lucide-react'
import { Job } from '../lib/api'
import { useUpdateJob } from '../hooks/useJobs'
import { formatDistanceToNow } from 'date-fns'

interface JobCardProps {
  job: Job
  isSelected: boolean
  onClick: () => void
}

// Source badge colors
const SOURCE_COLORS: Record<string, string> = {
  JSearch: 'bg-purple-100 text-purple-700',
  GitHub: 'bg-gray-100 text-gray-700',
  Indeed: 'bg-blue-100 text-blue-700',
  RemoteOK: 'bg-green-100 text-green-700',
  Arbeitnow: 'bg-orange-100 text-orange-700',
}

// Status badge colors and labels
const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  new: { bg: 'bg-blue-600', text: 'text-white', label: 'NEW' },
  reviewed: { bg: 'bg-gray-200', text: 'text-gray-600', label: 'Reviewed' },
  applied: { bg: 'bg-green-600', text: 'text-white', label: 'Applied' },
  rejected: { bg: 'bg-red-100', text: 'text-red-600', label: 'Rejected' },
}

export default function JobCard({ job, isSelected, onClick }: JobCardProps) {
  const sourceColor = SOURCE_COLORS[job.source] || 'bg-gray-100 text-gray-700'
  const statusConfig = STATUS_CONFIG[job.status] || STATUS_CONFIG.reviewed
  const updateJob = useUpdateJob()

  const addedDate = job.added_at
    ? formatDistanceToNow(new Date(job.added_at), { addSuffix: true })
    : ''

  // Dim rejected jobs
  const isRejected = job.status === 'rejected'

  const handleReject = (e: React.MouseEvent) => {
    e.stopPropagation() // Don't trigger card click
    updateJob.mutate({ id: job.id, update: { status: 'rejected' } })
  }

  const handleUnreject = (e: React.MouseEvent) => {
    e.stopPropagation()
    updateJob.mutate({ id: job.id, update: { status: 'reviewed' } })
  }

  return (
    <div
      onClick={onClick}
      className={`p-4 border-b border-gray-100 cursor-pointer transition-colors group ${
        isSelected
          ? 'bg-blue-50 border-l-4 border-l-blue-600'
          : 'hover:bg-gray-50'
      } ${job.status === 'new' ? 'bg-blue-50/30' : ''} ${isRejected ? 'opacity-50' : ''}`}
    >
      {/* Header with badges */}
      <div className="flex items-start justify-between gap-2 mb-1">
        <h3
          className={`font-medium text-gray-900 line-clamp-1 flex-1 ${
            job.status === 'new' ? 'font-semibold' : ''
          } ${isRejected ? 'line-through' : ''}`}
        >
          {job.title}
        </h3>
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Quick reject/unreject button */}
          {job.status !== 'rejected' && job.status !== 'applied' && (
            <button
              onClick={handleReject}
              className="p-1 rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-100 text-gray-400 hover:text-red-600 transition-all"
              title="Not interested"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          {job.status === 'rejected' && (
            <button
              onClick={handleUnreject}
              className="p-1 rounded-full hover:bg-gray-200 text-gray-400 hover:text-gray-600 transition-all"
              title="Move back to reviewed"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          {/* Status badge */}
          <span className={`px-2 py-0.5 text-xs font-medium rounded-full flex items-center gap-1 ${statusConfig.bg} ${statusConfig.text}`}>
            {job.status === 'applied' && <Check className="w-3 h-3" />}
            {job.status === 'rejected' && <X className="w-3 h-3" />}
            {statusConfig.label}
          </span>
          {job.is_saved && <span className="text-yellow-500">⭐</span>}
        </div>
      </div>

      {/* Company */}
      <p className="text-sm text-gray-600 mb-2">{job.company}</p>

      {/* Meta info */}
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          {job.location}
        </span>
        {job.duration && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {job.duration}
          </span>
        )}
      </div>

      {/* Footer with source and date */}
      <div className="flex items-center justify-between mt-2">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 text-xs rounded ${sourceColor}`}>
            {job.source}
          </span>
          {job.is_startup && (
            <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded">
              Startup
            </span>
          )}
        </div>
        {addedDate && (
          <span className="text-xs text-gray-400">{addedDate}</span>
        )}
      </div>
    </div>
  )
}
