/**
 * Composable for making authenticated API calls with Clerk
 */
import { useAuth } from '@clerk/vue'

export function useApi() {
  const { getToken } = useAuth()
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  /**
   * Make an authenticated API request
   * @param {string} path - API endpoint path (e.g., '/projects/my-projects')
   * @param {RequestInit} options - Fetch options (method, body, headers, etc.)
   * @returns {Promise<any>} - Response data
   */
  async function apiFetch(path, options = {}) {
    try {
      // Get Clerk session token
      const token = await getToken()
      
      if (!token) {
        throw new Error('Not authenticated - please sign in')
      }

      // Make request with Authorization header
      const response = await fetch(`${baseURL}${path}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `API error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  /**
   * GET request
   */
  async function get(path) {
    return apiFetch(path, { method: 'GET' })
  }

  /**
   * POST request
   */
  async function post(path, data) {
    return apiFetch(path, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  /**
   * PUT request
   */
  async function put(path, data) {
    return apiFetch(path, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  /**
   * DELETE request
   */
  async function del(path) {
    return apiFetch(path, { method: 'DELETE' })
  }

  return {
    apiFetch,
    get,
    post,
    put,
    del,
  }
}
