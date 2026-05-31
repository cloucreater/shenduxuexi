import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface DetectionResult {
  bbox: [number, number, number, number]
  label: string
  label_en: string
  confidence: number
}

export interface DetectionRecord {
  id: string
  image_url?: string
  result_image?: string
  detections: DetectionResult[]
  detection_time: number
  created_at: string
}

export const useDetectionStore = defineStore('detection', () => {
  const isLoading = ref(false)
  const currentDetection = ref<DetectionRecord | null>(null)
  const history = ref<DetectionRecord[]>([])

  async function detectImage(file: File) {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post<DetectionRecord>('/detect/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      currentDetection.value = response.data
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  async function detectVideo(file: File, onProgress?: (progress: number) => void) {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/detect/video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  async function fetchHistory(page = 1, limit = 10) {
    const response = await api.get<{ records: DetectionRecord[]; total: number }>('/history', {
      params: { page, limit }
    })
    history.value = response.data.records
    return response.data
  }

  return {
    isLoading,
    currentDetection,
    history,
    detectImage,
    detectVideo,
    fetchHistory
  }
})
