/**
 * Vibelnyc Domain and API Data Types.
 * Defines track structures, audio metric dimensions, mood categories, and backend responses.
 */

/**
 * Supported mood preset identifiers.
 */
export type Mood = 'MELANCHOLY' | 'HIGH ENERGY' | 'CHILL' | 'POP'

/**
 * Configuration options for rendering mood filter buttons.
 */
export interface MoodOption {
  /** Display name of the mood. */
  name: Mood
  /** CSS class applied to the button for styling and active states. */
  className: string
}

/**
 * Raw and percentage audio features on a 0-100 scale.
 */
export interface TrackFeatures {
  /** Energy level of the track (0.0 - 100.0). */
  energy: number
  /** Musical valence or emotional positivity (0.0 - 100.0). */
  valence: number
  /** Danceability index (0.0 - 100.0). */
  danceability: number
  /** Acousticness measure (0.0 - 100.0). */
  acousticness?: number
  /** Beats per minute tempo. */
  tempo?: number
  /** Loudness in decibels (dB). */
  loudness?: number
}

/**
 * Differences between seed track features and candidate track features.
 */
export interface FeatureDeltas {
  /** Difference in energy percentage points. */
  energy: number
  /** Difference in valence percentage points. */
  valence: number
  /** Difference in danceability percentage points. */
  danceability: number
}

/**
 * Unified representation of a track for UI rendering.
 */
export interface Track {
  /** Song title. */
  title: string
  /** Artist or band name. */
  artist: string
  /** Short monogram or artwork code. */
  art: string
  /** CSS class determining stylized visual appearance. */
  artClass: string
  /** Normalized energy percentage (0 - 100). */
  energy: number
  /** Normalized valence percentage (0 - 100). */
  valence: number
  /** Normalized danceability percentage (0 - 100). */
  dance: number
  /** Cosine similarity match score (0 - 100%). */
  match: number
  /** Unique Spotify track identifier. */
  spotifyId?: string
  /** Assigned KMeans cluster identifier. */
  clusterId?: number
  /** Descriptive name of the assigned vibe cluster. */
  clusterName?: string
  /** Feature deltas relative to the active seed track. */
  deltas?: FeatureDeltas
}

/**
 * Metric progress bar data structure.
 */
export interface MetricData {
  /** Metric abbreviation or label (e.g. 'ENG', 'VAL', 'DANCE'). */
  label: string
  /** Value percentage (0 - 100). */
  value: number
}

/**
 * Autocomplete search result item from the FastAPI backend.
 */
export interface SearchResultItem {
  /** Spotify track ID. */
  track_id: string
  /** Track title. */
  track_name: string
  /** Artist name(s). */
  artists: string
  /** Album name. */
  album_name: string
  /** Spotify popularity score (0 - 100). */
  popularity: number
}

/**
 * Autocomplete search response envelope.
 */
export interface SearchResponse {
  /** The sanitized search query. */
  query: string
  /** Number of results returned. */
  count: number
  /** Matching track candidate list. */
  results: SearchResultItem[]
}

/**
 * Seed track object returned from backend recommendation endpoints.
 */
export interface SeedTrackResponse {
  /** Name of the seed track. */
  track_name: string
  /** Artist of the seed track. */
  artist: string
  /** Unique Spotify track ID. */
  spotify_id: string
  /** Assigned KMeans cluster ID. */
  cluster_id: number
  /** Raw and scaled audio features. */
  raw_features: TrackFeatures
}

/**
 * Vibe cluster descriptor.
 */
export interface ClusterInfo {
  /** Integer ID of the cluster (0 - 7). */
  cluster_id: number
  /** Descriptive vibe label (e.g. 'Late Night Melancholic'). */
  cluster_name: string
}

/**
 * Candidate track recommendation returned by the backend engine.
 */
export interface RecommendedTrackResponse {
  /** Name of the recommended track. */
  track_name: string
  /** Artist name. */
  artist: string
  /** Spotify track ID. */
  spotify_id: string
  /** Computed cosine similarity match percentage. */
  match_percentage: number
  /** Cluster ID of the recommendation. */
  cluster_id: number
  /** Cluster name of the recommendation. */
  cluster_name: string
  /** Normalized feature levels. */
  features: TrackFeatures
  /** Feature differences relative to seed track. */
  deltas: FeatureDeltas
}

/**
 * Complete recommendation response payload from the FastAPI backend.
 */
export interface RecommendResponse {
  /** Information regarding the active seed track or mood archetype. */
  seed_track: SeedTrackResponse
  /** Cluster information for the seed track. */
  cluster_info: ClusterInfo
  /** List of top candidate recommendations. */
  recommendations: RecommendedTrackResponse[]
}
