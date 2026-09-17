import { Pause, Play, SkipForward } from 'lucide-react'
import { Track } from '@/types/music'
import { AlbumArt } from './album-art'
import { Metric } from './metric'

interface TrackCardProps {
  track: Track
}

export function TrackCard({ track }: TrackCardProps) {
  return (
    <article className="track-card">
      <div className="track-top">
        <AlbumArt track={track} small />
        <div className="track-meta">
          <h3>{track.title}</h3>
          <p>{track.artist}</p>
          <span className="match">{track.match}% MATCH</span>
        </div>
      </div>

      <div className="metrics">
        <Metric label="ENG" value={track.energy} />
        <Metric label="VAL" value={track.valence} />
        <Metric label="DANCE" value={track.dance} />
      </div>

      <div className="track-actions">
        <div className="icon-actions">
          <button aria-label="Play">
            <Play size={16} fill="currentColor" />
          </button>
          <button aria-label="Pause">
            <Pause size={16} />
          </button>
          <button aria-label="Skip">
            <SkipForward size={16} fill="currentColor" />
          </button>
        </div>
        <button className="play-link">+ PLAY</button>
      </div>
    </article>
  )
}
