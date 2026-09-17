'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { AlertCircle, ArrowUpRight, Loader2, X } from 'lucide-react'
import {
  ClusterInfo,
  Mood,
  RecommendedTrackResponse,
  SearchResultItem,
  SeedTrackResponse,
  Track,
} from '@/types/music'
import { MOODS, MOCK_TRACKS, SEED_TRACK } from '@/data/mock-tracks'
import {
  ApiError,
  checkBackendHealth,
  recommendByMood,
  recommendByTrack,
  searchTracks,
} from '@/lib/api'
import { Header } from '@/components/features/header'
import { Hero } from '@/components/features/hero'
import { AlbumArt } from '@/components/features/album-art'
import { Waveform } from '@/components/features/waveform'
import { TrackCard } from '@/components/features/track-card'
import { AlgorithmPanel } from '@/components/features/algorithm-panel'

/**
 * Helper to transform backend RecommendedTrackResponse objects into UI Track models.
 *
 * @param rec Candidate track from backend response.
 * @returns Formatted Track object ready for UI rendering.
 */
function mapBackendRecToUiTrack(rec: RecommendedTrackResponse): Track {
  const monogram = rec.track_name
    .split(' ')
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return {
    title: rec.track_name,
    artist: rec.artist,
    art: monogram || 'VN',
    artClass: 'art-generic',
    energy: rec.features.energy,
    valence: rec.features.valence,
    dance: rec.features.danceability,
    match: rec.match_percentage,
    spotifyId: rec.spotify_id,
    clusterId: rec.cluster_id,
    clusterName: rec.cluster_name,
    deltas: rec.deltas,
  }
}

/**
 * Helper to transform backend SeedTrackResponse into UI Track model for the seed card.
 *
 * @param seed Seed track response from backend.
 * @returns Formatted Track object representing the seed track.
 */
function mapBackendSeedToUiTrack(seed: SeedTrackResponse): Track {
  const monogram = seed.track_name
    .split(' ')
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return {
    title: seed.track_name,
    artist: seed.artist,
    art: monogram || 'VN',
    artClass: 'art-fishes',
    energy: seed.raw_features.energy,
    valence: seed.raw_features.valence,
    dance: seed.raw_features.danceability,
    match: 100,
    spotifyId: seed.spotify_id,
    clusterId: seed.cluster_id,
  }
}

/**
 * Vibelnyc Main Application Page.
 * Orchestrates live FastAPI ML recommendation requests, autocomplete search,
 * mood archetype calibration, and fallback test fixtures.
 *
 * @returns JSX Element rendering the complete Vibelnyc interface.
 */
