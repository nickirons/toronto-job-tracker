import {
  MapPin,
  Clock,
  DollarSign,
  Calendar,
  ExternalLink,
  Star,
  StarOff,
  Check,
  X,
  Eye,
} from 'lucide-react'
import { Job, JobStatus } from '../lib/api'
import { useUpdateJob } from '../hooks/useJobs'
import { formatDistanceToNow, format } from 'date-fns'
import { useEffect } from 'react'

interface JobDetailProps {
  job: Job | null
}

// Source badge colors
const SOURCE_COLORS: Record<string, string> = {
  JSearch: 'bg-purple-100 text-purple-700',
  GitHub: 'bg-gray-100 text-gray-700',
  Indeed: 'bg-blue-100 text-blue-700',
  RemoteOK: 'bg-green-100 text-green-700',
  Arbeitnow: 'bg-orange-100 text-orange-700',
}

export default function JobDetail({ job }: JobDetailProps) {
  const updateJob = useUpdateJob()

  // Mark as reviewed when job is selected (if currently "new")
  useEffect(() => {
    if (job && job.status === 'new') {
      updateJob.mutate({ id: job.id, update: { status: 'reviewed' } })
    }
  }, [job?.id])

  if (!job) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-6">
        <div className="text-4xl mb-4">👈</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Select a job to view details
        </h3>
        <p className="text-gray-500 text-sm">
          Click on a job from the list to see more information.
        </p>
      </div>
    )
  }

  const sourceColor = SOURCE_COLORS[job.source] || 'bg-gray-100 text-gray-700'

  const handleToggleSave = () => {
    updateJob.mutate({ id: job.id, update: { is_saved: !job.is_saved } })
  }

  const handleSetStatus = (status: JobStatus) => {
    updateJob.mutate({ id: job.id, update: { status } })
  }

  const handleApply = () => {
    // Opens the job listing URL (Indeed, LinkedIn, etc.)
    window.open(job.url, '_blank')
  }

  const handleApplyDirect = () => {
    // Opens the direct application portal (Workday, Greenhouse, Lever, etc.)
    if (job.apply_url) {
      window.open(job.apply_url, '_blank')
      // Auto-mark as applied when clicking apply direct
      if (job.status !== 'applied') {
        handleSetStatus('applied')
      }
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="mb-6">
        {/* Badges */}
        <div className="flex items-center gap-2 mb-3">
          {job.is_new && (
            <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
              NEW
            </span>
          )}
          {job.is_startup && (
            <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
              STARTUP
            </span>
          )}
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${sourceColor}`}>
            {job.source}
          </span>
        </div>

        {/* Title and company */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{job.title}</h1>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            {job.company.charAt(0).toUpperCase()}
          </div>
          <span className="text-lg text-gray-700">{job.company}</span>
        </div>
      </div>

      {/* Info cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <InfoCard
          icon={<MapPin className="w-4 h-4" />}
          label="Location"
          value={job.location}
        />
        {job.duration && (
          <InfoCard
            icon={<Clock className="w-4 h-4" />}
            label="Duration"
            value={job.duration}
          />
        )}
        {job.salary && (
          <InfoCard
            icon={<DollarSign className="w-4 h-4" />}
            label="Salary"
            value={job.salary}
          />
        )}
        {job.posted_date && (
          <InfoCard
            icon={<Calendar className="w-4 h-4" />}
            label="Posted"
            value={formatDistanceToNow(new Date(job.posted_date), {
              addSuffix: true,
            })}
          />
        )}
      </div>

      {/* Status indicator */}
      <div className="mb-4">
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${
          job.status === 'new' ? 'bg-blue-100 text-blue-700' :
          job.status === 'reviewed' ? 'bg-gray-100 text-gray-700' :
          job.status === 'applied' ? 'bg-green-100 text-green-700' :
          'bg-red-100 text-red-700'
        }`}>
          {job.status === 'new' && <Eye className="w-3.5 h-3.5" />}
          {job.status === 'reviewed' && <Eye className="w-3.5 h-3.5" />}
          {job.status === 'applied' && <Check className="w-3.5 h-3.5" />}
          {job.status === 'rejected' && <X className="w-3.5 h-3.5" />}
          {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
        </span>
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2 mb-6">
        {/* Apply button - opens job listing */}
        <button
          onClick={handleApply}
          className="flex items-center gap-2 px-4 py-2 text-white rounded-lg font-medium transition-colors bg-blue-600 hover:bg-blue-700"
          title="Opens job listing"
        >
          <ExternalLink className="w-4 h-4" />
          Apply
        </button>

        {/* Apply Direct button - opens application portal (only shown if available) */}
        {job.apply_url && (
          <button
            onClick={handleApplyDirect}
            className="flex items-center gap-2 px-4 py-2 text-white rounded-lg font-medium transition-colors bg-green-600 hover:bg-green-700"
            title="Opens direct application portal"
          >
            <ExternalLink className="w-4 h-4" />
            Apply Direct
          </button>
        )}

        {/* Save button */}
        <button
          onClick={handleToggleSave}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            job.is_saved
              ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {job.is_saved ? (
            <>
              <Star className="w-4 h-4 fill-current" />
              Saved
            </>
          ) : (
            <>
              <StarOff className="w-4 h-4" />
              Save
            </>
          )}
        </button>

        {/* Status action buttons */}
        {job.status !== 'applied' && (
          <button
            onClick={() => handleSetStatus('applied')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
          >
            <Check className="w-4 h-4" />
            Mark Applied
          </button>
        )}

        {job.status !== 'rejected' && (
          <button
            onClick={() => handleSetStatus('rejected')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
          >
            <X className="w-4 h-4" />
            Not Interested
          </button>
        )}

        {(job.status === 'applied' || job.status === 'rejected') && (
          <button
            onClick={() => handleSetStatus('reviewed')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
          >
            <Eye className="w-4 h-4" />
            Move to Reviewed
          </button>
        )}
      </div>

      {/* Description */}
      {job.description && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Job Description
          </h2>
          <div
            className="prose prose-sm max-w-none text-gray-700"
            dangerouslySetInnerHTML={{
              __html: job.description
                .replace(/\n/g, '<br/>')
                .replace(/&nbsp;/g, ' '),
            }}
          />
        </div>
      )}

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
        {job.added_at && (
          <p>
            Added to tracker:{' '}
            {format(new Date(job.added_at), 'MMM d, yyyy h:mm a')}
          </p>
        )}
      </div>
    </div>
  )
}

// Info card component
function InfoCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <div className="flex items-center gap-2 text-gray-500 mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="text-sm font-medium text-gray-900">{value}</p>
    </div>
  )
}
