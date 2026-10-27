import { API_BASE_URL } from './apiClient.js'

/**
 * Service to interact with the backend Documents API and Cloudinary uploads.
 */
export const documentService = {
  /**
   * Upload a document file to Cloudinary and store metadata + URL in database
   * @param {FormData} formData Contains file, name, category, scope, etc.
   */
  async uploadDocument(formData) {
    const url = `${API_BASE_URL}/documents/upload`
    const response = await fetch(url, {
      method: 'POST',
      body: formData, // fetch will set multipart/form-data boundary automatically
    })

    if (!response.ok) {
      let errorDetail = `Upload failed with status ${response.status}`
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
      throw new Error(errorDetail)
    }

    return response.json()
  },

  /**
   * List documents with optional filters
   */
  async listDocuments({ scope, category, status, query, skip = 0, limit = 50 } = {}) {
    const params = new URLSearchParams()
    if (scope && scope !== 'All') params.append('scope', scope)
    if (category && category !== 'All') params.append('category', category)
    if (status && status !== 'All') params.append('status', status)
    if (query && query.trim()) params.append('query', query.trim())
    if (skip > 0) params.append('skip', String(skip))
    if (limit) params.append('limit', String(limit))

    const qs = params.toString() ? `?${params.toString()}` : ''
    const response = await fetch(`${API_BASE_URL}/documents${qs}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.statusText}`)
    }
    return response.json()
  },

  /**
   * Fetch single document by ID
   */
  async getDocument(documentId) {
    const response = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(documentId)}`)
    if (!response.ok) {
      throw new Error(`Document not found: ${response.statusText}`)
    }
    return response.json()
  },

  /**
   * Update document details or status
   */
  async updateDocument(documentId, updates) {
    const response = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(documentId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    })
    if (!response.ok) {
      throw new Error(`Failed to update document: ${response.statusText}`)
    }
    return response.json()
  },

  /**
   * Delete document from DB and Cloudinary
   */
  async deleteDocument(documentId) {
    const response = await fetch(`${API_BASE_URL}/documents/${encodeURIComponent(documentId)}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error(`Failed to delete document: ${response.statusText}`)
    }
    return response.json()
  },
}

export default documentService