export default function Page() {
  const [mood, setMood] = useState<Mood>('MELANCHOLY')
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<SearchResultItem[]>([])
  const [seedTrack, setSeedTrack] = useState<Track>(SEED_TRACK)
  const [visibleTracks, setVisibleTracks] = useState<Track[]>(
    MOCK_TRACKS.MELANCHOLY
  )
  const [clusterInfo, setClusterInfo] = useState<ClusterInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(true)

  const searchDebounceRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * Loads recommendations based on a selected mood archetype.
   * Fetches from FastAPI and falls back to mock fixture on failure.
   */
  const loadMoodRecommendations = useCallback(
    async (selectedMood: Mood) => {
      setIsLoading(true)
      setErrorMessage(null)

      try {
        const response = await recommendByMood(selectedMood, 3)
        const uiTracks = response.recommendations.map(mapBackendRecToUiTrack)
        const uiSeed = mapBackendSeedToUiTrack(response.seed_track)

        setVisibleTracks(uiTracks)
        setSeedTrack(uiSeed)
        setClusterInfo(response.cluster_info)
        setIsBackendConnected(true)
      } catch (err) {
        setIsBackendConnected(false)
        setVisibleTracks(MOCK_TRACKS[selectedMood] || MOCK_TRACKS.MELANCHOLY)
        setClusterInfo(null)
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  // Cold-start initialization: check health and fetch initial mood recommendations
  useEffect(() => {
    async function init() {
      const healthy = await checkBackendHealth()
      setIsBackendConnected(healthy)
      if (healthy) {
        await loadMoodRecommendations('MELANCHOLY')
      }
    }
    init()
  }, [loadMoodRecommendations])

  // Autocomplete debounce effect
  useEffect(() => {
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current)
    }

    if (!query.trim()) {
      setSuggestions([])
      return
    }

    searchDebounceRef.current = setTimeout(async () => {
      try {
        const results = await searchTracks(query, 5)
        setSuggestions(results)
      } catch {
        setSuggestions([])
      }
    }, 250)

    return () => {
      if (searchDebounceRef.current) {
        clearTimeout(searchDebounceRef.current)
      }
    }
  }, [query])

  /**
   * Handles user submission of a search query for a specific seed track.
   */
  const handleSearchSubmit = async (
    trackName: string,
    artistName?: string
  ) => {
    setIsSearching(true)
    setErrorMessage(null)

    try {
      const response = await recommendByTrack(trackName, artistName, 3)
      const uiTracks = response.recommendations.map(mapBackendRecToUiTrack)
      const uiSeed = mapBackendSeedToUiTrack(response.seed_track)

      setVisibleTracks(uiTracks)
      setSeedTrack(uiSeed)
      setClusterInfo(response.cluster_info)
      setIsBackendConnected(true)
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setErrorMessage(
          `Track "${trackName}" was not found in the Spotify dataset. Try searching for tracks like "Creep", "Midnight City", "Intro", or "1901".`
        )
      } else if (err instanceof ApiError) {
        setErrorMessage(`Recommendation failed: ${err.detail}`)
      } else {
        setErrorMessage(
          'Could not reach the FastAPI recommendation engine at http://localhost:8000. Operating in offline demo mode.'
        )
        setIsBackendConnected(false)
      }
    } finally {
      setIsSearching(false)
    }
  }

  /**
   * Handles mood filter clicks.
   */
  const handleMoodSelect = (selectedMood: Mood) => {
    setMood(selectedMood)
    loadMoodRecommendations(selectedMood)
  }

  return (
    <main className="app-shell">
      <Header isBackendConnected={isBackendConnected} />

      <Hero
        query={query}
        onQueryChange={setQuery}
        onSearchSubmit={handleSearchSubmit}
        suggestions={suggestions}
        isSearching={isSearching}
        activeMood={mood}
        onSelectMood={handleMoodSelect}
        moods={MOODS}
      />

      {errorMessage && (
        <div
          role="alert"
          style={{
            backgroundColor: '#1f1315',
            border: '2px solid #ef4444',
            color: '#fca5a5',
            padding: '12px 16px',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={18} color="#ef4444" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            aria-label="Dismiss error"
            style={{
              background: 'none',
              border: 'none',
              color: '#fca5a5',
              cursor: 'pointer',
            }}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <section className="seed-card">
        <AlbumArt track={seedTrack} />
        <div className="seed-info">
          <span>SEED TRACK</span>
          <strong>
            {seedTrack.title} - {seedTrack.artist}
          </strong>
          {seedTrack.spotifyId && (
            <small
              style={{
                display: 'block',
                color: '#888',
                fontSize: '0.72rem',
                marginTop: '4px',
                fontFamily: 'monospace',
              }}
            >
              SPOTIFY ID: {seedTrack.spotifyId}
            </small>
          )}
        </div>
        <Waveform />
      </section>

      <div className="content-grid">
        <section className="recommendations">
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
            }}
          >
            <h2>RECOMMENDED</h2>
            {isLoading && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: '#ffdd00',
                  fontSize: '0.8rem',
                  fontFamily: 'monospace',
                }}
              >
                <Loader2 size={14} className="animate-spin" />
                <span>CALCULATING COSINE DISTANCE...</span>
              </div>
            )}
          </div>

          <div className="track-grid">
            {visibleTracks.map((track) => (
              <TrackCard
                track={track}
                key={`${track.artist}-${track.title}-${track.spotifyId || ''}`}
              />
            ))}
          </div>
        </section>

        <div id="algorithm">
          <AlgorithmPanel mood={mood} clusterInfo={clusterInfo} />
        </div>
      </div>

      <footer>
        VIBELNYC <span>SONIC MATCHING ENGINE / 2026</span>
        <ArrowUpRight size={15} />
      </footer>
    </main>
  )
}
