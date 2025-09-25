import axios from 'axios'

// Configure axios for the backend API
const API_BASE_URL = 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const graphService = {
  // Get the complete knowledge graph
  async getGraph() {
    try {
      const response = await apiClient.get('/graph')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch graph data: ${error.message}`)
    }
  },

  // Record user feedback for adaptive learning
  async recordFeedback(feedback) {
    try {
      const response = await apiClient.post('/feedback', feedback)
      return response.data
    } catch (error) {
      throw new Error(`Failed to record feedback: ${error.message}`)
    }
  },

  // Get graph statistics and analytics
  async getStats() {
    try {
      const response = await apiClient.get('/stats')
      return response.data
    } catch (error) {
      throw new Error(`Failed to fetch stats: ${error.message}`)
    }
  },

  // Ingest new data (for future file upload feature)
  async ingestData(formData) {
    try {
      const response = await apiClient.post('/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      throw new Error(`Failed to ingest data: ${error.message}`)
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await apiClient.get('/')
      return response.data
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`)
    }
  }
}

export default apiClient
