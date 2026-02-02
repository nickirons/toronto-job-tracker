import { Job } from '../lib/api'
import JobCard from './JobCard'

interface JobListProps {
  jobs: Job[]
  selectedJobId: string | null
  onSelectJob: (job: Job) => void
  isLoading: boolean
}

export default function JobList({
  jobs,
  selectedJobId,
  onSelectJob,
  isLoading,
}: JobListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading jobs...</div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-6">
        <div className="text-4xl mb-4">🔍</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No jobs found
        </h3>
        <p className="text-gray-500 text-sm">
          Try adjusting your filters or click Refresh to fetch new jobs.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-y-auto h-full">
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          isSelected={job.id === selectedJobId}
          onClick={() => onSelectJob(job)}
        />
      ))}
    </div>
  )
}
