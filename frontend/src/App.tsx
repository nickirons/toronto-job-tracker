import { useState, useMemo } from 'react'
import { useJobs } from './hooks/useJobs'
import { Job } from './lib/api'
import Header from './components/Header'
import FilterBar from './components/FilterBar'
import JobList from './components/JobList'
import JobDetail from './components/JobDetail'
import Settings from './components/Settings'

function App() {
  // State
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [source, setSource] = useState('')
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)

  // Build query params based on filters
  const queryParams = useMemo(() => {
    const params: {
      search?: string
      source?: string
      status?: string
      saved?: boolean
      startup?: boolean
    } = {}

    if (search) params.search = search
    if (source) params.source = source

    switch (filter) {
      case 'new':
      case 'reviewed':
      case 'applied':
      case 'rejected':
        params.status = filter
        break
      case 'saved':
        params.saved = true
        break
      // 'all' - no filter
    }

    return params
  }, [search, filter, source])

  // Fetch jobs
  const { data: jobs = [], isLoading } = useJobs(queryParams)

  // Handle job selection
  const handleSelectJob = (job: Job) => {
    setSelectedJob(job)
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <Header onOpenSettings={() => setSettingsOpen(true)} />

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Job list */}
        <div className="w-[400px] bg-white border-r border-gray-200 flex flex-col">
          <FilterBar
            search={search}
            onSearchChange={setSearch}
            filter={filter}
            onFilterChange={setFilter}
            source={source}
            onSourceChange={setSource}
          />
          <div className="flex-1 overflow-hidden">
            <JobList
              jobs={jobs}
              selectedJobId={selectedJob?.id || null}
              onSelectJob={handleSelectJob}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Right panel - Job detail */}
        <div className="flex-1 bg-white">
          <JobDetail job={selectedJob} />
        </div>
      </div>

      {/* Settings modal */}
      <Settings isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  )
}

export default App
