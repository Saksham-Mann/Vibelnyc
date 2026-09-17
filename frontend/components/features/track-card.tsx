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
 * Renders a Neo-Brutalist card for an individual recommended track.
 * Integrates an official Spotify mini-player iframe embed with graceful fallback
 * and an external "+ ADD" action link directing to the track on Spotify.
 *
 * @param props Component properties containing the track details to render.
 * @returns JSX Element representing the track recommendation card.
 */
export function TrackCard({ track }: TrackCardProps) {
  const spotifyId =
    track.spotifyId && track.spotifyId.trim().length > 0
      ? track.spotifyId.trim()
      : null

  const spotifyTrackUrl = spotifyId
    ? `https://open.spotify.com/track/${spotifyId}`
    : `https://open.spotify.com/search/${encodeURIComponent(
        `${track.title} ${track.artist}`
      )}`

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
                color: '#77736b',
                display: 'block',
                marginTop: '2px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 700,
              }}
            >
              {track.clusterName}
            </span>
          )}
        </div>
      </div>

      {spotifyId ? (
        <div className="spotify-embed-container">
          <iframe
            src={`https://open.spotify.com/embed/track/${spotifyId}?utm_source=generator&theme=0`}
            width="100%"
            height="80"
            frameBorder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy"
            style={{ display: 'block', border: 0 }}
            title={`Spotify preview for ${track.title} by ${track.artist}`}
          />
        </div>
      ) : (
        <div
          className="spotify-embed-fallback"
          aria-label="Audio preview unavailable"
        >
          [ AUDIO PREVIEW UNAVAILABLE ]
        </div>
      )}

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
            color: '#77736b',
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
        <a
          href={spotifyTrackUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="add-track-link"
          aria-label={`Add ${track.title} by ${track.artist} on Spotify`}
        >
          + ADD
        </a>
      </div>
    </article>
  )
}
