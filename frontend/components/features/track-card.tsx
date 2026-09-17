import { Pause, Play, SkipForward } from 'lucide-react'
import { Track } from '@/types/music'
import { AlbumArt } from './album-art'
import { Metric } from './metric'

/**
 * Props for the TrackCard component.
 */
interface TrackCardProps {
  /** The recommendation track object containing metadata, scores, and audio metrics. */
  track: Track
}

/**
 * Renders a Neo-Brutalist card for an individual recommended track,
 * displaying metadata, percentage match score, feature deltas, and playback controls.
 *
 * @param props Contains the track details to render.
 * @returns JSX Element representing the track recommendation card.
 */
export function TrackCard({ track }: TrackCardProps) {
  return (
    <article className="track-card">
      <div className="track-top">
        <AlbumArt track={track} small />
        <div className="track-meta">
          <h3>{track.title}</h3>
          <p>{track.artist}</p>
          <span className="match">{track.match}% MATCH</span>
          {track.clusterName && (
            <span
              style={{
                fontSize: '0.7rem',
                color: '#aaa',
                display: 'block',
                marginTop: '2px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {track.clusterName}
            </span>
          )}
        </div>
      </div>

      <div className="metrics">
        <Metric label="ENG" value={track.energy} />
        <Metric label="VAL" value={track.valence} />
        <Metric label="DANCE" value={track.dance} />
      </div>

      {track.deltas && (
        <div
          style={{
            display: 'flex',
            gap: '8px',
            fontSize: '0.68rem',
            color: '#888',
            padding: '2px 0 6px 0',
            fontFamily: 'monospace',
          }}
        >
          <span>
            dE:{' '}
            <strong
              style={{
                color: track.deltas.energy >= 0 ? '#10b981' : '#ef4444',
              }}
            >
              {track.deltas.energy >= 0 ? '+' : ''}
              {track.deltas.energy}%
            </strong>
          </span>
          <span>
            dV:{' '}
            <strong
              style={{
                color: track.deltas.valence >= 0 ? '#10b981' : '#ef4444',
              }}
            >
              {track.deltas.valence >= 0 ? '+' : ''}
              {track.deltas.valence}%
            </strong>
          </span>
          <span>
            dD:{' '}
            <strong
              style={{
                color: track.deltas.danceability >= 0 ? '#10b981' : '#ef4444',
              }}
            >
              {track.deltas.danceability >= 0 ? '+' : ''}
              {track.deltas.danceability}%
            </strong>
          </span>
        </div>
      )}

      <div className="track-actions">
        <div className="icon-actions">
          <button type="button" aria-label="Play track">
            <Play size={16} fill="currentColor" />
          </button>
          <button type="button" aria-label="Pause track">
            <Pause size={16} />
          </button>
          <button type="button" aria-label="Skip track">
            <SkipForward size={16} fill="currentColor" />
          </button>
        </div>
        <button type="button" className="play-link">
          + PLAY
        </button>
      </div>
    </article>
  )
}
