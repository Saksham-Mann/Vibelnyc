/**
 * Vibelnyc API Client module.
 * Communicates with the FastAPI recommendation backend.
 */

import {
  RecommendResponse,
  SearchResultItem,
  SearchResponse,
} from '@/types/music'

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Custom error class capturing HTTP status and backend message details.
 */
export class ApiError extends Error {
  status: number
  detail: string

  /**
   * Constructs an ApiError instance.
   * @param status HTTP response status code.
   * @param detail Error explanation from server.
   */
  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

/**
 * Performs autocomplete search for track titles and artists against the FastAPI backend.
 * @param query Search query string entered by the user.
 * @param limit Maximum number of autocomplete suggestions to return (default: 5).
 * @returns Promise resolving to a list of matching search results.
 * @throws {ApiError} If the server returns a non-2xx status code.
 */
export async function searchTracks(
  query: string,
  limit: number = 5
): Promise<SearchResultItem[]> {
  if (!query || !query.trim()) {
    return []
  }

  const encodedQuery = encodeURIComponent(query.trim())
  const url = `${API_BASE_URL}/api/search?q=${encodedQuery}&limit=${limit}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      response.status,
      errorData.detail || `Search failed with status ${response.status}`
    )
  }

  const data: SearchResponse = await response.json()
  return data.results
}

/**
 * Requests track recommendations based on a seed track title and optional artist name.
 * @param trackName Title of the seed track to match.
 * @param artistName Optional artist name to narrow down seed track selection.
 * @param nResults Number of candidate recommendations to retrieve (default: 3).
 * @returns Promise resolving to the recommendation response including seed track and cluster info.
 * @throws {ApiError} With status 404 if the seed track is not found in the dataset.
 */
export async function recommendByTrack(
  trackName: string,
  artistName?: string,
  nResults: number = 3
): Promise<RecommendResponse> {
  const url = `${API_BASE_URL}/api/recommend`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      track_name: trackName,
      artist_name: artistName || null,
      n_results: nResults,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      response.status,
      errorData.detail || `Recommendation failed with status ${response.status}`
    )
  }

  return response.json()
}

/**
 * Requests recommendations based on a predefined mood archetype vector.
 * @param mood Mood preset identifier ('melancholy', 'high-energy', 'chill', 'pop').
 * @param nResults Number of candidate recommendations to retrieve (default: 3).
 * @returns Promise resolving to the recommendation response for the selected mood.
 * @throws {ApiError} If the mood key is invalid or server encounters an error.
 */
export async function recommendByMood(
  mood: string,
  nResults: number = 3
): Promise<RecommendResponse> {
  const normalizedMood = mood.trim().toLowerCase().replace(/\s+/g, '-')
  const url = `${API_BASE_URL}/api/recommend/mood`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      mood: normalizedMood,
      n_results: nResults,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      response.status,
      errorData.detail || `Mood recommendation failed with status ${response.status}`
    )
  }

  return response.json()
}

/**
 * Checks connectivity to the FastAPI backend.
 * @returns Promise resolving to true if backend is online and models are loaded, false otherwise.
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })
    if (!response.ok) return false
    const data = await response.json()
    return data.status === 'healthy' && data.engine_loaded === true
  } catch {
    return false
  }
}
