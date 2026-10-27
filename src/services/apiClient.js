const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

/**
 * Universal API request wrapper
 */
export async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http')
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`
    try {
      const errJson = await response.json()
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string'
          ? errJson.detail
          : JSON.stringify(errJson.detail)
      }
    } catch {
      // Body not JSON
    }
    const error = new Error(errorDetail)
    error.status = response.status
    throw error
  }

  return response.json()
}

export { API_BASE_URL }
