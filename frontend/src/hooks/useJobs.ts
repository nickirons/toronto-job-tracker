import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getJobs,
  getStats,
  updateJob,
  refreshJobs,
  getSettings,
  updateSettings,
  clearAllJobs,
  Job,
} from '../lib/api'

// Jobs hook
export function useJobs(params?: {
  search?: string
  source?: string
  saved?: boolean
  new_only?: boolean
  startup?: boolean
}) {
  return useQuery({
    queryKey: ['jobs', params],
    queryFn: () => getJobs(params),
  })
}

// Stats hook
export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

// Settings hook
export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: getSettings,
  })
}

// Update job mutation
export function useUpdateJob() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      update,
    }: {
      id: string
      update: { is_viewed?: boolean; is_saved?: boolean }
    }) => updateJob(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

// Refresh mutation
export function useRefresh() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: refreshJobs,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

// Update settings mutation
export function useUpdateSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })
}

// Clear all jobs mutation
export function useClearJobs() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: clearAllJobs,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}
