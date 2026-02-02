import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export type JobStatus = 'new' | 'reviewed' | 'applied' | 'rejected'

export interface Job {
  id: string
  title: string
  company: string
  location: string
  url: string
  apply_url: string | null  // Direct application portal URL (Workday, Greenhouse, Lever, etc.)
  source: string
  salary: string | null
  description: string | null
  posted_date: string | null
  added_at: string | null
  duration: string | null
  status: JobStatus
  is_saved: boolean
  is_startup: boolean
  is_new: boolean
}

export interface Stats {
  total: number
  new: number
  reviewed: number
  applied: number
  rejected: number
  saved: number
  by_status: Record<string, number>
  by_source: Record<string, number>
  last_refresh: string | null
}

export interface Settings {
  rapidapi_key: string
  rapidapi_key_set: boolean
  refresh_interval_minutes: number
}

// Jobs API
export const getJobs = async (params?: {
  search?: string
  source?: string
  status?: string
  saved?: boolean
  startup?: boolean
}): Promise<Job[]> => {
  const { data } = await api.get('/jobs', { params })
  return data
}

export const getJob = async (id: string): Promise<Job> => {
  const { data } = await api.get(`/jobs/${id}`)
  return data
}

export const updateJob = async (
  id: string,
  update: { status?: JobStatus; is_saved?: boolean }
): Promise<Job> => {
  const { data } = await api.patch(`/jobs/${id}`, update)
  return data
}

export const deleteJob = async (id: string): Promise<void> => {
  await api.delete(`/jobs/${id}`)
}

export const refreshJobs = async (): Promise<{
  message: string
  new_jobs: number
  total_jobs: number
  last_refresh: string
}> => {
  const { data } = await api.post('/jobs/refresh')
  return data
}

export const clearAllJobs = async (): Promise<void> => {
  await api.delete('/jobs')
}

// Stats API
export const getStats = async (): Promise<Stats> => {
  const { data } = await api.get('/jobs/stats')
  return data
}

// Settings API
export const getSettings = async (): Promise<Settings> => {
  const { data } = await api.get('/settings')
  return data
}

export const updateSettings = async (update: {
  rapidapi_key?: string
  refresh_interval_minutes?: number
}): Promise<Settings> => {
  const { data } = await api.put('/settings', update)
  return data
}

export default api
